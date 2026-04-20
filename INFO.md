# INFO — Architecture & Design Documentation

Comprehensive **High-Level Design (HLD)** and **Low-Level Design (LLD)** for the LangGraph Multi-Agent System.

---

## Table of Contents
- [1. System Overview (HLD)](#1-system-overview-hld)
- [2. Architecture Diagram](#2-architecture-diagram)
- [3. Container Infrastructure](#3-container-infrastructure)
- [4. Agent Design (LLD)](#4-agent-design-lld)
- [5. LangGraph State Machine (LLD)](#5-langgraph-state-machine-lld)
- [6. Self-Correction Retry Loop](#6-self-correction-retry-loop)
- [7. Service Layer (LLD)](#7-service-layer-lld)
- [8. Prompt Engineering](#8-prompt-engineering)
- [9. API Layer](#9-api-layer)
- [10. Data Model](#10-data-model)
- [11. File Reference](#11-file-reference)

---

## 1. System Overview (HLD)

The system is a **multi-agent AI orchestrator** that:

1. Receives a natural language query from the user.
2. Refines the query using an LLM for precision.
3. Classifies the intent (code, web, db, latex) using a router.
4. Dispatches to a specialized agent.
5. Executes the agent's output in an **isolated sandbox** (Piston for code, TeXLive for LaTeX, PostgreSQL for SQL).
6. If execution fails, triggers a **self-correction retry loop** (up to 2 retries).
7. Returns a formatted response with execution results.

### Design Principles
| Principle | Implementation |
|---|---|
| **Separation of Concerns** | Each agent is a self-contained class with its own service dependency |
| **Sandbox Isolation** | Code and LaTeX run in dedicated Docker containers, never on the host |
| **Autonomous Recovery** | Runtime errors trigger automated retry with error feedback to LLM |
| **Stateless API** | Each query is a fresh graph invocation; no session state persisted |
| **Prompt-Driven Behavior** | All agent behavior is controlled via external `.txt` prompt templates |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER QUERY                                   │
│                   "Write Python to sort a list"                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ai-code-api (FastAPI)                              │
│                    Port: 8001 → 8000                                 │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    LangGraph State Machine                      │ │
│  │                                                                 │ │
│  │  ┌─────┐    ┌────────┐    ┌────────┐                           │ │
│  │  │START │───▶│  LLM   │───▶│ Router │                           │ │
│  │  └─────┘    │ (Refine)│    │(Intent)│                           │ │
│  │             └────────┘    └───┬────┘                            │ │
│  │                    ┌──────────┼──────────┬──────────┐           │ │
│  │                    ▼          ▼          ▼          ▼           │ │
│  │               ┌──────┐  ┌──────┐  ┌──────┐  ┌───────┐         │ │
│  │               │ Code │  │ Web  │  │  DB  │  │ LaTeX │         │ │
│  │               │Agent │  │Agent │  │Agent │  │ Agent │         │ │
│  │               └──┬───┘  └──┬───┘  └──┬───┘  └──┬────┘         │ │
│  │                  │         │         │         │               │ │
│  │                  ▼         │         │         ▼               │ │
│  │            ┌──────────┐    │         │   ┌──────────┐          │ │
│  │            │should_   │    │         │   │should_   │          │ │
│  │            │retry?    │    │         │   │retry?    │          │ │
│  │            └─┬────┬───┘    │         │   └─┬────┬───┘          │ │
│  │         retry│    │cont.   │         │retry│    │cont.         │ │
│  │              ▼    │        │         │     ▼    │              │ │
│  │         ┌────────┐│        │         │┌────────┐│              │ │
│  │         │ Refine ││        │         ││ Refine ││              │ │
│  │         │ Node   ││        │         ││ Node   ││              │ │
│  │         └───┬────┘│        │         │└───┬────┘│              │ │
│  │             │     │        │         │    │     │              │ │
│  │             ▼     │        │         │    ▼     │              │ │
│  │          (back    │        │         │ (back    │              │ │
│  │          to LLM)  │        │         │ to LLM)  │              │ │
│  │                   ▼        ▼         ▼          ▼              │ │
│  │                 ┌──────────────────────────┐                   │ │
│  │                 │       Final Node         │                   │ │
│  │                 │  (Format + Append Output) │                   │ │
│  │                 └────────────┬─────────────┘                   │ │
│  │                              ▼                                 │ │
│  │                 ┌──────────────────────────┐                   │ │
│  │                 │      Cleanup Node        │                   │ │
│  │                 │  (Trim message history)  │                   │ │
│  │                 └────────────┬─────────────┘                   │ │
│  │                              ▼                                 │ │
│  │                           [END]                                │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────┬──────────────────┬──────────────────┬────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌───────────────┐ ┌─────────────────┐
│  piston-engine   │ │ latex-checker  │ │  demo-postgres   │
│  (Code Sandbox)  │ │ (TeXLive)     │ │  (PostgreSQL)    │
│  Port: 2000      │ │ Port: 3000    │ │  Port: 5433      │
│                  │ │ (internal)    │ │                   │
│  Supports:       │ │               │ │  Tables:          │
│  Python, JS, Go, │ │ Compiles .tex │ │  users, products, │
│  PHP, Clojure... │ │ to .pdf       │ │  orders           │
└──────────────────┘ └───────────────┘ └─────────────────┘
```

---

## 3. Container Infrastructure

Defined in `docker-compose.yml` (4 services):

### 3.1 ai-code-api
- **Image**: `python:3.11-slim` + custom `Dockerfile`
- **Role**: Hosts the FastAPI server and the LangGraph state machine
- **Memory**: Capped at 512MB
- **Volumes**: `./src` and `./scripts` are hot-mounted for live reloading
- **Dependencies**: Waits for `piston-engine` and `latex-checker`

### 3.2 piston-engine
- **Image**: `ghcr.io/engineer-man/piston`
- **Role**: Isolated code execution sandbox
- **Capabilities**: Runs arbitrary code in 50+ languages
- **Privilege**: `privileged: true` (required for container-in-container execution)
- **Persistence**: `./piston/packages` stores downloaded runtimes between restarts

### 3.3 latex-checker
- **Image**: `texlive/texlive:latest-medium`
- **Role**: LaTeX compilation sandbox
- **Server**: Runs a custom HTTP server (`latex_server.py`) on port 3000
- **Process**: Receives LaTeX code → writes to temp file → runs `pdflatex` → returns result JSON
- **Persistence**: `./latex_outputs/` stores generated PDFs on the host

### 3.4 demo-postgres
- **Image**: `postgres:15-alpine`
- **Role**: Demo relational database for the DB Agent
- **Seed Data**: `scripts/init-db.sql` auto-executes on first boot
- **Credentials**: `user:password@demo_db`

---

## 4. Agent Design (LLD)

All agents extend `BaseAgent` (abstract class):

```python
class BaseAgent(ABC):
    def __init__(self, llm_service):
        self.llm = llm_service

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
```

### 4.1 CodeAgent (`src/agents/code_agent.py`)

| Step | Action |
|---|---|
| 1 | Reads refined query from state |
| 2 | Loads `code_prompt.txt` template |
| 3 | Invokes LLM to generate code |
| 4 | Extracts language + code from LLM response using `extract_code_and_lang()` |
| 5 | Calls `PistonService.execute(lang, code)` |
| 6 | Returns `final_answer`, `execution_result`, `agent_used` |

**Key Feature — Autonomous Runtime Management:**
If the identified language (e.g. `clojure`, `php`) is not installed in Piston, the `PistonService` automatically:
1. Queries installed runtimes via `GET /api/v2/runtimes`
2. If missing, installs via `POST /api/v2/packages` (up to 300s timeout)
3. Then executes the code

### 4.2 LatexAgent (`src/agents/latex_agent.py`)

| Step | Action |
|---|---|
| 1 | Reads refined query from state |
| 2 | Loads `latex_prompt.txt` template |
| 3 | Invokes LLM to generate LaTeX code |
| 4 | Extracts code from markdown code blocks |
| 5 | Calls `LatexService.compile(code)` → sends to `latex-checker` container |
| 6 | Returns `final_answer`, `execution_result`, `agent_used` |

**Compilation Pipeline (inside `latex-checker`):**
```
LaTeX code → temp .tex file → pdflatex -halt-on-error → PDF → /latex_outputs/
```

### 4.3 WebAgent (`src/agents/web_agent.py`)

| Step | Action |
|---|---|
| 1 | Searches using `WebService` (Wikipedia + Google) |
| 2 | Sends search results to LLM with `web_prompt.txt` |
| 3 | Returns LLM-generated summary |

### 4.4 DBAgent (`src/agents/db_agent.py`)

| Step | Action |
|---|---|
| 1 | Converts natural language to SQL using LLM + `db_prompt.txt` |
| 2 | Cleans SQL with `clean_sql()` parser |
| 3 | Executes on `demo_postgres` via `psycopg2` |
| 4 | Sends raw results back to LLM for natural language explanation |
| 5 | Returns `final_answer`, `sql`, `data`, `agent_used` |

---

## 5. LangGraph State Machine (LLD)

### 5.1 State Schema (`src/graph/state.py`)

```python
class AgentState(TypedDict, total=False):
    # Core
    user_query: str                            # Original user input
    intent: str                                # Classified intent (code/web/db/latex)

    # Conversation
    messages: Annotated[List[Any], operator.add]  # Append-only message history

    # Tool / agent flow
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Any

    # Control
    refined_query: str                         # LLM-refined version of user query
    intermediate_steps: List[str]              # Audit trail of processing steps

    # Output
    final_answer: str                          # LLM-generated response text
    response: str                              # Final formatted output

    # Execution Metadata
    execution_result: Any                      # Raw sandbox result (Piston/LaTeX)
    agent_used: str                            # Which agent handled the query
    retry_count: int                           # Number of retry attempts (max 2)
    errors: List[str]                          # Accumulated error messages
    sql: str                                   # Executed SQL (DB agent only)
    data: Any                                  # Raw DB result (DB agent only)
```

### 5.2 Graph Construction (`src/graph/builder.py`)

The graph is built using LangGraph's `StateGraph`:

```
Nodes: llm → router → [code | web | db | latex] → final → cleanup
                                 ↑         ↓
                                 └─ refine ←┘  (on failure)
```

**Node Definitions:**

| Node | Function | Purpose |
|---|---|---|
| `llm` | `llm_node()` | Refines user query for precision |
| `router` | `router_node()` | Classifies intent using LLM |
| `code` | `CodeAgent.run()` | Generates + executes code |
| `web` | `WebAgent.run()` | Searches web + summarizes |
| `db` | `DBAgent.run()` | NL→SQL + execution + explanation |
| `latex` | `LatexAgent.run()` | Generates + compiles LaTeX |
| `refine` | `refine_node()` | Injects error feedback into query |
| `final` | `final_node()` | Formats output with sandbox results |
| `cleanup` | `cleanup_node()` | Trims message history to last 8 |

**Edge Definitions:**

| From | To | Type | Condition |
|---|---|---|---|
| `START` | `llm` | Direct | Always |
| `llm` | `router` | Direct | Always |
| `router` | `code/web/db/latex` | Conditional | Based on `route_by_intent()` |
| `code` | `final` or `refine` | Conditional | `should_retry()` checks for errors |
| `latex` | `final` or `refine` | Conditional | `should_retry()` checks for errors |
| `web` | `final` | Direct | Always (no retry for web) |
| `db` | `final` | Direct | Always (no retry for db) |
| `refine` | `llm` | Direct | Loops back for another attempt |
| `final` | `cleanup` | Direct | Always |
| `cleanup` | `END` | Direct | Always |

---

## 6. Self-Correction Retry Loop

The retry mechanism is a **closed-loop feedback system** that operates on `code` and `latex` agents.

### Flow

```
Agent executes → should_retry() checks result
     │                    │
     │  (success)         │  (failure + retry_count < 2)
     ▼                    ▼
  final_node         refine_node
                         │
                         │  Injects error message into refined_query
                         ▼
                      llm_node (skips re-refinement, keeps error context)
                         │
                         ▼
                     router_node → re-routes to same agent
                         │
                         ▼
                     Agent re-executes with corrected code
```

### `should_retry()` Logic (`src/graph/edges/retry.py`)

```python
def should_retry(state) -> "retry" | "continue":
    # For latex_agent: checks if pdf_filename is missing or "error" key exists
    # For code_agent: checks stderr or "error" key in execution result
    # Returns "retry" if has_error AND retry_count < 2
    # Returns "continue" otherwise
```

### `refine_node()` Logic (`src/graph/nodes/refine.py`)

Constructs a new `refined_query` containing:
```
"The previous attempt failed with the following error:
{error_message}

Please fix the issue and provide a corrected version. Query: {original_query}"
```

This ensures the LLM receives the **exact compilation/execution error** and can fix it (e.g., removing `\includegraphics` for missing files, fixing syntax errors, adding missing packages).

---

## 7. Service Layer (LLD)

### 7.1 LLMService (`src/services/llm_service.py`)
- **Provider**: Groq Cloud
- **Model**: `llama-3.3-70b-versatile`
- **Temperature**: `0` (deterministic)
- **Auth**: Reads `GROQ_API_KEY` from environment
- **Methods**: `invoke(prompt) → str`, `stream(prompt) → generator`

### 7.2 PistonService (`src/services/piston_service.py`)
- **Endpoint**: `http://piston_engine:2000`
- **API**: Piston v2 REST API
- **Auto-Install**: Checks runtimes before execution, installs if missing (300s timeout)
- **Execution Timeout**: 30s per code run
- **Method**: `execute(language, code) → dict`

### 7.3 LatexService (`src/services/latex_service.py`)
- **Endpoint**: `http://latex-checker:3000`
- **Protocol**: HTTP POST with `{"code": "<latex>"}` JSON
- **Response**: `{"exit_code", "stdout", "stderr", "pdf_filename"}`
- **Timeout**: 30s
- **Method**: `compile(code) → dict`

### 7.4 WebService (`src/services/web_service.py`)
- **Sources**: Wikipedia (primary) + Google Search (secondary)
- **Wikipedia**: Returns 3-sentence summary
- **Google**: Returns top 5 URLs
- **Method**: `search(query) → list[dict]`

### 7.5 DBService (`src/services/db_service.py`)
- **Driver**: `psycopg2` with `RealDictCursor`
- **DSN**: `postgresql://user:password@demo_postgres:5432/demo_db`
- **Method**: `execute(query) → list[dict] | {"status": "ok"} | {"error": str}`

---

## 8. Prompt Engineering

All prompts are stored as external `.txt` files in `src/prompts/` and loaded dynamically. This allows editing prompts without code changes (hot-mounted volume).

| File | Purpose | Key Rules |
|---|---|---|
| `router_prompt.txt` | Intent classification | Must return exactly one of: `code`, `web`, `db`, `latex` |
| `code_prompt.txt` | Code generation | Senior engineer persona; produces clean, documented code |
| `latex_prompt.txt` | LaTeX generation | Forbids `\includegraphics`, `braket`/`physics` packages; uses standard `amsmath` |
| `web_prompt.txt` | Search summarization | Synthesizes Wikipedia + Google results |
| `db_prompt.txt` | NL-to-SQL | Schema-aware; generates PostgreSQL-compatible queries |

### Template Variable Escaping
All prompts use Python `str.format()`. LaTeX braces must be double-escaped:
```
\end{{document}}  ← correct (produces \end{document})
\end{document}   ← CRASHES with KeyError
```

---

## 9. API Layer

### 9.1 FastAPI Application (`src/api/main.py`)

Single-file app that mounts the agent router:
```python
app = FastAPI()
app.include_router(agent_router, prefix="/agent")
```

### 9.2 System Bootstrap (`src/api/routes/agent.py`)

Uses a **singleton pattern** — services and agents are instantiated once at module load:

```python
def create_system():
    llm = LLMService()
    piston_service = PistonService()
    latex_service = LatexService()
    web_service = WebService()
    db_service = DBService(dsn="postgresql://user:password@demo_postgres:5432/demo_db")

    agents = {
        "code": CodeAgent(llm, piston_service),
        "web": WebAgent(llm, web_service),
        "db": DBAgent(llm, db_service),
        "latex": LatexAgent(llm, latex_service),
    }
    return build_graph(llm, agents)

graph = create_system()  # singleton
```

### 9.3 Endpoint

```
POST /agent/run
Body: {"query": "your natural language query"}
Response: {"query": "...", "response": "..."}
```

---

## 10. Data Model

### 10.1 Demo Database (PostgreSQL)

Seeded by `scripts/init-db.sql`:

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),
    category VARCHAR(50),
    stock_quantity INT
);

-- Orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total_price DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data:**
| Table | Records |
|---|---|
| `users` | Alice Johnson (28), Bob Smith (34), Charlie Brown (22), Diana Prince (30) |
| `products` | Laptop ($1200), Smartphone ($800), Coffee Maker ($50), Desk Chair ($150), Backpack ($40) |
| `orders` | Alice: $1250 shipped + $40 pending; Bob: $800 processing; Charlie: $50 delivered |

---

## 11. File Reference

### Source Tree

```
src/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── base_agent.py           # Abstract base class for all agents
│   ├── code_agent.py           # Code generation + Piston execution
│   ├── db_agent.py             # NL→SQL + PostgreSQL execution
│   ├── latex_agent.py          # LaTeX generation + TeXLive compilation
│   └── web_agent.py            # Wikipedia + Google search + summarization
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   └── agent.py            # POST /agent/run endpoint + system bootstrap
│   └── schemas/
│       ├── __init__.py
│       └── request.py          # Pydantic request model
├── graph/
│   ├── __init__.py
│   ├── builder.py              # LangGraph StateGraph construction
│   ├── state.py                # AgentState TypedDict definition
│   ├── edges/
│   │   ├── __init__.py
│   │   ├── retry.py            # should_retry() conditional edge
│   │   └── routing.py          # route_by_intent() conditional edge
│   └── nodes/
│       ├── __init__.py
│       ├── cleanup.py          # Message history trimming
│       ├── final.py            # Output formatting + sandbox result display
│       ├── llm.py              # Query refinement node
│       ├── refine.py           # Error feedback injection for retry loop
│       ├── router.py           # Intent classification node
│       └── tool_executor.py    # Generic tool execution (unused currently)
├── latex_server.py             # HTTP server for LaTeX compilation (runs in latex-checker)
├── prompts/
│   ├── code_prompt.txt         # Code generation prompt
│   ├── db_prompt.txt           # NL-to-SQL prompt
│   ├── latex_prompt.txt        # LaTeX generation prompt (no images, no braket)
│   ├── router_prompt.txt       # Intent classification prompt
│   └── web_prompt.txt          # Web search summarization prompt
└── services/
    ├── __init__.py
    ├── db_service.py           # PostgreSQL client (psycopg2)
    ├── latex_service.py        # LaTeX compilation HTTP client
    ├── llm_service.py          # Groq LLM client (langchain-groq)
    ├── piston_service.py       # Piston sandbox client with auto-install
    └── web_service.py          # Wikipedia + Google Search client
```

### Dependencies (`requirements.txt`)

| Package | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `langchain` / `langchain-groq` | LLM orchestration |
| `langgraph` | State machine graph engine |
| `httpx` | HTTP client for Piston/LaTeX services |
| `psycopg2-binary` | PostgreSQL driver |
| `wikipedia` | Wikipedia API client |
| `googlesearch-python` | Google Search scraper |
| `python-dotenv` | Environment variable loading |

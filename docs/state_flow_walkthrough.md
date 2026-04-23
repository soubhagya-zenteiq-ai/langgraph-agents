# 🧠 LangGraph Agent — State Flow Walkthrough

This document explains how the `AgentState` dictionary evolves as it travels through each node in the LangGraph graph, using a concrete example for all four agent types.

---

## 📦 The `AgentState` Schema

```python
class AgentState(TypedDict, total=False):
    # Core
    user_query: str          # The original input from the user
    intent: str              # Classified intent: code | web | db | latex

    # Conversation history (auto-accumulates via operator.add)
    messages: Annotated[List[Any], operator.add]

    # Tool flow
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Any

    # Control
    refined_query: str       # Query rewritten by LLM for better results
    intermediate_steps: List[str]

    # Output
    final_answer: str        # Agent's generated answer
    response: str            # Final formatted string shown to user

    # Metadata
    execution_result: Union[ExecutionResult, DBResponse, WebSearchResponse, Any]
    agent_used: str          # Which agent handled the query
    retry_count: int         # Used by code/latex retry loop
    errors: List[str]
    sql: str                 # Only set by DB agent
    data: Any                # Only set by DB agent
    metadata: Dict[str, Any]
```

> **Key Rule**: LangGraph only **merges** the dict returned by each node into the current state. Fields not returned by a node remain **unchanged**.

---

## 🗺️ Graph Execution Order

```
START
  │
  ▼
[llm] ──→ [router] ──→ (route_by_intent)
                              │
              ┌───────────────┼────────────────┬──────────┐
              ▼               ▼                ▼          ▼
           [web]           [code]            [db]      [latex]
              │               │                │          │
              │         (should_retry?)        │    (should_retry?)
              │          ┌───┴────┐            │     ┌────┴────┐
              │        retry   continue        │   retry    continue
              │          │        │            │     │         │
              │        [refine]   │            │  [refine]    │
              │          │        │            │     │         │
              │          └──→[llm]             │     └──→[llm] │
              │                               │               │
              └───────────────────────────────┴───────────────┘
                                              │
                                           [final]
                                              │
                                          [cleanup]
                                              │
                                            END
```

---

## 🔁 Example 1: Web Query — "What are the latest breakthroughs in quantum computing?"

### 🟢 Initial State (at `START`)

```python
{
    "user_query": "What are the latest breakthroughs in quantum computing?",
    "messages": []
    # all other fields → None / unset
}
```

---

### Node 1 → `llm` (`src/graph/nodes/llm.py`)

**What happens**: Sends the `user_query` to the LLM to rewrite it for better search precision.

**Prompt sent to LLM**:
```
Rewrite the following user query to be more precise for a search engine or database.
Return ONLY the refined query string. No explanations, no lists.

Original Query: What are the latest breakthroughs in quantum computing?
```

**LLM returns**: `"Quantum computing breakthroughs 2024-2025 milestones research"`

**State update returned by node**:
```python
{
    "refined_query": "Quantum computing breakthroughs 2024-2025 milestones research"
}
```

**Full cumulative state**:
```python
{
    "user_query":     "What are the latest breakthroughs in quantum computing?",
    "messages":       [],
    "refined_query":  "Quantum computing breakthroughs 2024-2025 milestones research"
}
```

---

### Node 2 → `router` (`src/graph/nodes/router.py`)

**What happens**: Uses `router_prompt.txt` to classify the intent.

**Prompt sent to LLM**:
```
You are an intent classification engine.
Classify the user query into EXACTLY one of: code | web | db | latex

Query: Quantum computing breakthroughs 2024-2025 milestones research
```

**LLM returns**: `"web"`

**State update returned by node**:
```python
{
    "intent": "web"
}
```

**Full cumulative state**:
```python
{
    "user_query":    "What are the latest breakthroughs in quantum computing?",
    "messages":      [],
    "refined_query": "Quantum computing breakthroughs 2024-2025 milestones research",
    "intent":        "web"
}
```

---

### Conditional Edge → `route_by_intent`

```python
intent = state["intent"]  # "web"
# → routes to "web" node
```

---

### Node 3 → `web` (`src/agents/web_agent.py`)

**What happens**:
1. Calls `web_service.search(refined_query)` → gets raw search results
2. Sends results + query to LLM via `web_prompt.txt` → gets summarized answer

**Internal search results** (raw data from `WebService`):
```python
[
    {"title": "Google's Willow chip achieves quantum error correction", "snippet": "..."},
    {"title": "IBM Quantum Heron processor breaks 1000 qubit barrier",  "snippet": "..."},
    {"title": "Microsoft topological qubit research 2025",              "snippet": "..."}
]
```

**Prompt sent to LLM**:
```
You are a web research assistant.
Based on these search results: [...]
Answer the user's question: "Quantum computing breakthroughs 2024-2025..."
```

**LLM returns**: `"In 2024-2025, major breakthroughs include Google's Willow chip..."`

**State update returned by node**:
```python
{
    "final_answer":     "In 2024-2025, major breakthroughs include Google's Willow chip...",
    "agent_used":       "web_agent",
    "execution_result": [WebSearchResponse(...)]
}
```

**Full cumulative state**:
```python
{
    "user_query":       "What are the latest breakthroughs in quantum computing?",
    "messages":         [],
    "refined_query":    "Quantum computing breakthroughs 2024-2025 milestones research",
    "intent":           "web",
    "agent_used":       "web_agent",
    "execution_result": [WebSearchResponse(...)],
    "final_answer":     "In 2024-2025, major breakthroughs include Google's Willow chip..."
}
```

---

### Node 4 → `final` (`src/graph/nodes/final.py`)

**What happens**: Formats the `final_answer` into a clean `response` string. For `web_agent`, no sandbox output or SQL is appended.

**State update returned by node**:
```python
{
    "response": "In 2024-2025, major breakthroughs include Google's Willow chip..."
}
```

---

### Node 5 → `cleanup` (`src/graph/nodes/cleanup.py`)

**What happens**: Trims `messages` to the last 8 items to avoid token overflow.

**State update returned by node**:
```python
{
    "messages": []   # was already empty; trimmed to [-8:]
}
```

---

### 🏁 Final State (at `END`)

```python
{
    "user_query":       "What are the latest breakthroughs in quantum computing?",
    "messages":         [],
    "refined_query":    "Quantum computing breakthroughs 2024-2025 milestones research",
    "intent":           "web",
    "agent_used":       "web_agent",
    "execution_result": [WebSearchResponse(...)],
    "final_answer":     "In 2024-2025, major breakthroughs include Google's Willow chip...",
    "response":         "In 2024-2025, major breakthroughs include Google's Willow chip..."
}
```

---

## 💻 Example 2: Code Query — "Write a Python function to find prime numbers"

### Changes vs Example 1

| Node | Key Difference |
|:-----|:--------------|
| `llm` | Refines to: `"Python function Sieve of Eratosthenes prime numbers"` |
| `router` | Returns `intent = "code"` |
| `code` | Calls Piston sandbox to **execute** the generated code |
| `final` | Appends `✅ SANDBOX EXECUTION` block with stdout |
| Retry? | If Piston returns error, `should_retry` → `"refine"` → back to `llm` |

**State after `code` node**:
```python
{
    ...
    "intent":           "code",
    "final_answer":     "Here is a Python function using the Sieve...\n```python\ndef sieve(n): ...```",
    "execution_result": ExecutionResult(success=True, stdout="[2, 3, 5, 7, 11]", stderr=""),
    "agent_used":       "code_agent",
    "metadata":         {"language": "python"},
    "retry_count":      0
}
```

**State after `final` node**:
```python
{
    ...
    "response": "Here is a Python function using the Sieve...\n\n--- 🖥️ SANDBOX EXECUTION ✅ ---\n[2, 3, 5, 7, 11]\n---"
}
```

---

## 🗄️ Example 3: Database Query — "Get all users older than 25"

| Node | Key Difference |
|:-----|:--------------|
| `router` | Returns `intent = "db"` |
| `db` | Generates SQL from LLM, runs it against PostgreSQL, returns raw results |
| `final` | Appends `🗄️ DATABASE METADATA` block with SQL + raw data |

**State after `db` node**:
```python
{
    ...
    "intent":           "db",
    "sql":              "SELECT * FROM users WHERE age > 25;",
    "data":             DBResponse(status="success", data=[{"id":1, "name":"Alice", "age":30}]),
    "final_answer":     "Found 1 users older than 25: Alice (age 30).",
    "agent_used":       "db_agent"
}
```

**State after `final` node**:
```python
{
    "response": "Found 1 users older than 25...\n\n--- 🗄️ DATABASE METADATA ---\nSQL Executed:\n```sql\nSELECT * FROM users WHERE age > 25;\n```\nRaw Data:\n[{'id': 1, 'name': 'Alice', 'age': 30}]\n---"
}
```

---

## 📄 Example 4: LaTeX Query — "Generate a LaTeX report on Fourier Transform"

| Node | Key Difference |
|:-----|:--------------|
| `router` | Returns `intent = "latex"` |
| `latex` | LLM generates `.tex` source, Piston compiles it, checks for PDF |
| `final` | Appends `📄 LATEX COMPILATION SUCCESS` or failure logs |
| Retry? | Same retry loop as `code` — `should_retry` can send back to `refine` → `llm` |

**State after `latex` node** (success case):
```python
{
    ...
    "intent":           "latex",
    "final_answer":     "Here is the LaTeX code for a Fourier Transform report...",
    "execution_result": ExecutionResult(success=True, stdout="", stderr=""),
    "agent_used":       "latex_agent"
}
```

---

## 🔄 Retry Loop (Code / LaTeX Only)

When an agent fails (e.g., the code throws a runtime error):

```
[code] → should_retry() → "retry"
              │
           [refine]    ← builds new refined_query with error feedback
              │
            [llm]      ← rewrites the query using the error context
              │
           [router]    ← re-classifies (still "code")
              │
           [code]      ← tries again
```

**State during retry** (after `refine` node):
```python
{
    ...
    "retry_count":  1,
    "errors":       ["NameError: name 'seive' is not defined"],
    "refined_query": "previous attempt failed: NameError. Fix: Python Sieve of Eratosthenes"
}
```

---

## 📊 State Field Ownership Table

| Field | Set By | Used By |
|:------|:-------|:--------|
| `user_query` | `run_agent.py` | `llm`, `web/code/db/latex` (fallback) |
| `refined_query` | `llm` | `router`, all agents |
| `intent` | `router` | `route_by_intent` edge |
| `final_answer` | web / code / db / latex agent | `final` |
| `execution_result` | code / latex / web agent | `final` |
| `agent_used` | code / web / db / latex agent | `final` |
| `sql` + `data` | `db` agent only | `final` |
| `metadata` | `code` agent | optional downstream |
| `retry_count` + `errors` | `refine` node | `should_retry` edge |
| `response` | `final` | printed by `run_agent.py` |
| `messages` | accumulated | `cleanup` (trimmed to 8) |

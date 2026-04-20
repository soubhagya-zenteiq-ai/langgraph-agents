# LangGraph Multi-Agent System

A production-ready, multi-agent AI system built with **LangGraph** and **Groq**. It autonomously routes natural language queries to specialized agents (Code, LaTeX, Web, DB), executes them in isolated Docker sandboxes, and self-corrects on failure.

> See [INFO.md](INFO.md) for the full High-Level & Low-Level Design documentation.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- A [Groq API Key](https://console.groq.com)

### 1. Configure Environment
```bash
# Create .env in root
echo "GROQ_API_KEY=your_groq_api_key" > .env
```

### 2. Build & Launch
```bash
docker-compose up --build -d
```
This spins up **4 containers**:
| Container | Image | Port | Purpose |
|---|---|---|---|
| `ai_piston_executor_api` | python:3.11-slim (custom) | `8001` | FastAPI orchestrator |
| `piston_engine` | ghcr.io/engineer-man/piston | `2000` | Code sandbox |
| `latex_checker` | texlive/texlive:latest-medium | (internal) | LaTeX compiler |
| `demo_postgres` | postgres:15-alpine | `5433` | Demo database |

### 3. Verify All Services
```bash
docker ps
```

---

## Running Queries

All commands are run inside the API container via `docker exec`.

### 💻 Code Generation & Sandbox Execution
```bash
# Python
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Write a Python script to calculate Fibonacci numbers up to 100"

# JavaScript / NodeJS
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Write a NodeJS script that sorts an array of objects by their age field"

# Go
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Write a Go program that prints Hello World"

# PHP
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Write a PHP script that calculates 2 to the power of 10"
```
> **Note:** If a language runtime is not installed, the system auto-installs it on the fly via the Piston API.

### 📄 LaTeX Document Generation
```bash
# Scientific report (compiles to PDF in ./latex_outputs/)
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Create a LaTeX report on Quantum Computing"

# Complex table
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Write a LaTeX document with a table showing properties of planets"

# Mathematical proof
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Generate a LaTeX document with a proof of the Pythagorean theorem"
```
> PDFs are saved to `./latex_outputs/` on the host machine.

### 🌐 Web Research
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "What are the latest breakthroughs in quantum computing?"

docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Summarize the plot of the movie Inception"
```

### 📊 Database Queries (Demo PostgreSQL)
```bash
# Simple query
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "How many products are in stock in the Electronics category?"

# Join query
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "List the total amount spent by Alice Johnson on all her orders"

# Aggregation
docker exec -it ai_piston_executor_api python scripts/run_agent.py \
  "Find the email of the user who placed the most expensive order"
```

### 🧪 Batch Testing
```bash
docker exec -it ai_piston_executor_api python scripts/test_queries.py
```

### 🌐 API Testing (Swagger & curl)
The API is exposed on port `8001`.

**Swagger UI (Interactive Browser Testing):**
👉 **[http://localhost:8001/docs](http://localhost:8001/docs)**

**curl Command:**
```bash
curl -X POST http://localhost:8001/agent/run \
     -H "Content-Type: application/json" \
     -d '{"query": "Create a simple React counter component"}'
```

---

## Demo Database Schema

Pre-loaded via `scripts/init-db.sql`:

| Table | Columns |
|---|---|
| `users` | `id`, `name`, `email`, `age`, `created_at` |
| `products` | `id`, `name`, `price`, `category`, `stock_quantity` |
| `orders` | `id`, `user_id`, `total_price`, `status`, `created_at` |

Connect directly:
```bash
docker exec -it demo_postgres psql -U user -d demo_db -c "SELECT * FROM users;"
```

---

## Project Structure
```
langgraph-agents/
├── docker-compose.yml          # 4-container orchestration
├── Dockerfile                  # API container image
├── requirements.txt            # Python dependencies
├── .env                        # GROQ_API_KEY
├── INFO.md                     # Full HLD + LLD documentation
├── scripts/
│   ├── run_agent.py            # CLI test runner
│   ├── test_queries.py         # Batch test suite
│   └── init-db.sql             # Demo DB seed data
├── src/
│   ├── agents/                 # Agent implementations
│   ├── services/               # External service clients
│   ├── graph/                  # LangGraph state machine
│   │   ├── builder.py          # Graph construction
│   │   ├── state.py            # Shared state schema
│   │   ├── nodes/              # Graph node functions
│   │   └── edges/              # Routing & retry logic
│   ├── prompts/                # LLM prompt templates
│   ├── api/                    # FastAPI application
│   └── latex_server.py         # TeXLive HTTP server
├── latex_outputs/              # Generated PDFs
└── piston/                     # Piston runtime packages
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `GROQ_API_KEY not found` | Ensure `.env` file exists with valid key |
| LaTeX compilation fails | Check `./latex_outputs/` logs; system retries up to 2x |
| DB connection refused | Wait for `demo_postgres` to finish init: `docker logs demo_postgres` |
| Language not found in Piston | Auto-install happens; first run may be slow (~30s) |
| Container OOM | Increase memory limit in `docker-compose.yml` (default: 512M) |

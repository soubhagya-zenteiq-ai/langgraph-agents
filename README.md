# LangGraph Multi-Agent System

A streamlined, unified AI agent architecture built with LangGraph.

## Features
- **Query Refinement**: Queries are automatically refined for better accuracy.
- **Intent Routing**: Intelligent routing to specialized agents.
- **Code Agent**: Senior engineer level code generation.
- **Web Agent**: Integrated Wikipedia and Google Search for real-time information.
- **DB Agent**: Natural language to SQL conversion and execution on PostgreSQL.
- **Dockerized**: Fully containerized with PostgreSQL and API.

## Capability Matrix
| Agent | Capability | Service |
|-------|------------|---------|
| Code  | Code Gen   | Groq Llama3 |
| Web   | Search     | Wiki + Google |
| DB    | SQL        | PostgreSQL |

## Sample Questions
You can interact with the system using natural language. Try these examples:

### 💻 Code Generation
- "Write a Python function to sort a list of numbers using the quicksort algorithm."
- "Create a basic HTML5/CSS3 landing page structure for a coffee shop."
- "Explain how to use decorators in Python with a simple example."

### 🌐 Web Research
- "Who is the current CEO of Microsoft and what was their most recent announcement?"
- "What is the capital of Japan and its current population?"
- "Summarize the latest news regarding SpaceX Starship launches."

### 📊 Database Queries (On Demo DB)
- "Get all users from the database who are older than 25."
- "Show me all products in the Electronics category with their prices."
- "What is the total price of all orders with a 'shipped' status?"
- "List the names and emails of all users who have placed at least one order."

## Demo Database Schema
The system comes with a pre-configured demo PostgreSQL database (`demo_db`) containing:
- **`users`**: `id`, `name`, `email`, `age`
- **`products`**: `id`, `name`, `price`, `category`, `stock_quantity`
- **`orders`**: `id`, `user_id`, `total_price`, `status`

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Groq API Key

### Configuration
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_groq_api_key
```

### Running with Docker
```bash
docker-compose up --build
```

### Testing the System
You can test the system using the provided scripts or direct API calls.

#### 🛠️ Direct CLI Tests (via Docker)
Run these commands to test specific capabilities. The system will print its `[THINKING]` process, refine your query, correctly route it, and show the exact execution results.

**Code Generation & Sandbox Execution:**
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Write a Python script to calculate Fibonacci numbers up to 100"
```
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Write a NodeJS script that sorts an array of objects by their 'age' field"
```
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Create a Python script that calculates the factorial of 5 and prints it"
```

**Web Research:**
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "What are the latest breakthroughs in quantum computing?"
```
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Who won the most recent Super Bowl and what was the score?"
```
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Summarize the plot of the movie Inception in two sentences"
```

**Database Analytics (On Demo DB):**
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "How many products are in stock in the Electronics category?"
```
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Are there any users who are younger than 25?"
```

**Complex Database Joins:**
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "List the total amount spent by Alice Johnson on all her orders."
```
```bash
docker exec -it ai_piston_executor_api python scripts/run_agent.py "Find the email address of the user who placed the most expensive order."
```

#### 🧪 Batch Testing
Run the automated test suite to see the system process multiple intents consecutively:
```bash
docker exec -it ai_piston_executor_api python scripts/test_queries.py
```

#### 🌐 API Testing (curl)
If you prefer testing the REST endpoint:
```bash
curl -X POST http://localhost:8001/agent/run \
     -H "Content-Type: application/json" \
     -d '{"query": "Create a simple React counter component"}'
```

# File Explanations and Commenting Plan

This plan outlines the task of documenting and adding comments to all files in the `langgraph-agents` repository.

## File Descriptions

### Core & API
- **src/api/main.py**: Entry point for the FastAPI application. It initializes the FastAPI app, registers the agent routes, and provides a basic health check endpoint.
- **src/api/routes/agent.py**: Defines the REST API endpoints for interacting with the AI agents. It handles incoming user queries, triggers the LangGraph workflow, and returns the response.
- **src/api/schemas/request.py**: Defines the Pydantic schemas for API requests and responses. It ensures data validation for the input query and structured output.

### Graph & Workflow
- **src/graph/builder.py**: Orchestrates the assembly of the LangGraph state machine. It defines how nodes (LLM, Router, Agents) are connected and handles conditional routing and retries.
- **src/graph/state.py**: Defines the system state (`AgentState`) shared across all nodes in the graph. It tracks the user query, intent, messages, tool inputs/outputs, and execution metadata.
- **src/graph/nodes/llm.py**: A core node that invokes the primary Language Model. It prepares the conversation context and executes the LLM to determine the next steps or final answers.
- **src/graph/nodes/router.py**: Analyzes the LLM output to determine the user's intent. It routes the flow to the appropriate agent (code, web, db, latex) based on the detected task.
- **src/graph/nodes/final.py**: The terminal node that processes the final output from an agent or the LLM. It formats the response for the user and ensures all necessary information is included.
- **src/graph/nodes/cleanup.py**: Performs post-processing tasks after the workflow is complete. It manages state cleanup and final logging before returning the result to the API.
- **src/graph/nodes/refine.py**: Handles query refinement and self-correction. If an agent execution fails or the LLM needs more clarity, this node updates the query to improve the next attempt.
- **src/graph/nodes/tool_executor.py**: (Generic node) Manages the execution of external tools or internal agent functions. It acts as an abstraction layer for tool calls within the graph.
- **src/graph/edges/routing.py**: Contains the logic for conditional routing based on intent. It maps specific intents to their corresponding agent nodes in the graph.
- **src/graph/edges/retry.py**: Implements retry logic in the workflow. It checks if an agent's execution resulted in an error and decides whether to retry the task or proceed to completion.

### Agents
- **src/agents/base_agent.py**: An abstract base class for all specialized agents. It defines the common interface (`run` method) and initializes shared services like the LLM.
- **src/agents/code_agent.py**: Specialized agent for handling programming tasks. It generates code using the LLM, executes it in a secure Piston sandbox, and returns the results.
- **src/agents/web_agent.py**: Agent designed for web-related queries such as searching and information retrieval. It utilizes web search tools to gather real-time data from the internet.
- **src/agents/db_agent.py**: Manages database-related tasks. It generates and executes SQL queries against a PostgreSQL instance, processing data for the final response.
- **src/agents/latex_agent.py**: Specialized in LaTeX document generation and compilation. It produces LaTeX code and uses the LaTeX service to render PDFs or images.

### Services & Tools
- **src/services/llm_service.py**: Wrapper for LLM interactions (e.g., Groq, OpenAI). It manages API calls, message formatting, and model configuration for the entire system.
- **src/services/piston_service.py**: Interface for the Piston code execution engine. It handles language runtime detection, installation, and secure code execution in isolated environments.
- **src/services/latex_service.py**: Provides LaTeX compilation capabilities. It communicates with a LaTeX server to transform TeX code into rendered outputs like PDF documents.
- **src/services/db_service.py**: Manages connections and operations for the PostgreSQL database. It provides an abstraction for running queries and fetching results securely.
- **src/services/web_service.py**: Core service for web interactions. It wraps search engine APIs and potentially other web-based tools for use by the Web Agent.
- **src/tools/code/generator.py**: Utility for generating boilerplate or specific code structures. It assists the Code Agent in producing valid and runnable source code.
- **src/tools/db/postgres.py**: Low-level database utility for PostgreSQL. It handles the raw connection pool and basic CRUD operations for the DB Service.
- **src/tools/db/query_builder.py**: Helper for constructing dynamic and safe SQL queries. It prevents SQL injection and simplifies complex query generation from LLM output.
- **src/tools/web/search.py**: Implementation of the web search tool. It interfaces with search providers (e.g., Google, Serper) to retrieve relevant snippets and URLs.
- **src/tools/utils.py**: General-purpose utilities used across different tools. Includes common helper functions for string manipulation, data formatting, etc.

### Utils & Config
- **src/utils/logger.py**: Configures and manages the application's logging system. It ensures consistent log formatting and output across all modules and services.
- **src/utils/parsers.py**: Contains functions for parsing LLM outputs. It extracts structured data like code blocks, JSON, or specific intents from raw text responses.
- **src/utils/prompts.py**: Utility for loading and managing LLM prompt templates. It centralizes prompt storage to allow for easy updates and versioning.
- **src/utils/validators.py**: Custom validation logic for system inputs and outputs. It ensures that data flowing through the graph meets specific criteria and constraints.
- **src/config/settings.py**: Main configuration module using Pydantic Settings. It loads environment variables and sets default values for API keys, URLs, and model names.
- **src/config/constants.py**: Defines static constants used throughout the application. Centralizes strings, limits, and other fixed values to avoid hardcoding.

### System & Infrastructure
- **src/latex_server.py**: A standalone Flask or FastAPI server that handles LaTeX compilation. It wraps a LaTeX distribution (like TeX Live) to provide rendering via API.
- **Dockerfile**: Defines the container image for the application. It sets up the Python environment, installs dependencies, and prepares the system for production.
- **docker-compose.yml**: Orchestrates the multi-container setup. It links the AI agent service with supporting containers like Piston, PostgreSQL, and the LaTeX server.
- **requirements.txt**: Lists all Python library dependencies required for the project. Used by pip to install the necessary packages during setup.
- **run.sh**: A bootstrap shell script to start the application. It handles environment setup, migrations, and launching the main API server.
- **install_piston_packages.sh**: A utility script to pre-load specific language runtimes into the Piston sandbox. Ensures that common languages are available at startup.


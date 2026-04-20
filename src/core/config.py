from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- API Metadata ---
    PROJECT_NAME: str = "AI Code Sandbox Service"
    API_VERSION: str = "1.0.0"
    DEBUG_MODE: bool = False

    # --- AI / LLM Keys ---
    # Pydantic will throw an error at startup if this is missing from the .env
    GROQ_API_KEY: str 

    # --- Sandbox / Execution Config ---
    # DOCKER_HOST is optional. llm-sandbox defaults to the local daemon socket
    # (e.g., unix://var/run/docker.sock) if not explicitly provided.
    DOCKER_HOST: Optional[str] = None
    
    # Safety rail: Maximum seconds a sandbox container is allowed to run 
    # before being killed (prevents infinite while-loops in generated code)
    MAX_EXECUTION_TIMEOUT: int = 15 

    # --- LangChain Tracing (Optional but recommended for production) ---
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "Code-Executor-Agent"

    # Pydantic V2 configuration to load variables from the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ignores extra variables in .env that aren't defined here
    )

# Instantiate a global settings object to be imported across the app
settings = Settings()
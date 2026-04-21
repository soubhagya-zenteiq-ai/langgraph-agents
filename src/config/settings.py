"""
Handles application environment settings and secrets using Pydantic Settings.
Ensures that all required environment variables are present and correctly typed.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # --- LLM Config ---
    GROQ_API_KEY: str
    DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.0

    # --- Service URLs ---
    PISTON_URL: str = "http://piston_engine:2000"
    LATEX_URL: str = "http://latex-checker:3000"
    
    # --- Database Config ---
    # Default for local docker-compose setup
    DATABASE_URL: str = "postgresql://user:password@demo_postgres:5432/demo_db"

    # --- Pydantic Config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton instance
settings = Settings()

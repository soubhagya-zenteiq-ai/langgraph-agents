"""
Wrapper for LLM interactions (e.g., Groq, OpenAI).
Manages API calls, message formatting, and model configuration.
Provides a unified interface for the system to invoke language models.
"""
import os

from typing import Optional
from src.config.settings import settings
from langchain_groq import ChatGroq

class LLMService:
    def __init__(self, model_name: Optional[str] = None, temperature: Optional[float] = None):
        self.model = ChatGroq(
            model=model_name or settings.DEFAULT_MODEL,
            temperature=temperature if temperature is not None else settings.TEMPERATURE,
            groq_api_key=settings.GROQ_API_KEY
        )

    def invoke(self, prompt: str) -> str:
        """Safe LLM call"""
        response = self.model.invoke(prompt)
        return str(response.content)

    def stream(self, prompt: str):
        """Streaming support"""
        return self.model.stream(prompt)
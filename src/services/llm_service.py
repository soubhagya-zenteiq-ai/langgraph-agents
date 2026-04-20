import os
from typing import Optional
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.model = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=api_key
        )

    def invoke(self, prompt: str) -> str:
        """Safe LLM call"""
        response = self.model.invoke(prompt)
        return str(response.content)

    def stream(self, prompt: str):
        """Streaming support"""
        return self.model.stream(prompt)
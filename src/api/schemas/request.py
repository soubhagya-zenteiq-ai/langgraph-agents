"""
Defines Pydantic models for API request validation.
Ensures that incoming data follows the expected structure for agent queries.
Used by the FastAPI routes to enforce type safety and data integrity.
"""
from pydantic import BaseModel



class AgentRequest(BaseModel):
    query: str
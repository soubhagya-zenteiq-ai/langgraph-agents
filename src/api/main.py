"""
Entry point for the FastAPI application.
Initializes the FastAPI app, registers agent routes, and provides a health check.
This serves as the main web interface for the multi-agent system.
"""
from fastapi import FastAPI

from src.config.settings import settings
from src.api.routes.agent import router as agent_router


app = FastAPI(
    title="AI Agent System",
    description="Multi-capability AI agent using LangGraph",
    version="1.0.0"
)


# Register routes
app.include_router(agent_router, prefix="/agent")


# Health check
@app.get("/")
def root():
    return {"status": "ok"}
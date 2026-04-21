"""
Abstract base class for all specialized agents.
Defines the common interface (run method) and initializes shared services.
Ensures that all agents follow a consistent structure for LangGraph integration.
"""
from abc import ABC, abstractmethod

from typing import Any, Dict


class BaseAgent(ABC):
    def __init__(self, llm_service):
        self.llm = llm_service

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic"""
        pass
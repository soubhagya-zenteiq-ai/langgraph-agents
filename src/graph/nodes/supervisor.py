"""
Manages the execution queue for multi-agent workflows.
Decides which agent to run next based on the planned selected_agents.
"""
from typing import Dict, Any


def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    selected_agents = state.get("selected_agents", [])
    
    # Check if we were in the middle of a retry for the current agent
    # We use agent_used as a tracker for what we are currently doing
    current_agent = state.get("agent_used")
    
    if not selected_agents:
        print("[SUPERVISOR] All tasks completed. Moving to final output.")
        return {"intent": "final"}
        
    # If the current agent is still the first in the list, 
    # it means we are potentially retrying or just starting it.
    next_agent = selected_agents[0]
    
    print(f"[SUPERVISOR] Active step: {next_agent}. Remaining queue: {selected_agents[1:]}")
    
    return {
        "intent": next_agent,
        "agent_used": next_agent
    }

def pop_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Called after an agent successfully completes its task to move to the next item in the queue.
    """
    selected_agents = state.get("selected_agents", [])
    if selected_agents:
        completed = selected_agents[0]
        remaining = selected_agents[1:]
        print(f"[SUPERVISOR] Completed: {completed}. Moving to next...")
        return {"selected_agents": remaining}
    return {}

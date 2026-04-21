"""
Terminal node that processes the final output from agents or the LLM.
Formats the response for the user and ensures all necessary information is included.
Acts as the final aggregation point before the workflow concludes.
"""
from typing import Dict, Any
from src.api.schemas.service_responses import ExecutionResult, DBResponse


def final_node(state: Dict[str, Any]) -> Dict[str, Any]:
    final_output = state.get("final_answer", "No response generated")
    
    # Append code execution sandbox result if present
    if "execution_result" in state:
        result = state["execution_result"]
        agent_used = state.get("agent_used", "")
        
        # Check if result is a Pydantic model
        if isinstance(result, ExecutionResult):
            if agent_used == "code_agent":
                status_icon = "✅" if result.success else "❌"
                content = result.stdout if result.success else result.stderr
                final_output += f"\n\n--- 🖥️ SANDBOX EXECUTION {status_icon} ---\n{content}\n-----------------------------------"
            
            elif agent_used == "latex_agent":
                if result.success:
                    # In our new model, success means extraction/compilation worked
                    final_output += f"\n\n--- 📄 LATEX COMPILATION SUCCESS ---\nCheck /latex_outputs for the PDF result.\n--------------------------------------"
                else:
                    error_context = result.stderr or result.stdout[-500:]
                    final_output += f"\n\n--- ❌ LATEX COMPILATION FAILED ---\nError Logs:\n{error_context}\n-----------------------------------"

    # Append database query / raw data if present
    if "sql" in state and "data" in state:
        sql = state["sql"]
        data = state["data"]
        
        if isinstance(data, DBResponse):
            data_str = data.data if data.status == "success" else f"Error: {data.error}"
        else:
            data_str = str(data)
            
        final_output += f"\n\n--- 🗄️ DATABASE METADATA ---\nSQL Executed:\n```sql\n{sql}\n```\nRaw Data Returned:\n{data_str}\n------------------------------"

    return {
        "response": final_output
    }
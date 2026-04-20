from typing import Dict, Any


def final_node(state: Dict[str, Any]) -> Dict[str, Any]:
    final_output = state.get("final_answer", "No response generated")
    
    # Append code execution sandbox result if present
    if "execution_result" in state:
        result = state["execution_result"]
        # Piston execution returns raw output in "run" dict
        run_output = result.get("run", {}).get("output", "No output or execution failed")
        
        final_output += f"\n\n--- 🖥️ SANDBOX EXECUTION OUTPUT ---\n{run_output}\n-----------------------------------"

    # Append database query / raw data if present
    if "sql" in state and "data" in state:
        sql = state["sql"]
        data = state["data"]
        final_output += f"\n\n--- 🗄️ DATABASE METADATA ---\nSQL Executed:\n```sql\n{sql}\n```\nRaw Data Returned:\n{data}\n------------------------------"

    return {
        "response": final_output
    }
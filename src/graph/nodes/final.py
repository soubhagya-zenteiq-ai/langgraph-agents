from typing import Dict, Any


def final_node(state: Dict[str, Any]) -> Dict[str, Any]:
    final_output = state.get("final_answer", "No response generated")
    
    # Append code execution sandbox result if present
    if "execution_result" in state:
        result = state["execution_result"]
        agent_used = state.get("agent_used", "")
        
        if agent_used == "code_agent":
            # Piston execution returns raw output in "run" dict
            run_output = result.get("run", {}).get("output", "No output or execution failed")
            final_output += f"\n\n--- 🖥️ SANDBOX EXECUTION OUTPUT ---\n{run_output}\n-----------------------------------"
        
        elif agent_used == "latex_agent":
            pdf_name = result.get("pdf_filename")
            if pdf_name:
                final_output += f"\n\n--- 📄 LATEX COMPILATION SUCCESS ---\nGenerated PDF: {pdf_name}\nLocation: /latex_outputs/{pdf_name}\n--------------------------------------"
            else:
                stderr = result.get("stderr", "")
                stdout = result.get("stdout", "")
                # pdflatex errors are often at the end of stdout
                error_context = stderr + "\n" + (stdout[-500:] if stdout else "No log output")
                final_output += f"\n\n--- ❌ LATEX COMPILATION FAILED ---\nError Logs:\n{error_context}\n-----------------------------------"

    # Append database query / raw data if present
    if "sql" in state and "data" in state:
        sql = state["sql"]
        data = state["data"]
        final_output += f"\n\n--- 🗄️ DATABASE METADATA ---\nSQL Executed:\n```sql\n{sql}\n```\nRaw Data Returned:\n{data}\n------------------------------"

    return {
        "response": final_output
    }
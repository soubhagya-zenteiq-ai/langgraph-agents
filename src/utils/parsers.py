"""
Contains functions for parsing LLM outputs.
Extracts structured data like code blocks, JSON, or specific intents from raw text responses.
Provides robust text processing to transform unstructured AI responses into system-usable data.
"""
import re


def extract_code_and_lang(text: str):
    """
    Extracts language and code from markdown code blocks.
    Default to 'python' if none found.
    """
    pattern = r"```(\w+)\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).lower(), match.group(2).strip()
    
    # Fallback to python
    return "python", text.strip()

def clean_sql(text: str) -> str:
    """
    Strips markdown code blocks from SQL queries.
    """
    return text.replace("```sql", "").replace("```", "").strip()

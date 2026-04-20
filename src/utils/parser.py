import re
import json
from typing import Any, Dict, List


# -----------------------------
# JSON parsing
# -----------------------------

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract JSON object from LLM output safely.
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {}


# -----------------------------
# List extraction
# -----------------------------

def extract_list(text: str) -> List[str]:
    """
    Extract bullet/line items from text.
    """
    lines = text.split("\n")
    items = []

    for line in lines:
        line = line.strip("-• ").strip()
        if line:
            items.append(line)

    return items


# -----------------------------
# Clean text
# -----------------------------

def clean_text(text: str) -> str:
    return text.strip()


# -----------------------------
# Extract code block
# -----------------------------

def extract_code(text: str) -> str:
    """
    Extract code block from markdown-style response.
    """
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()
import re
from typing import Any, Dict


# -----------------------------
# Text / Parsing utils
# -----------------------------

def extract_json(text: str) -> Dict[str, Any]:
    """
    Try extracting JSON from LLM output.
    """
    try:
        import json

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {}


# -----------------------------
# Safe string utils
# -----------------------------

def clean_text(text: str) -> str:
    """
    Basic cleanup for LLM output
    """
    return text.strip().replace("\n\n", "\n")


# -----------------------------
# SQL safety helpers
# -----------------------------

def is_read_only_query(sql: str) -> bool:
    sql = sql.lower().strip()

    forbidden = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create"
    ]

    if not sql.startswith("select"):
        return False

    for f in forbidden:
        if f in sql:
            return False

    return True


# -----------------------------
# Generic validator
# -----------------------------

def ensure_keys(data: Dict[str, Any], keys: list) -> bool:
    """
    Ensure required keys exist
    """
    return all(k in data for k in keys)
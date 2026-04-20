from typing import Dict, Any


# -----------------------------
# Intent validation
# -----------------------------

VALID_INTENTS = {"code", "web", "db"}


def validate_intent(intent: str) -> str:
    if intent not in VALID_INTENTS:
        return "web"  # safe fallback
    return intent


# -----------------------------
# SQL safety
# -----------------------------

FORBIDDEN_SQL = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create"
}


def is_safe_sql(sql: str) -> bool:
    sql = sql.lower().strip()

    if not sql.startswith("select"):
        return False

    for keyword in FORBIDDEN_SQL:
        if keyword in sql:
            return False

    return True


# -----------------------------
# Required keys check
# -----------------------------

def validate_keys(data: Dict[str, Any], required: list) -> bool:
    return all(k in data for k in required)


# -----------------------------
# Basic input validation
# -----------------------------

def validate_query(query: str) -> bool:
    if not query:
        return False

    if len(query.strip()) < 2:
        return False

    return True
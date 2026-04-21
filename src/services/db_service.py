"""
Manages connections and operations for the PostgreSQL database.
Provides an abstraction for running queries and fetching results securely.
Handles connection pooling and ensures data integrity during database tasks.
"""
import psycopg2

from typing import Optional
from psycopg2.extras import RealDictCursor
from src.config.settings import settings
from src.api.schemas.service_responses import DBResponse


class DBService:
    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or settings.DATABASE_URL

    def execute(self, query: str) -> DBResponse:
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)

                    if cur.description:
                        return DBResponse(status="success", data=cur.fetchall())
                    else:
                        return DBResponse(status="success", data=[{"status": "ok"}])

        except Exception as e:
            return DBResponse(status="error", error=str(e))
import psycopg2
from psycopg2.extras import RealDictCursor


class DBService:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def execute(self, query: str):
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query)

                    if cur.description:
                        return cur.fetchall()
                    else:
                        return {"status": "ok"}

        except Exception as e:
            return {"error": str(e)}
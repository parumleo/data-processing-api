"""Database connectivity and persistence of verified CSV processing summaries."""
import json
import os


def _connect():
    # Import here so the CSV API can run and be tested without a database server.
    import psycopg2

    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    return psycopg2.connect(url, connect_timeout=5)


def check_database() -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()


def save_summary(summary: dict) -> int:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sales_processing_runs (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    received_orders INTEGER NOT NULL,
                    completed_orders INTEGER NOT NULL,
                    total_revenue NUMERIC(14,2) NOT NULL,
                    result_json JSONB NOT NULL
                )
            """)
            cur.execute("""
                INSERT INTO sales_processing_runs
                    (received_orders, completed_orders, total_revenue, result_json)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (
                summary["received_orders"], summary["completed_orders"],
                summary["total_revenue"], json.dumps(summary),
            ))
            return int(cur.fetchone()[0])

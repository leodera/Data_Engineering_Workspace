import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(override=True)


def execute_sql(sql_query, db_type="pg", params=None):
    """Executes SQL statements against PostgreSQL or MySQL.

    Handles SELECT (returns DataFrame), DML (INSERT/UPDATE/DELETE), and DDL
    (CREATE/DROP).
    """
    url_key = "POSTGRES_URL" if db_type == "pg" else "MYSQL_URL"
    db_url = os.getenv(url_key)

    if not db_url:
        raise ValueError(f"Environment variable '{url_key}' is not set.")

    engine = create_engine(db_url, pool_pre_ping=True)

    clean_query = sql_query.strip().lower()
    is_select = clean_query.startswith("select") or clean_query.startswith(
        "with"
    )

    with engine.connect() as conn:
        if is_select:
            return pd.read_sql_query(text(sql_query), conn, params=params)
        else:
            with conn.begin():
                result = conn.execute(text(sql_query), params or {})
                return f"Execution successful. Rows affected: {result.rowcount}"


def run_pg_query(sql_query, params=None):
    return execute_sql(sql_query, db_type="pg", params=params)


def run_mysql_query(sql_query, params=None):
    return execute_sql(sql_query, db_type="mysql", params=params)

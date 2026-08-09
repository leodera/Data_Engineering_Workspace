# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python (Jupyter_env)
#     language: python
#     name: jupyter_env
# ---

# %%
# %%writefile db_utils.py
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv(override=True)

def run_pg_query(sql_query):
    """Executes SQL against PostgreSQL lazily."""
    pg_url = os.getenv("POSTGRES_URL")
    engine = create_engine(pg_url, pool_pre_ping=True)
    with engine.connect() as conn:
        return pd.read_sql_query(sql_query, conn)

def run_mysql_query(sql_query):
    """Executes SQL against MySQL lazily."""
    mysql_url = os.getenv("MYSQL_URL")
    engine = create_engine(mysql_url, pool_pre_ping=True)
    with engine.connect() as conn:
        return pd.read_sql_query(sql_query, conn)

# %%

import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv(override=True)
url =os.getenv("MYSQL_URL")
mysql_engine = create_engine(
    url,
    pool_pre_ping=True
)

query = """SELECT *
           FROM v_retail
           LIMIT 1000;"""

df = pd.read_sql(query, con=mysql_engine)
df

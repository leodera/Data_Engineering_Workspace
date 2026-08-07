import pandas as pd
from sqlalchemy import create_engine

# 🔹 PostgreSQL connection string with SSL
conn_str = "postgresql://avnadmin:"PASSWORD"@pg-2461fc86-pascalchidera21-0ad9.h.aivencloud.com:14160/defaultdb?sslmode=require"

# 🔹 Create engine
engine = create_engine(conn_str)

# 🔹 Load CSV and convert '?' to NaN/NULL automatically
file_path = r"C:\Users\Dell\Downloads\car_info.csv.csv"
df = pd.read_csv(file_path, na_values=['?'])

# 🔹 Clean column names (strip spaces, lowercase) to avoid SQL syntax errors
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# 🔹 Upload to PostgreSQL
df.to_sql(
    name="car_info",
    con=engine,
    if_exists="append",   # Change to 'replace' if creating table for the first time
    index=False
)

print("✅ Data uploaded successfully!")
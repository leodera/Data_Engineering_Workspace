import pandas as pd
from sqlalchemy import create_engine, text

# 1. File Path
file_path = r"C:\Users\Dell\Downloads\Movie_Data.csv"

# 2. Database Connection Strings
# PostgreSQL Connection (Aiven Cloud SSL Enabled)
pg_url = "postgresql+psycopg2://avnadmin:AVNS_gfgTO8VJrwgd96ey2bW@pg-2461fc86-pascalchidera21-0ad9.h.aivencloud.com:14160/defaultdb?sslmode=require"
pg_engine = create_engine(pg_url, pool_pre_ping=True)

# MySQL Connection (Aiven Cloud SSL Enabled)
mysql_url = "mysql+pymysql://avnadmin:AVNS_tkMbRWpQWYzHFqbAR8-@mysql-37f12a2a-pascalchidera21-0ad9.i.aivencloud.com:14160/defaultdb"
mysql_engine = create_engine(
    mysql_url,
    connect_args={"ssl": {"ssl_mode": "REQUIRED"}},
    pool_pre_ping=True
)

# 3. Read and Clean CSV Data
print("Reading and cleaning Movie_Data.csv...")
df = pd.read_csv(file_path)

# Map raw CSV headers to standard SQL snake_case column names
column_mapping = {
    'Movie Title': 'movie_title',
    'Release Date': 'release_date',
    'Wikipedia URL': 'wikipedia_url',
    'Genre': 'genre',
    'Director (1)': 'director_1',
    'Director (2)': 'director_2',
    'Cast (1)': 'cast_1',
    'Cast (2)': 'cast_2',
    'Cast (3)': 'cast_3',
    'Cast (4)': 'cast_4',
    'Cast (5)': 'cast_5',
    'Budget ': 'budget',
    'Revenue': 'revenue'
}
df = df.rename(columns=column_mapping)

# Clean numeric currency values ($15,000,000.00 -> 15000000.00)
for col in ['budget', 'revenue']:
    df[col] = df[col].astype(str).str.replace(r'[\$,]', '', regex=True)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Format release_date to proper date objects
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

# 4. PostgreSQL: Create Schema and Table
print("Initializing PostgreSQL schema and table...")
with pg_engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS movie_data;"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS movie_data.movies (
            id SERIAL PRIMARY KEY,
            movie_title VARCHAR(255),
            release_date DATE,
            wikipedia_url TEXT,
            genre VARCHAR(100),
            director_1 VARCHAR(150),
            director_2 VARCHAR(150),
            cast_1 VARCHAR(150),
            cast_2 VARCHAR(150),
            cast_3 VARCHAR(150),
            cast_4 VARCHAR(150),
            cast_5 VARCHAR(150),
            budget NUMERIC(15, 2),
            revenue NUMERIC(15, 2)
        );
    """))
    conn.commit()

# 5. MySQL: Create Database/Schema and Table
print("Initializing MySQL database and table...")
with mysql_engine.connect() as conn:
    # MySQL uses DATABASE synonymous with SCHEMA
    conn.execute(text("CREATE DATABASE IF NOT EXISTS movie_data;"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS movie_data.movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_title VARCHAR(255),
            release_date DATE,
            wikipedia_url VARCHAR(500),
            genre VARCHAR(100),
            director_1 VARCHAR(150),
            director_2 VARCHAR(150),
            cast_1 VARCHAR(150),
            cast_2 VARCHAR(150),
            cast_3 VARCHAR(150),
            cast_4 VARCHAR(150),
            cast_5 VARCHAR(150),
            budget DECIMAL(15, 2),
            revenue DECIMAL(15, 2)
        );
    """))
    conn.commit()

# 6. Upload Cleaned Data to PostgreSQL
print(f"Uploading {len(df)} rows to PostgreSQL (movie_data.movies)...")
df.to_sql(
    name='movies',
    con=pg_engine,
    schema='movie_data',
    if_exists='append',
    index=False,
    chunksize=500
)
print("PostgreSQL upload complete.")

# 7. Upload Cleaned Data to MySQL
print(f"Uploading {len(df)} rows to MySQL (movie_data.movies)...")
df.to_sql(
    name='movies',
    con=mysql_engine,
    schema='movie_data',
    if_exists='append',
    index=False,
    chunksize=500
)
print("MySQL upload complete.")

print("\n🎉 Migration complete! All movie records successfully uploaded to both databases.")
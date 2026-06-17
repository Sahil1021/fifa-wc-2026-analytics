import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')},1433;"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(connection_string)

conn = get_connection()
cursor = conn.cursor()

# Check England vs Croatia specifically
cursor.execute("""
    SELECT m.match_id, m.match_date, m.home_score, m.away_score, t1.team_name, t2.team_name
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.team_id
    JOIN teams t2 ON m.away_team_id = t2.team_id
    WHERE t1.team_name = 'England' AND t2.team_name = 'Croatia'
""")
rows = cursor.fetchall()
print(f"Rows found for England vs Croatia: {len(rows)}")
for row in rows:
    print(f"  match_id={row[0]} date={row[1]} score={row[2]}-{row[3]} {row[4]} vs {row[5]}")

# Check all matches involving England
print("\nAll England matches in DB:")
cursor.execute("""
    SELECT m.match_id, m.match_date, m.home_score, m.away_score, t1.team_name, t2.team_name
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.team_id
    JOIN teams t2 ON m.away_team_id = t2.team_id
    WHERE t1.team_name = 'England' OR t2.team_name = 'England'
""")
for row in cursor.fetchall():
    print(f"  match_id={row[0]} date={row[1]} score={row[2]}-{row[3]} {row[4]} vs {row[5]}")

# Count total rows in matches table vs how many have scores
cursor.execute("SELECT COUNT(*) FROM matches")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM matches WHERE home_score IS NOT NULL")
with_score = cursor.fetchone()[0]
print(f"\nTotal rows in matches table: {total}")
print(f"Rows with non-null home_score: {with_score}")

conn.close()
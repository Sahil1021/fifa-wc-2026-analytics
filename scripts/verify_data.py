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

def verify():
    conn = get_connection()
    cursor = conn.cursor()

    print("=" * 50)
    print("📊 DATABASE VERIFICATION REPORT")
    print("=" * 50)

    # Count teams
    cursor.execute("SELECT COUNT(*) FROM teams")
    print(f"\n✅ Total Teams: {cursor.fetchone()[0]}")

    # Count matches
    cursor.execute("SELECT COUNT(*) FROM matches")
    print(f"✅ Total Matches: {cursor.fetchone()[0]}")

    # Matches played so far
    cursor.execute("SELECT COUNT(*) FROM matches WHERE home_score IS NOT NULL")
    print(f"✅ Matches Played: {cursor.fetchone()[0]}")

    # Matches remaining
    cursor.execute("SELECT COUNT(*) FROM matches WHERE home_score IS NULL")
    print(f"✅ Matches Remaining: {cursor.fetchone()[0]}")

    # Sample teams
    print("\n📋 Sample Teams in Database:")
    cursor.execute("SELECT team_name, fifa_code, confederation FROM teams ORDER BY team_name")
    for i, row in enumerate(cursor.fetchall()):
        if i < 10:
            print(f"   {row[1]} | {row[0]} | {row[2]}")

    # Sample matches played
    print("\n⚽ Recent Matches Played:")
    cursor.execute("""
        SELECT 
            t1.team_name as home_team,
            m.home_score,
            m.away_score,
            t2.team_name as away_team,
            m.stage,
            m.match_date
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.home_score IS NOT NULL
        ORDER BY m.match_date DESC
    """)
    rows = cursor.fetchall()
    if rows:
        for row in rows[:5]:
            print(f"   {row[0]} {row[1]}-{row[2]} {row[3]} | {row[4]} | {row[5]}")
    else:
        print("   No completed matches yet")

    print("\n" + "=" * 50)
    conn.close()

if __name__ == "__main__":
    verify()
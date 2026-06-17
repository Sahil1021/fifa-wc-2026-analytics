import requests
import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('FOOTBALL_API_KEY')
HEADERS = {"X-Auth-Token": API_KEY}

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

def find_team_id(cursor, tla_code, team_name):
    cursor.execute("SELECT team_id FROM teams WHERE fifa_code = ?", tla_code)
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("SELECT team_id FROM teams WHERE team_name = ?", team_name)
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("SELECT team_id FROM teams WHERE team_name LIKE ?", f"%{team_name}%")
    result = cursor.fetchone()
    return result[0] if result else None

response = requests.get(
    "https://api.football-data.org/v4/competitions/WC/matches",
    headers=HEADERS
)
matches = response.json().get('matches', [])
completed = [m for m in matches if m.get('score', {}).get('fullTime', {}).get('home') is not None]

conn = get_connection()
cursor = conn.cursor()

print(f"🔍 Tracing all {len(completed)} completed matches through the actual insert logic:\n")

for match in completed:
    home_name = match.get('homeTeam', {}).get('name', '')
    away_name = match.get('awayTeam', {}).get('name', '')
    home_tla = match.get('homeTeam', {}).get('tla', '')
    away_tla = match.get('awayTeam', {}).get('tla', '')
    match_date = match.get('utcDate', '')

    home_id = find_team_id(cursor, home_tla, home_name)
    away_id = find_team_id(cursor, away_tla, away_name)

    if not home_id or not away_id:
        print(f"❌ TEAM MATCH FAILED: {home_name} vs {away_name}")
        continue

    cursor.execute("""
        SELECT match_id, match_date FROM matches
        WHERE home_team_id = ? AND away_team_id = ? AND match_date = ?
    """, home_id, away_id, match_date)
    existing = cursor.fetchone()

    if existing:
        print(f"⏭️  Already in DB: {home_name} vs {away_name}")
    else:
        # Check if it exists under a DIFFERENT date format (the suspect)
        cursor.execute("""
            SELECT match_id, match_date FROM matches
            WHERE home_team_id = ? AND away_team_id = ?
        """, home_id, away_id)
        any_match = cursor.fetchone()
        if any_match:
            print(f"⚠️  EXISTS BUT DATE MISMATCH: {home_name} vs {away_name}")
            print(f"     API date:  '{match_date}'")
            print(f"     DB date:   '{any_match[1]}'")
        else:
            print(f"🆕 NOT IN DB YET (should insert): {home_name} {match.get('score',{}).get('fullTime',{}).get('home')}-{match.get('score',{}).get('fullTime',{}).get('away')} {away_name} | date={match_date}")

conn.close()
print("\n✅ Trace complete")
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

response = requests.get(
    "https://api.football-data.org/v4/competitions/WC/matches",
    headers=HEADERS
)
matches = response.json().get('matches', [])
completed = [m for m in matches if m.get('score', {}).get('fullTime', {}).get('home') is not None]

conn = get_connection()
cursor = conn.cursor()

print(f"🔍 Checking all {len(completed)} completed matches against our teams table:\n")

for match in completed:
    home_name = match['homeTeam']['name']
    away_name = match['awayTeam']['name']
    home_tla = match['homeTeam'].get('tla')
    away_tla = match['awayTeam'].get('tla')
    
    cursor.execute("SELECT team_id FROM teams WHERE fifa_code = ?", home_tla)
    home_result = cursor.fetchone()
    
    cursor.execute("SELECT team_id FROM teams WHERE fifa_code = ?", away_tla)
    away_result = cursor.fetchone()
    
    home_status = "✅" if home_result else "❌ NOT FOUND"
    away_status = "✅" if away_result else "❌ NOT FOUND"
    
    if not home_result or not away_result:
        print(f"⚠️  {home_name} ({home_tla}) {home_status}  vs  {away_name} ({away_tla}) {away_status}")

conn.close()
print("\n✅ Diagnostic complete")
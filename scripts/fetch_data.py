import requests
import pyodbc
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# API setup
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4"
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

def fetch_teams():
    """Fetch all World Cup 2026 teams and load into Azure SQL"""
    print("🔄 Fetching teams from API...")
    
    # WC 2026 competition code is WC
    response = requests.get(
        f"{BASE_URL}/competitions/WC/teams",
        headers=HEADERS
    )
    
    # Check rate limit headers as advised
    print(f"API calls remaining: {response.headers.get('X-Requests-Available-Minute', 'N/A')}")
    
    if response.status_code != 200:
        print(f"❌ API error: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    teams = data.get('teams', [])
    print(f"✅ Found {len(teams)} teams")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for team in teams:
        # Check if team already exists
        cursor.execute("SELECT team_id FROM teams WHERE fifa_code = ?", team.get('tla', ''))
        existing = cursor.fetchone()
        
        if not existing:
            cursor.execute("""
                INSERT INTO teams (team_name, fifa_code, confederation)
                VALUES (?, ?, ?)
            """, 
            team.get('name', ''),
            team.get('tla', ''),
            team.get('area', {}).get('name', '')
            )
            print(f"  ✅ Inserted: {team.get('name')}")
        else:
            print(f"  ⏭️ Already exists: {team.get('name')}")
    
    conn.commit()
    conn.close()
    print(f"\n🎉 Teams loaded into Azure SQL successfully!")

def fetch_matches():
    """Fetch all World Cup 2026 matches"""
    print("\n🔄 Fetching matches from API...")
    
    response = requests.get(
        f"{BASE_URL}/competitions/WC/matches",
        headers=HEADERS
    )
    
    print(f"API calls remaining: {response.headers.get('X-Requests-Available-Minute', 'N/A')}")
    
    if response.status_code != 200:
        print(f"❌ API error: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    matches = data.get('matches', [])
    print(f"✅ Found {len(matches)} matches")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for match in matches:
        # Get team IDs from our database
        home_team_code = match.get('homeTeam', {}).get('tla', '')
        away_team_code = match.get('awayTeam', {}).get('tla', '')
        
        cursor.execute("SELECT team_id FROM teams WHERE fifa_code = ?", home_team_code)
        home_team = cursor.fetchone()
        
        cursor.execute("SELECT team_id FROM teams WHERE fifa_code = ?", away_team_code)
        away_team = cursor.fetchone()
        
        if home_team and away_team:
            # Check if match already exists
            match_date = match.get('utcDate', '')
            cursor.execute("""
                SELECT match_id FROM matches 
                WHERE home_team_id = ? AND away_team_id = ? AND match_date = ?
            """, home_team[0], away_team[0], match_date)
            
            existing = cursor.fetchone()
            
            if not existing:
                score = match.get('score', {})
                full_time = score.get('fullTime', {})
                
                cursor.execute("""
                    INSERT INTO matches 
                    (match_date, stage, group_name, home_team_id, away_team_id, 
                     home_score, away_score, venue, city)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                match_date,
                match.get('stage', ''),
                match.get('group', ''),
                home_team[0],
                away_team[0],
                full_time.get('home'),
                full_time.get('away'),
                match.get('venue', ''),
                match.get('area', {}).get('name', '')
                )
    
    conn.commit()
    conn.close()
    print(f"🎉 Matches loaded into Azure SQL successfully!")

if __name__ == "__main__":
    fetch_teams()
    fetch_matches()
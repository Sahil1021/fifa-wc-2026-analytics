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

def find_team_id(cursor, tla_code, team_name):
    """Try matching by TLA first, fall back to name matching.
    Handles cases where the API's TLA code differs from what's
    stored in our database (e.g. Uruguay = URY in API vs URU in our table)."""
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

def fetch_teams():
    """Fetch all World Cup 2026 teams and load into Azure SQL"""
    print("🔄 Fetching teams from API...")

    response = requests.get(
        f"{BASE_URL}/competitions/WC/teams",
        headers=HEADERS
    )

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
    """Fetch all World Cup 2026 matches.
    Inserts brand new fixtures, and UPDATES existing fixtures with
    final scores once results come in (fixtures are originally loaded
    with NULL scores before kickoff)."""
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

    inserted_count = 0
    updated_count = 0
    skipped_count = 0

    for match in matches:
        home_team_code = match.get('homeTeam', {}).get('tla', '')
        away_team_code = match.get('awayTeam', {}).get('tla', '')
        home_team_name = match.get('homeTeam', {}).get('name', '')
        away_team_name = match.get('awayTeam', {}).get('name', '')

        home_team_id = find_team_id(cursor, home_team_code, home_team_name)
        away_team_id = find_team_id(cursor, away_team_code, away_team_name)

        if home_team_id and away_team_id:
            match_date = match.get('utcDate', '')
            score = match.get('score', {})
            full_time = score.get('fullTime', {})
            api_home_score = full_time.get('home')
            api_away_score = full_time.get('away')

            cursor.execute("""
                SELECT match_id, home_score, away_score FROM matches
                WHERE home_team_id = ? AND away_team_id = ? AND match_date = ?
            """, home_team_id, away_team_id, match_date)

            existing = cursor.fetchone()

            if not existing:
                cursor.execute("""
                    INSERT INTO matches
                    (match_date, stage, group_name, home_team_id, away_team_id,
                     home_score, away_score, venue, city)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                match_date,
                match.get('stage', ''),
                match.get('group', ''),
                home_team_id,
                away_team_id,
                api_home_score,
                api_away_score,
                match.get('venue', ''),
                match.get('area', {}).get('name', '')
                )
                inserted_count += 1
            else:
                # Fixture row already exists. If the API now has a final
                # score that differs from what's stored, update it.
                db_match_id, db_home_score, db_away_score = existing
                if api_home_score is not None and (
                    db_home_score != api_home_score or db_away_score != api_away_score
                ):
                    cursor.execute("""
                        UPDATE matches
                        SET home_score = ?, away_score = ?
                        WHERE match_id = ?
                    """, api_home_score, api_away_score, db_match_id)
                    updated_count += 1
                    print(f"  🔄 Updated score: {home_team_name} {api_home_score}-{api_away_score} {away_team_name}")
        else:
            skipped_count += 1

    conn.commit()
    conn.close()
    print(f"\n🎉 Matches processed!")
    print(f"   Newly inserted: {inserted_count}")
    print(f"   Scores updated: {updated_count}")
    print(f"   Skipped (no team match / TBD fixtures): {skipped_count}")

if __name__ == "__main__":
    fetch_teams()
    fetch_matches()
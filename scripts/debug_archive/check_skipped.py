import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('FOOTBALL_API_KEY')
HEADERS = {"X-Auth-Token": API_KEY}

response = requests.get(
    "https://api.football-data.org/v4/competitions/WC/matches",
    headers=HEADERS
)
matches = response.json().get('matches', [])

none_count = 0
real_issue_count = 0
completed_with_none = []

for match in matches:
    home = match.get('homeTeam', {})
    away = match.get('awayTeam', {})
    home_tla = home.get('tla')
    away_tla = away.get('tla')
    has_score = match.get('score', {}).get('fullTime', {}).get('home') is not None

    if home_tla is None or away_tla is None:
        none_count += 1
        if has_score:
            completed_with_none.append(match)
            real_issue_count += 1

print(f"Total matches with at least one None team: {none_count}")
print(f"Of those, how many have a completed score (real problem): {real_issue_count}")

if completed_with_none:
    print("\n⚠️ These are real problems — completed matches with missing team data:")
    for m in completed_with_none:
        print(f"  {m.get('homeTeam')} vs {m.get('awayTeam')} | stage={m.get('stage')}")
else:
    print("\n✅ All None-team matches are future/unscheduled fixtures (TBD placeholders).")
    print("   This is expected — knockout stage slots not yet determined.")
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
API_KEY = os.getenv('FOOTBALL_API_KEY')
HEADERS = {"X-Auth-Token": API_KEY}

response = requests.get(
    "https://api.football-data.org/v4/competitions/WC/matches",
    headers=HEADERS
)

print(f"Status: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    
    # Find most recent match with a score
    completed = [m for m in matches if m.get('score', {}).get('fullTime', {}).get('home') is not None]
    completed.sort(key=lambda x: x['utcDate'], reverse=True)
    
    print(f"\nTotal matches in API response: {len(matches)}")
    print(f"Completed matches per API: {len(completed)}")
    print(f"\nMost recent 5 completed matches per API:")
    for m in completed[:5]:
        home = m['homeTeam']['name']
        away = m['awayTeam']['name']
        hs = m['score']['fullTime']['home']
        as_ = m['score']['fullTime']['away']
        date = m['utcDate']
        print(f"  {home} {hs}-{as_} {away} | {date}")
    
    # Check specifically for England vs Croatia
    eng_cro = [m for m in matches if 
               ('England' in m['homeTeam']['name'] or 'England' in m['awayTeam']['name']) and
               ('Croatia' in m['homeTeam']['name'] or 'Croatia' in m['awayTeam']['name'])]
    
    print(f"\n🔍 England vs Croatia match found in API: {len(eng_cro) > 0}")
    if eng_cro:
        m = eng_cro[0]
        print(f"   Status: {m.get('status')}")
        print(f"   Score: {m.get('score')}")
        print(f"   Date: {m.get('utcDate')}")
else:
    print(f"Error: {response.text}")
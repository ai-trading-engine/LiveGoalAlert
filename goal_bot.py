import requests
import time

BOT_TOKEN = "8453055906:AAHiSGL5GgVvZOakbxeZVMdWcoFqAor5vWQ"
CHAT_ID = "5523976168"
API_KEY = "b65a354d40eead8407927b4b414fa98a"

sent_goals = set()

def send_telegram(msg):
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url,data={
        "chat_id": CHAT_ID,
        "text": msg
    })


def check_matches():

    url = "https://v3.football.api-sports.io/fixtures?live=all"

    headers = {
        "x-apisports-key": API_KEY
    }

    r = requests.get(url,headers=headers).json()

    matches = r["response"]

    for match in matches:

        fixture = match["fixture"]["id"]

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        home_goals = match["goals"]["home"]
        away_goals = match["goals"]["away"]

        score = f"{home_goals}-{away_goals}"

        key = f"{fixture}-{score}"

        if key not in sent_goals:

            msg = f"""
⚽ GOAL ALERT

{home} {home_goals} - {away_goals} {away}

League: {match['league']['name']}
Minute: {match['fixture']['status']['elapsed']}'
"""

            send_telegram(msg)

            sent_goals.add(key)



while True:

    check_matches()

    time.sleep(15)

import requests
import firebase_admin
from firebase_admin import credentials, firestore
from telegram.ext import Application, CommandHandler
import asyncio

TOKEN = "8453055906:AAHiSGL5GgVvZOakbxeZVMdWcoFqAor5vWQ"
API_KEY = "b65a354d40eead8407927b4b414fa98a"

# initialize firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# LEAGUES WE WANT
LEAGUES = [
"Premier League",
"La Liga",
"Serie A",
"UEFA Champions League"
]

# save user when /start is used
async def start(update, context):

    chat_id = update.effective_chat.id

    db.collection("users").document(str(chat_id)).set({
        "chat_id": chat_id
    })

    await update.message.reply_text(
        "✅ You will now receive live goal alerts!"
    )

# send alerts to all users
def broadcast(message):

    users = db.collection("users").stream()

    for user in users:

        chat_id = user.to_dict()["chat_id"]

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": message
            }
        )

# store previous scores
last_scores = {}

def check_goals():

    url = "https://v3.football.api-sports.io/fixtures?live=all"

    headers = {
        "x-apisports-key": API_KEY
    }

    r = requests.get(url, headers=headers).json()

    matches = r["response"]

    for match in matches:

        league = match["league"]["name"]

        # filter leagues
        if league not in LEAGUES:
            continue

        fixture_id = match["fixture"]["id"]

        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        home_goals = match["goals"]["home"]
        away_goals = match["goals"]["away"]

        score = f"{home_goals}-{away_goals}"

        key = f"{fixture_id}-{score}"

        if key not in last_scores:

            last_scores[key] = True

            minute = match["fixture"]["status"]["elapsed"]

            message = f"""
⚽ GOAL ALERT

{home} {home_goals} - {away_goals} {away}

League: {league}
Minute: {minute}'
"""

            broadcast(message)

async def goal_loop():

    while True:

        check_goals()

        await asyncio.sleep(10)

async def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    asyncio.create_task(goal_loop())

    await app.run_polling()

asyncio.run(main())
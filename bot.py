import json
import os
import requests
from datetime import datetime, timezone

FEED_URL = "https://oddspredict.pages.dev/data/predictions.json"
POSTED_FILE = "data/posted.json"

DISCLAIMER = (
    "\n\n18+. Model estimates only. Not betting advice. "
    "Gamble responsibly. oddspredict.pages.dev"
)


def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return []


def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(posted, f, indent=2)


def fetch_todays_pick():
    try:
        r = requests.get(FEED_URL, timeout=30)
        r.raise_for_status()
        feed = r.json()
    except Exception as e:
        print(f"Failed to fetch feed: {e}")
        return None

    if not feed.get("available"):
        print("Feed marked unavailable.")
        return None

    predictions = feed.get("predictions", [])
    if not predictions:
        print("No predictions in feed.")
        return None

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    todays = [
        p for p in predictions
        if p.get("kickoff_utc", "").startswith(today)
    ]
    if not todays:
        print(f"No predictions for {today}.")
        return None

    todays.sort(key=lambda p: p.get("probability", 0), reverse=True)
    return todays[0]


def format_post(pick):
    line = f" {pick['line']}" if pick.get("line") else ""
    body = (
        f"🏆 {pick['league']}\n"
        f"⚽ {pick['home']} vs {pick['away']}\n"
        f"📊 {pick['market']}: {pick['selection']}{line}\n"
        f"📈 Model: {pick['probability']:.1f}% confidence"
    )
    return body + DISCLAIMER


def main():
    posted = load_posted()
    pick = fetch_todays_pick()
    if not pick:
        return

    key = f"{pick['home']}|{pick['away']}|{pick['market']}|{pick['selection']}"
    if key in posted:
        print("Already posted today.")
        return

    body = format_post(pick)
    print("--- WOULD POST ---")
    print(body)
    print("------------------")

    posted.append(key)
    save_posted(posted)


if __name__ == "__main__":
    main()
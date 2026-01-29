import feedparser
import requests
import os
import re
from datetime import datetime

# --------------------
# KONFIGURATION
# --------------------

RSS_FEEDS = {
    "Mjölby": "https://www.corren.se/rss/lokalt/mjolby",
    "Motala": "https://www.corren.se/rss/lokalt/motala",
    "Boxholm": "https://www.corren.se/rss/lokalt/boxholm",
    "Vadstena": "https://www.corren.se/rss/lokalt/vadstena",
}

LINK_PREFIX = "https://www.corren.se/naringsliv/nyetableringar/"

SEEN_FILE = "seen_guids.txt"

# Telegram
TELEGRAM_BOT_TOKEN = "BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "CHAT_ID_HERE"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# --------------------
# HJÄLPFUNKTIONER
# --------------------

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        for guid in sorted(seen):
            f.write(guid + "\n")

def extract_registration_sentence(text):
    """
    Försöker extrahera meningen som innehåller registreringen hos Bolagsverket
    """
    if not text:
        return ""

    # Ta bort HTML-taggar
    clean = re.sub("<[^<]+?>", "", text).strip()

    match = re.search(r"(Den .*?Bolagsverket\.)", clean)
    return match.group(1) if match else clean

def send_telegram_message(text):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": False,
    }
    r = requests.post(TELEGRAM_API_URL, json=payload, timeout=15)
    r.raise_for_status()

# --------------------
# MAIN
# --------------------

seen = load_seen()
new_items = []

for ort, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)

    for entry in feed.entries:
        guid = entry.get("guid", "")
        link = entry.get("link", "")

        if not link.startswith(LINK_PREFIX):
            continue

        if guid in seen:
            continue  # 🔒 absolut dublettspärr

        description = entry.get("description", "") or entry.get("summary", "")
        registration_text = extract_registration_sentence(description)

        try:
            published_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
        except Exception:
            published_date = ""

        new_items.append({
            "guid": guid,
            "ort": ort,
            "title": entry.get("title", ""),
            "registration": registration_text,
            "link": link,
            "date": published_date,
        })

# --------------------
# SKICKA TELEGRAM
# --------------------

if not new_items:
    print("Inga nya nyetableringar hittades.")
    exit(0)

for item in new_items:
    message = (
        f"Nyetablering\n\n"
        f"Ort: {item['ort']}\n"
        f"Titel: {item['title']}\n\n"
        f"{item['registration']}\n\n"
        f"{item['link']}"
    )

    send_telegram_message(message)
    seen.add(item["guid"])

save_seen(seen)

print(f"Skickade {len(new_items)} nya nyetableringar till Telegram.")

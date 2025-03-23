import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from sqlalchemy import create_engine
import os

# ✅ Haal de database URL uit de Railway omgeving
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///events.db")

engine = create_engine(DATABASE_URL)

URLS = [
    "https://danswebsite1.com/agenda",
    "https://danswebsite2.com/evenementen"
]

def fetch_html(url):
    """Haalt de HTML op van een opgegeven URL."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"⚠️ Fout bij ophalen van {url}: Status {response.status_code}")
        return None

def extract_events(html, url):
    """Zoekt automatisch naar evenementgegevens in de HTML."""
    soup = BeautifulSoup(html, "html.parser")
    events = []

    for event in soup.find_all(["div", "article"], class_=lambda x: x and "event" in x.lower()):
        naam = event.find(["h2", "h3"])
        datum = event.find(["time", "span"], class_=lambda x: x and "date" in x.lower())
        locatie = event.find(["span", "p"], class_=lambda x: x and "location" in x.lower())

        event_data = {
            "naam": naam.text.strip() if naam else "Onbekend",
            "datum": datum.text.strip() if datum else "Onbekend",
            "locatie": locatie.text.strip() if locatie else "Onbekend",
            "url": url
        }
        events.append(event_data)

    return events

def save_to_database(events):
    """Slaat evenementen op in de database."""
    if events:
        df = pd.DataFrame(events)
        df.to_sql("events", engine, if_exists="append", index=False)
        print("✅ Evenementen opgeslagen in database!")
    else:
        print("⚠️ Geen nieuwe evenementen gevonden.")

def scrape_and_store():
    """Doorloopt alle URLs en verzamelt + slaat evenementen op."""
    all_events = []

    for url in URLS:
        print(f"🔍 Scraping {url}...")
        html = fetch_html(url)
        if html:
            events = extract_events(html, url)
            all_events.extend(events)

    save_to_database(all_events)

# ✅ Stel automatische scraping in (elke 6 uur)
schedule.every(6).hours.do(scrape_and_store)

print("🔄 Scraper gestart...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Wacht 1 minuut voor de volgende check

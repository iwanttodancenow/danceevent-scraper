import requests
from bs4 import BeautifulSoup

# 🔹 Lijst met websites die je wilt scrapen
URLS = [
    "https://www.eventbrite.de/d/germany/kizomba/",
    "https://www.latinworld.nl/kizomba/agenda/"
]

def scrape_urls():
    scraped_data = []
    
    for url in URLS:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 🔹 Zoek naar evenement-links (afhankelijk van de website)
            event_links = soup.find_all('a', class_='event-link')
            
            for link in event_links:
                scraped_data.append(link.get('href'))
    
    return scraped_data

# 🔹 Test de scraper
scraped_events = scrape_urls()
print("Gevonden evenementen:", scraped_events)

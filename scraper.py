import json
import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE = "https://sharkstreams.net"

CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]

headers = {"User-Agent": "Mozilla/5.0"}


def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        streams = []

        def handle_response(response):
            if ".m3u8" in response.url:
                streams.append(response.url)

        page.on("response", handle_response)

        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(8000)
        except:
            pass

        browser.close()

        return streams[0] if streams else None


def parse_category(cat):
    url = f"{BASE}/category/{cat}"
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    rows = soup.select(".row")

    for row in rows:
        try:
            name = row.select_one(".ch-name").text.strip()
            date = row.select_one(".ch-date").text.strip()

            onclick = row.select_one("a.hd-link")["onclick"]
            channel_id = onclick.split("channel=")[1].split("'")[0]

            stream = get_stream(channel_id)

            results.append({
                "title": name,
                "date": date,
                "channel": channel_id,
                "player": f"{BASE}/player.php?channel={channel_id}",
                "stream": stream
            })

        except:
            continue

    return results


all_data = {}

for c in CATEGORIES:
    print(f"Parsing {c}")
    all_data[c] = parse_category(c)

with open("output.json", "w") as f:
    json.dump(all_data, f, indent=2)

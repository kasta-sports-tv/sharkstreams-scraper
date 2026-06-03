import json
import re
from playwright.sync_api import sync_playwright

BASE = "https://sharkstreams.net"
CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]


def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)

            html = page.content()

            matches = re.findall(r"https?://[^\"']+\.m3u8[^\"']*", html)

            browser.close()

            if matches:
                return matches[0]

    except Exception as e:
        print(f"[ERROR] {channel_id}: {e}")

    return None


def parse_category(cat):
    url = f"{BASE}/category/{cat}"

    import requests
    from bs4 import BeautifulSoup

    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    for row in soup.select(".row"):
        try:
            title = row.select_one(".ch-name").text.strip()
            onclick = row.select_one("a.hd-link")["onclick"]

            channel_id = onclick.split("channel=")[1].split("'")[0]

            stream = get_stream(channel_id)

            results.append({
                "title": title,
                "channel": channel_id,
                "stream": stream
            })

        except:
            continue

    return results


all_data = {}

for c in CATEGORIES:
    print(f"[INFO] {c}")
    all_data[c] = parse_category(c)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print("DONE JSON")

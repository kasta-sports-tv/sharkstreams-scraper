import json
import time
from playwright.sync_api import sync_playwright

BASE = "https://roxiestreams.info/"
CATEGORIES = ["soccer", "mlb", "nba", "nfl", "nhl", "fighting", "motorsports"]


def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    stream_url = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def handle_response(response):
                nonlocal stream_url
                if ".m3u8" in response.url:
                    stream_url = response.url

            page.on("response", handle_response)

            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            browser.close()

            return stream_url

    except Exception as e:
        print("[ERROR]", channel_id, e)

    return None


def parse_category(cat):
    import requests
    from bs4 import BeautifulSoup

    url = f"{BASE}/category/{cat}"
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
    print("[INFO]", c)
    all_data[c] = parse_category(c)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print("DONE JSON")

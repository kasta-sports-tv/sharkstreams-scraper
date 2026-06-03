import requests
from bs4 import BeautifulSoup
import json
import re

BASE = "https://sharkstreams.net"

CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 🔥 покращений витяг stream
def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text

        # 1. прямий пошук m3u8
        matches = re.findall(r"https?://[^\"]+\.m3u8[^\"]*", html)
        if matches:
            return matches[0]

        # 2. пошук у JS/рядках
        matches = re.findall(r"['\"](https?://[^'\"]+\.m3u8[^'\"]*)['\"]", html)
        if matches:
            return matches[0]

    except:
        return None

    return None


def parse_category(cat):
    url = f"{BASE}/category/{cat}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return []

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
    print(f"Parsing {c}...")
    all_data[c] = parse_category(c)

with open("output.json", "w") as f:
    json.dump(all_data, f, indent=2)

print("Done")

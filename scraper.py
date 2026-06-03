import requests
from bs4 import BeautifulSoup
import re
import json
import time

BASE = "https://sharkstreams.net"
CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]

headers = {"User-Agent": "Mozilla/5.0"}


def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text

        matches = re.findall(r"https?://[^\"']+\.m3u8[^\"']*", html)
        if matches:
            return matches[0]

    except:
        pass

    return None


def parse_category(cat):
    url = f"{BASE}/category/{cat}"
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select(".row")
    results = []

    for row in rows:
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

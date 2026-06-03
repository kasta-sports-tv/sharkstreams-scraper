import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz
import json
import time

BASE = "https://sharkstreams.net"

CATEGORIES = [
    "boxing","cfl","mlb","mma","motorsports","nba",
    "ncaaf","nfl","nhl","soccer","tennis","ufc","ufl","wnba","wwe"
]

kyiv = pytz.timezone("Europe/Kyiv")


def get_html(url):
    r = requests.get(url, timeout=15)
    return r.text


def parse_category(cat):
    url = f"{BASE}/category/{cat}"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select(".row")
    matches = []

    for r in rows:
        link = r.find("a", onclick=True)
        if not link:
            continue

        onclick = link["onclick"]

        m = re.search(r"channel=(\d+)", onclick)
        if not m:
            continue

        channel = m.group(1)

        title = r.select_one(".ch-name")
        time_el = r.select_one(".ch-date")
        cat_el = r.select_one(".ch-category")

        matches.append({
            "channel": channel,
            "title": title.text.strip() if title else None,
            "time": time_el.text.strip() if time_el else None,
            "category": cat.upper()
        })

    return matches


def build():
    all_matches = []

    for cat in CATEGORIES:
        try:
            data = parse_category(cat)
            all_matches.extend(data)
            time.sleep(0.5)  # щоб не банило
        except Exception as e:
            print("error:", cat, e)

    output = {
        "playlist_info": {
            "name": "SharkStreams AUTO ALL",
            "last_update": datetime.now(kyiv).strftime("%Y-%m-%d %H:%M:%S")
        },
        "live_matches": all_matches,
        "total": len(all_matches)
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    build()

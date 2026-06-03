import requests
from bs4 import BeautifulSoup
import re

BASE = "https://sharkstreams.net"

CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]

headers = {"User-Agent": "Mozilla/5.0"}


# ---------- STREAM ----------
def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text

        matches = re.findall(r"https?://[^\"]+\.m3u8[^\"]*", html)
        if matches:
            return matches[0]

        matches = re.findall(r"['\"](https?://[^'\"]+\.m3u8[^'\"]*)['\"]", html)
        if matches:
            return matches[0]

    except:
        return None

    return None


# ---------- CATEGORY ----------
def parse_category(cat):
    url = f"{BASE}/category/{cat}"
    r = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    streams = []

    rows = soup.select(".row")

    for row in rows:
        try:
            title = row.select_one(".ch-name").text.strip()

            onclick = row.select_one("a.hd-link")["onclick"]
            channel_id = onclick.split("channel=")[1].split("'")[0]

            stream = get_stream(channel_id)

            if stream:
                streams.append({
                    "title": title,
                    "url": stream
                })

        except:
            continue

    return streams


# ---------- BUILD M3U ----------
def build_m3u(all_streams):
    lines = ["#EXTM3U"]

    for cat, items in all_streams.items():
        for item in items:
            title = item["title"]
            url = item["url"]

            lines.append(f'#EXTINF:-1 group-title="{cat.upper()}",{title}')
            lines.append(url)

    return "\n".join(lines)


# ---------- MAIN ----------
all_streams = {}

for c in CATEGORIES:
    print(f"Parsing {c}...")
    all_streams[c] = parse_category(c)

m3u_content = build_m3u(all_streams)

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("M3U generated")

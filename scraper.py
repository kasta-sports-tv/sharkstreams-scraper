import requests
from bs4 import BeautifulSoup
import re
import time

BASE = "https://sharkstreams.net"

CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]

headers = {
    "User-Agent": "Mozilla/5.0"
}


# ---------- STREAM (SAFE + RETRY) ----------
def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    for _ in range(2):  # retry 2 рази
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
            time.sleep(1)

    return None


# ---------- CATEGORY ----------
def parse_category(cat):
    url = f"{BASE}/category/{cat}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return []

    streams = []
    rows = soup.select(".row")

    for row in rows:
        try:
            title = row.select_one(".ch-name").text.strip()

            onclick = row.select_one("a.hd-link")["onclick"]
            channel_id = onclick.split("channel=")[1].split("'")[0]

            stream = get_stream(channel_id)

            # ⚠️ НЕ пропускаємо матч повністю — тільки якщо є стрім
            if stream:
                streams.append({
                    "title": title,
                    "url": stream
                })

        except:
            continue

    return streams


# ---------- M3U BUILDER (SAFE) ----------
def build_m3u(all_streams):
    lines = ["#EXTM3U"]

    total = 0

    for cat, items in all_streams.items():
        for item in items:
            title = item.get("title", "Unknown")
            url = item.get("url")

            if not url:
                continue

            lines.append(f'#EXTINF:-1 group-title="{cat.upper()}",{title}')
            lines.append(url)
            total += 1

    print(f"[INFO] Total streams in M3U: {total}")

    return "\n".join(lines)


# ---------- MAIN ----------
all_streams = {}

for c in CATEGORIES:
    print(f"[INFO] Parsing {c}...")
    all_streams[c] = parse_category(c)

m3u_content = build_m3u(all_streams)

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("[DONE] M3U generated")

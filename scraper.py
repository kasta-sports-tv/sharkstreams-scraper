import requests
from bs4 import BeautifulSoup
import re
import json
import time

BASE = "https://sharkstreams.net"
CATEGORIES = ["mlb", "nba", "soccer", "nhl", "nfl"]

headers = {
    "User-Agent": "Mozilla/5.0"
}


# ---------- STREAM ----------
def get_stream(channel_id):
    url = f"{BASE}/player.php?channel={channel_id}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text

        # 1) прямий m3u8
        matches = re.findall(r"https?://[^\"']+\.m3u8[^\"']*", html)
        if matches:
            return matches[0]

        # 2) iframe пошук (ВАЖЛИВО)
        iframe = re.search(r'<iframe[^>]+src=["\'](.*?)["\']', html)
        if iframe:
            iframe_url = iframe.group(1)

            if iframe_url.startswith("/"):
                iframe_url = BASE + iframe_url

            try:
                r2 = requests.get(iframe_url, headers=headers, timeout=15)
                html2 = r2.text

                matches2 = re.findall(r"https?://[^\"']+\.m3u8[^\"']*", html2)
                if matches2:
                    return matches2[0]

            except:
                pass

    except Exception as e:
        print(f"[ERROR] channel {channel_id}: {e}")

    return None


# ---------- CATEGORY ----------
def parse_category(cat):
    url = f"{BASE}/category/{cat}"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return []

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


# ---------- MAIN ----------
all_data = {}

for c in CATEGORIES:
    print(f"[INFO] Parsing {c}")
    all_data[c] = parse_category(c)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print("[DONE] output.json updated")

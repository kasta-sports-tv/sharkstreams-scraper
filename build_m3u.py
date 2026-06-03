import json

with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

lines = ["#EXTM3U"]

total = 0

for cat, items in data.items():
    for item in items:
        stream = item.get("stream")

        if not stream:
            continue

        title = item.get("title", "Unknown")

        lines.append(f'#EXTINF:-1 group-title="{cat.upper()}",{title}')
        lines.append(stream)

        total += 1

print("TOTAL:", total)

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("M3U DONE")

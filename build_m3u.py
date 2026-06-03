import json

with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

lines = ["#EXTM3U"]

total = 0
skipped = 0

for cat, items in data.items():
    for item in items:

        stream = item.get("stream")

        # 🔥 жорсткий захист від сміття
        if not stream or not isinstance(stream, str) or "http" not in stream:
            skipped += 1
            continue

        title = item.get("title") or "Unknown"

        print(f"[OK] {cat} -> {title}")

        lines.append(f'#EXTINF:-1 group-title="{cat.upper()}",{title}')
        lines.append(stream)

        total += 1


print("================================")
print("TOTAL STREAMS:", total)
print("SKIPPED:", skipped)
print("================================")

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("[DONE] M3U GENERATED")

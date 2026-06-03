import json

data = {
    "test": "ok"
}

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

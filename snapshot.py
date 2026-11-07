import json, pathlib, datetime
root = pathlib.Path(__file__).parent
data = json.loads((root/"data/apps.json").read_text())
today = datetime.date.today().isoformat()
out = root/"data/history"/f"{today}.json"
out.parent.mkdir(parents=True, exist_ok=True)
if out.exists():
    print("snapshot exists:", out.name)
else:
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("snapshot written:", out.name, "apps:", len(data["apps"]))

"""Snapshot paginated Core league discovery without changing scheduled ingestion scope."""

import ast
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    tree = ast.parse((ROOT / "espn_service/clients/espn_client.py").read_text(encoding="utf-8"))
    sports = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.AnnAssign) and n.target.id == "SPORT_NAMES")
    snapshot = {"checked_at": datetime.now(timezone.utc).isoformat(), "sports": {}}
    for sport in sports:
        items = []
        page = 1
        while True:
            url = f"https://sports.core.api.espn.com/v2/sports/{sport}/leagues?limit=1000&page={page}"
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.load(response)
            items.extend(data.get("items", []))
            if page >= data.get("pageCount", 1):
                break
            page += 1
        snapshot["sports"][sport] = {"count": data.get("count"), "items": items}
        print(sport, len(items), flush=True)
    out = ROOT / "docs/data/leagues.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

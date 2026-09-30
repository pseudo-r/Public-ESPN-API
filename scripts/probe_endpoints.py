"""Read-only probes of documented and candidate routes; save status and shape, not bodies."""

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://site.api.espn.com/apis/"
WEB = "https://site.web.api.espn.com/apis/"
PROBES = [
    SITE + "site/v2/sports/football/nfl/" + path
    for path in ("scoreboard", "teams", "injuries", "transactions", "groups", "calendar",
                 "teams/12/schedule", "teams/12/depthcharts", "teams/12/injuries",
                 "athletes/3139477", "athletes/3139477/gamelog")
]
# Keep explicit URLs to make the sample reproducible.
PROBES += [SITE + "v2/sports/football/nfl/standings", SITE + "site/v3/sports/football/nfl/scoreboard"]
PROBES += [WEB + "common/v3/sports/football/nfl/athletes/3139477/" + path
           for path in ("overview", "stats", "gamelog", "splits", "bio")]
PROBES += [
    WEB + "common/v3/sports/football/nfl/statistics/byathlete?limit=1",
    SITE + "personalized/v2/scoreboard/header?sport=cricket&region=in",
    "https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?limit=1",
    "https://sports.core.api.espn.com/v3/sports/football/leagues/nfl/athletes?limit=1",
    "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/providers?limit=100",
]

CORE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/"
EVENT = CORE + "events/401772988"
PROBES += [EVENT, EVENT + "/competitions/401772988"]
PROBES += [EVENT + "/competitions/401772988/" + path for path in (
    "status", "drives?limit=1", "competitors/17/roster?limit=1",
    "competitors/17/statistics", "competitors/17/linescores",
)]
PROBES += [CORE + path for path in (
    "calendar", "seasons/2026/types", "seasons/2026/types/2/weeks",
    "athletes/3139477/eventlog", "athletes/3139477/statisticslog",
)]
PROBES += [WEB + "search/v2?query=Patrick%20Mahomes&limit=1"]
PROBES += [SITE + f"site/v2/sports/{sport}/{league}/{resource}"
           for sport, league in (("basketball", "nba"), ("baseball", "mlb"),
                                  ("hockey", "nhl"), ("soccer", "eng.1"),
                                  ("football", "college-football"))
           for resource in ("teams", "scoreboard", "news?limit=1")]


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=25) as response:
            data = json.load(response)
            return {"url": url, "status": response.status,
                    "keys": sorted(data) if isinstance(data, dict) else [],
                    "empty": not bool(data)}
    except urllib.error.HTTPError as exc:
        return {"url": url, "status": exc.code}
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return {"url": url, "error": str(exc)}


def main():
    results = []
    for url in PROBES:
        result = fetch(url)
        results.append(result)
        print(result, flush=True)
    output = ROOT / "docs" / "data" / "live-probes.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
                                  "results": results}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

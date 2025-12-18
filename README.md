# ESPN Public API Documentation

> **Disclaimer:** This is documentation for ESPN's undocumented public API. I am not affiliated with ESPN. Use responsibly and follow ESPN's terms of service.

## Table of Contents

- [Overview](#overview)
- [Base URLs](#base-urls)
- [Quick Start](#quick-start)
- [Sports Endpoints](#sports-endpoints)
- [Fantasy Sports API](#fantasy-sports-api)
- [Betting & Odds](#betting--odds)
- [Advanced Endpoints](#advanced-endpoints)
- [Parameters Reference](#parameters-reference)
- [ESPN Service (Django Implementation)](#espn-service-django-implementation)

---

## Overview

ESPN provides undocumented APIs that power their website and mobile apps. These endpoints return JSON data for scores, teams, players, statistics, and more across all major sports.

### Important Notes

- **Unofficial:** These APIs are not officially supported and may change without notice
- **No Authentication Required:** Most endpoints are publicly accessible
- **Rate Limiting:** Be respectful - no official limits published, but excessive requests may be blocked
- **Best Practice:** Implement caching and error handling in your applications

---

## Base URLs

| Domain | Purpose |
|--------|---------|
| `site.api.espn.com` | Scores, news, teams, standings |
| `sports.core.api.espn.com` | Athletes, stats, odds, detailed data |
| `site.web.api.espn.com` | Search, athlete profiles |
| `cdn.espn.com` | CDN-optimized live data |
| `fantasy.espn.com` | Fantasy sports leagues |
| `now.core.api.espn.com` | Real-time news feeds |

---

## Quick Start

### Get NFL Scoreboard
```bash
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
```

### Get NBA Teams
```bash
curl "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
```

### Get MLB Scores for Specific Date
```bash
curl "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates=20241215"
```

---

## Sports Endpoints

### General Pattern
```
https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/{resource}
```

### NFL (National Football League)

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard` |
| Teams | `site.api.espn.com/apis/site/v2/sports/football/nfl/teams` |
| Team Detail | `site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{id}` |
| Team Roster | `site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{id}/roster` |
| Team Schedule | `site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{id}/schedule` |
| Standings | `site.api.espn.com/apis/site/v2/sports/football/nfl/standings` |
| News | `site.api.espn.com/apis/site/v2/sports/football/nfl/news` |
| Game Summary | `site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={id}` |
| Leaders | `site.api.espn.com/apis/site/v3/sports/football/nfl/leaders` |

**With Parameters:**
```bash
# Specific week
?dates=20241215&week=15&seasontype=2

# Team with roster enabled
/teams/12?enable=roster,stats
```

### NBA (National Basketball Association)

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard` |
| Teams | `site.api.espn.com/apis/site/v2/sports/basketball/nba/teams` |
| Team Detail | `site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{id}` |
| Standings | `site.api.espn.com/apis/site/v2/sports/basketball/nba/standings` |
| News | `site.api.espn.com/apis/site/v2/sports/basketball/nba/news` |
| Players | `site.api.espn.com/apis/site/v2/sports/basketball/nba/players` |

### MLB (Major League Baseball)

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard` |
| Teams | `site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams` |
| Standings | `site.api.espn.com/apis/site/v2/sports/baseball/mlb/standings` |
| News | `site.api.espn.com/apis/site/v2/sports/baseball/mlb/news` |

### NHL (National Hockey League)

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard` |
| Teams | `site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams` |
| Standings | `site.api.espn.com/apis/site/v2/sports/hockey/nhl/standings` |
| News | `site.api.espn.com/apis/site/v2/sports/hockey/nhl/news` |

### College Football

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard` |
| Rankings | `site.api.espn.com/apis/site/v2/sports/football/college-football/rankings` |
| Teams | `site.api.espn.com/apis/site/v2/sports/football/college-football/teams` |
| News | `site.api.espn.com/apis/site/v2/sports/football/college-football/news` |

**Conference Filtering (use `groups` parameter):**

| Conference | ID |
|------------|-----|
| SEC | 8 |
| Big Ten | 5 |
| ACC | 1 |
| Big 12 | 4 |
| Pac-12 | 9 |
| American (AAC) | 151 |
| Mountain West | 17 |
| MAC | 15 |
| Sun Belt | 37 |
| Top 25 | 80 |

```bash
# SEC games only
?groups=8
```

### College Basketball

| Endpoint | URL |
|----------|-----|
| Men's Scoreboard | `site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard` |
| Men's Rankings | `site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/rankings` |
| Women's Scoreboard | `site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard` |

### WNBA

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard` |
| Teams | `site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams` |

### Soccer

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard` |
| Teams | `site.api.espn.com/apis/site/v2/sports/soccer/{league}/teams` |
| Standings | `site.api.espn.com/apis/site/v2/sports/soccer/{league}/standings` |

**Soccer League Codes:**

| League | Code |
|--------|------|
| Premier League | `eng.1` |
| Championship | `eng.2` |
| La Liga | `esp.1` |
| Bundesliga | `ger.1` |
| Serie A | `ita.1` |
| Ligue 1 | `fra.1` |
| MLS | `usa.1` |
| NWSL | `usa.nwsl` |
| Champions League | `uefa.champions` |
| Europa League | `uefa.europa` |
| World Cup | `fifa.world` |
| Liga MX | `mex.1` |
| Eredivisie | `ned.1` |
| Primeira Liga | `por.1` |
| Scottish Premiership | `sco.1` |
| Brasileirão | `bra.1` |
| Copa Libertadores | `conmebol.libertadores` |

### UFC / MMA

| Endpoint | URL |
|----------|-----|
| Scoreboard | `site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard` |
| Rankings | `site.api.espn.com/apis/site/v2/sports/mma/ufc/rankings` |
| Athletes | `site.api.espn.com/apis/site/v2/sports/mma/ufc/athletes` |
| News | `site.api.espn.com/apis/site/v2/sports/mma/ufc/news` |

### Golf

| Endpoint | URL |
|----------|-----|
| PGA Scoreboard | `site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard` |
| PGA Leaderboard | `site.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard` |
| LPGA Scoreboard | `site.api.espn.com/apis/site/v2/sports/golf/lpga/scoreboard` |

**Golf Tours:** `pga`, `lpga`, `eur`, `champions-tour`

### Racing

| Endpoint | URL |
|----------|-----|
| F1 Scoreboard | `site.api.espn.com/apis/site/v2/sports/racing/f1/scoreboard` |
| F1 Standings | `site.api.espn.com/apis/site/v2/sports/racing/f1/standings` |
| NASCAR Cup | `site.api.espn.com/apis/site/v2/sports/racing/nascar-premier/scoreboard` |
| IndyCar | `site.api.espn.com/apis/site/v2/sports/racing/irl/scoreboard` |

### Tennis

| Endpoint | URL |
|----------|-----|
| ATP Scoreboard | `site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard` |
| WTA Scoreboard | `site.api.espn.com/apis/site/v2/sports/tennis/wta/scoreboard` |
| Rankings | `site.api.espn.com/apis/site/v2/sports/tennis/atp/rankings` |

### Other Sports

| Sport | League Code |
|-------|-------------|
| Rugby | `rugby/rugby-union` |
| Cricket | `cricket` |
| Lacrosse (PLL) | `lacrosse/pll` |
| Boxing | `boxing` |

---

## Fantasy Sports API

Base URL: `https://fantasy.espn.com/apis/v3/games/{sport}/seasons/{year}`

### Game Codes

| Sport | Code |
|-------|------|
| Football | `ffl` |
| Basketball | `fba` |
| Baseball | `flb` |
| Hockey | `fhl` |

### League Endpoints

```bash
# Get league data (public leagues)
GET /apis/v3/games/ffl/seasons/2024/segments/0/leagues/{league_id}

# With views
?view=mTeam
?view=mRoster
?view=mMatchup
?view=mSettings
?view=mDraftDetail
```

### Authentication (Private Leagues)

Private leagues require cookies: `espn_s2` and `SWID`

### X-Fantasy-Filter Header

For filtering player data:
```json
{
  "players": {
    "filterSlotIds": {"value": [0,1,2]},
    "sortPercOwned": {"sortAsc": false, "sortPriority": 1},
    "limit": 50
  }
}
```

---

## Betting & Odds

Base: `sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}`

| Endpoint | Path |
|----------|------|
| Game Odds | `/events/{id}/competitions/{id}/odds` |
| Win Probabilities | `/events/{id}/competitions/{id}/probabilities` |
| Futures | `/seasons/{year}/futures` |
| ATS Records | `/seasons/{year}/types/{type}/teams/{id}/ats` |

**Betting Provider IDs:**

| Provider | ID |
|----------|-----|
| Caesars | 38 |
| Bet365 | 2000 |
| DraftKings | 41 |

---

## Advanced Endpoints

### Core API (Detailed Data)

Base: `sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}`

| Endpoint | Path |
|----------|------|
| Athletes | `/athletes?limit=1000` |
| Seasons | `/seasons` |
| Teams (Season) | `/seasons/{year}/teams` |
| Draft | `/seasons/{year}/draft` |
| Events | `/events?dates=2024` |
| Venues | `/venues?limit=500` |
| Franchises | `/franchises` |
| Positions | `/positions` |

### Athlete Endpoints

| Endpoint | URL |
|----------|-----|
| Overview | `site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/overview` |
| Game Log | `site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/gamelog` |
| Splits | `site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/splits` |
| Stats | `site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/stats` |

### CDN Endpoints (Fast/Live)

| Endpoint | URL |
|----------|-----|
| Scoreboard | `cdn.espn.com/core/{league}/scoreboard?xhr=1` |
| Boxscore | `cdn.espn.com/core/{league}/boxscore?xhr=1&gameId={id}` |
| Play-by-Play | `cdn.espn.com/core/{league}/playbyplay?xhr=1&gameId={id}` |
| Schedule | `cdn.espn.com/core/{league}/schedule?xhr=1` |
| Standings | `cdn.espn.com/core/{league}/standings?xhr=1` |

### Search

```bash
GET https://site.web.api.espn.com/apis/common/v3/search?query=mahomes&limit=10
```

---

## Parameters Reference

### Common Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `dates` | Filter by date | `20241215` or `20241201-20241231` |
| `week` | Week number | `1` through `18` |
| `seasontype` | Season type | `1`=preseason, `2`=regular, `3`=postseason |
| `season` | Year | `2024` |
| `limit` | Results limit | `100`, `1000` |
| `groups` | Conference ID | `8` (SEC) |
| `enable` | Include extra data | `roster,stats,projection` |
| `xhr` | CDN flag | `1` |

### Season Types

| Type | Value |
|------|-------|
| Preseason | 1 |
| Regular Season | 2 |
| Postseason | 3 |
| Off Season | 4 |

---

## ESPN Service (Django Implementation)

This repository includes a production-ready Django REST API that wraps ESPN's endpoints.

### Features

- Data ingestion and persistence
- Clean REST API with filtering
- Background jobs (Celery)
- Docker support
- OpenAPI documentation

### Quick Start

```bash
cd espn_service
docker compose up --build

# API: http://localhost:8000
# Docs: http://localhost:8000/api/docs/
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/api/v1/ingest/teams/` | POST | Ingest ESPN teams |
| `/api/v1/ingest/scoreboard/` | POST | Ingest ESPN events |
| `/api/v1/teams/` | GET | List teams |
| `/api/v1/teams/{id}/` | GET | Team details |
| `/api/v1/events/` | GET | List events |
| `/api/v1/events/{id}/` | GET | Event details |

### Example Usage

```bash
# Ingest NBA teams
curl -X POST http://localhost:8000/api/v1/ingest/teams/ \
  -H "Content-Type: application/json" \
  -d '{"sport": "basketball", "league": "nba"}'

# Query teams
curl "http://localhost:8000/api/v1/teams/?league=nba&search=Lakers"

# Query events
curl "http://localhost:8000/api/v1/events/?league=nba&date=2024-12-15"
```

See [espn_service/README.md](espn_service/README.md) for full documentation.

---

## Copy-Paste Examples

### Most Used Endpoints

```bash
# NFL
https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams
https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings

# NBA
https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard
https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams

# MLB
https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard
https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams

# NHL
https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard
https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams

# College Football
https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard
https://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings

# Soccer (Premier League)
https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard
https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/standings

# UFC
https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard
https://site.api.espn.com/apis/site/v2/sports/mma/ufc/rankings

# F1
https://site.api.espn.com/apis/site/v2/sports/racing/f1/scoreboard
https://site.api.espn.com/apis/site/v2/sports/racing/f1/standings
```

### Core API Examples

```bash
# All NFL athletes
https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?limit=1000&active=true

# Game odds
https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{eventId}/competitions/{eventId}/odds

# Play-by-play
https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{eventId}/competitions/{eventId}/plays?limit=400
```

### CDN (Live Data)

```bash
# Live scoreboard
https://cdn.espn.com/core/nfl/scoreboard?xhr=1

# Live boxscore
https://cdn.espn.com/core/nfl/boxscore?xhr=1&gameId={gameId}
```

---

## Contributing

Found a new endpoint? Please open an issue or PR!

## License

MIT License - See LICENSE file

---

*Last Updated: December 2024*

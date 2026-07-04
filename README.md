<!-- GitAds-Verify: 44FZ4IWPYGNOY6XFRMCK946T5LOIFT23 -->

# ESPN Public API Documentation

**Disclaimer:** This is documentation for ESPN's undocumented public API. I am not affiliated with ESPN. Use responsibly and follow ESPN's terms of service.

[![CI](https://github.com/pseudo-r/Public-ESPN-API/actions/workflows/ci.yml/badge.svg?branch=Public-Api)](https://github.com/pseudo-r/Public-ESPN-API/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/pseudo-r/Public-ESPN-API/branch/Public-Api/graph/badge.svg)](https://codecov.io/gh/pseudo-r/Public-ESPN-API)

---

## ☕ Support This Project

If this documentation has saved you time, consider supporting ongoing development and maintenance:

| Platform | Link |
|----------|------|
| ☕ Buy Me a Coffee | [buymeacoffee.com/pseudo_r](https://buymeacoffee.com/pseudo_r) |
| 💖 GitHub Sponsors | [github.com/sponsors/Kloverdevs](https://github.com/sponsors/Kloverdevs) |
| 💳 PayPal Donate | [PayPal (CAD)](https://www.paypal.com/donate/?business=H5VPFZ2EHVNBU&no_recurring=0&currency_code=CAD) |

Every contribution helps keep this project updated as ESPN changes their API.

---

## 📱 Real-World Apps Built With This API

These apps are live examples of what you can build using this documentation and the included Django service:

### 🏀 [Sportly: Basketball Live](https://play.google.com/store/apps/details?id=com.sportly.basketball)
> Real-time NBA, college basketball, and international leagues — scores, standings, player stats, and live game tracking.

[![Get it on Google Play](https://img.shields.io/badge/Google_Play-Sportly_Basketball-3DDC84?logo=google-play&logoColor=white)](https://play.google.com/store/apps/details?id=com.sportly.basketball)

### ⚽ [Sportly: Soccer Live](https://play.google.com/store/apps/details?id=com.sportly.soccer)
> Premier League, La Liga, Bundesliga, Serie A, MLS, and more — live scores, tables, fixtures, and news.

[![Get it on Google Play](https://img.shields.io/badge/Google_Play-Sportly_Soccer-3DDC84?logo=google-play&logoColor=white)](https://play.google.com/store/apps/details?id=com.sportly.soccer)

### 🏒 [Sportly: NHL & Hockey Live](https://play.google.com/store/apps/details?id=com.sportly.hockey)
> Live NHL scores, standings, game stats, and hockey data across leagues.

[![Get it on Google Play](https://img.shields.io/badge/Google_Play-Sportly_Hockey-3DDC84?logo=google-play&logoColor=white)](https://play.google.com/store/apps/details?id=com.sportly.hockey)

### 🏈 [Sportly: American Football Live](https://play.google.com/store/apps/details?id=com.sportly.football)
> NFL scores, standings, play-by-play, and college football coverage.

[![Get it on Google Play](https://img.shields.io/badge/Google_Play-Sportly_Football-3DDC84?logo=google-play&logoColor=white)](https://play.google.com/store/apps/details?id=com.sportly.football)

### ⚾ [Sportly: Baseball Live](https://play.google.com/store/apps/details?id=com.sportly.baseball)
> MLB scores, box scores, standings, and baseball stats.

[![Get it on Google Play](https://img.shields.io/badge/Google_Play-Sportly_Baseball-3DDC84?logo=google-play&logoColor=white)](https://play.google.com/store/apps/details?id=com.sportly.baseball)



## Table of Contents

- [Overview](#overview)
- [Base URLs](#base-urls)
- [Quick Start](#quick-start)
- [Sports Coverage](#sports-coverage)
- [API Endpoint Patterns](#api-endpoint-patterns)
    - [Site API v2](#site-api-v2-scores-teams-standings)
    - [Site API v3](#site-api-v3-richer-game-data)
    - [Core API v2](#core-api-v2-athletes-stats-events-odds)
    - [Core API v3](#core-api-v3-enriched-schema)
    - [Search & Web API](#search--web-api)
    - [CDN API](#cdn-api-real-time-optimized)
    - [Now API](#now-api-real-time-news)
- [Fantasy Sports API](#fantasy-sports-api)
- [Betting & Odds](#betting--odds)
- [Notable Specialized Endpoints](#notable-specialized-endpoints)
- [Parameters Reference](#parameters-reference)
- [ESPN Service (Django Implementation)](#espn-service-django-implementation)
- [Response Schemas](docs/response_schemas.md)
- [CHANGELOG](CHANGELOG.md)

---

## Overview

ESPN provides undocumented APIs that power their website and mobile apps. These endpoints return JSON data for scores, teams, players, statistics, and more across all major sports.

**Coverage:** 17 sports · 139 leagues · 370 v2 endpoints · 79 v3 endpoints  
*(Mapped from the ESPN WADL at `sports.core.api.espn.com/v2/application.wadl` and `sports.core.api.espn.com/v3/application.wadl`)*

**Additional domains documented:** `site.api.espn.com` (v2 + v3) · `site.web.api.espn.com` · `cdn.espn.com` · `now.core.api.espn.com` · `fantasy.espn.com`

### Important Notes

- **Unofficial:** These APIs are not officially supported and may change without notice
- **No Authentication Required:** Most endpoints are publicly accessible
- **Rate Limiting:** Be respectful — no official limits published, but excessive requests may be blocked
- **Best Practice:** Implement caching and error handling in your applications
- **`$ref` URLs with `.pvt` domain:** Some Core API responses contain `$ref` URLs pointing to `sports.core.api.espn.pvt` — this is ESPN's internal domain and is not publicly accessible. Replace `.pvt` with `.com` to get a working URL (e.g. `sports.core.api.espn.pvt/v2/...` → `sports.core.api.espn.com/v2/...`). See [#20](https://github.com/pseudo-r/Public-ESPN-API/issues/20).
- **Season dates may not match event availability:** The dates returned by the seasons/calendar endpoint (e.g. start/end of a soccer season) may not perfectly align with when scoreboard data is available. If the scoreboard returns empty for the reported start date, try a date range closer to when matches actually begin. See [#17](https://github.com/pseudo-r/Public-ESPN-API/issues/17).

---

## Base URLs

| Domain | Version | Purpose |
|--------|---------|---------|
| `site.api.espn.com` | v2/v3 | Scores, news, teams, standings (site-facing) |
| `sports.core.api.espn.com` | v2 | Athletes, stats, odds, play-by-play, detailed data |
| `sports.core.api.espn.com` | v3 | Athletes, leaders (richer schema) |
| `site.web.api.espn.com` | v3 | Search, athlete profiles |
| `cdn.espn.com` | — | CDN-optimized live data |
| `fantasy.espn.com` | v3 | Fantasy sports leagues |
| `now.core.api.espn.com` | — | Real-time news feeds |

---

## Quick Start

```bash
# NFL Scoreboard
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

# NBA Teams
curl "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"

# MLB Scores for a Specific Date
curl "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates=20241215"

# NHL Standings — NOTE: use /apis/v2/ (not /apis/site/v2/ which returns a stub)
curl "https://site.api.espn.com/apis/v2/sports/hockey/nhl/standings"
```

---

## Sports Coverage

Each sport has its own detailed endpoint reference document:

| Sport | Slug | # Leagues | Documentation |
|-------|------|-----------|---------------|
| 🏉 Australian Football | `australian-football` | 1 | [docs/sports/australian_football.md](docs/sports/australian_football.md) |
| ⚾ Baseball | `baseball` | 13 | [docs/sports/baseball.md](docs/sports/baseball.md) |
| 🏀 Basketball | `basketball` | 15 | [docs/sports/basketball.md](docs/sports/basketball.md) |
| 🏏 Cricket | `cricket` | varies | [docs/sports/cricket.md](docs/sports/cricket.md) |
| 🏑 Field Hockey | `field-hockey` | 1 | [docs/sports/field_hockey.md](docs/sports/field_hockey.md) |
| 🏈 Football | `football` | 5 | [docs/sports/football.md](docs/sports/football.md) |
| ⛳ Golf | `golf` | 9 | [docs/sports/golf.md](docs/sports/golf.md) |
| 🏒 Hockey | `hockey` | 6 | [docs/sports/hockey.md](docs/sports/hockey.md) |
| 🥍 Lacrosse | `lacrosse` | 4 | [docs/sports/lacrosse.md](docs/sports/lacrosse.md) |
| 🥊 MMA | `mma` | 25+ | [docs/sports/mma.md](docs/sports/mma.md) |
| 🏎️ Racing | `racing` | 5 | [docs/sports/racing.md](docs/sports/racing.md) |
| 🏉 Rugby | `rugby` | 24 | [docs/sports/rugby.md](docs/sports/rugby.md) |
| 🏉 Rugby League | `rugby-league` | 1 | [docs/sports/rugby_league.md](docs/sports/rugby_league.md) |
| ⚽ Soccer | `soccer` | 24 | [docs/sports/soccer.md](docs/sports/soccer.md) |
| 🎾 Tennis | `tennis` | 2 | [docs/sports/tennis.md](docs/sports/tennis.md) |
| 🏐 Volleyball | `volleyball` | 2 | [docs/sports/volleyball.md](docs/sports/volleyball.md) |
| 🤽 Water Polo | `water-polo` | 2 | [docs/sports/water_polo.md](docs/sports/water_polo.md) |

> For global and cross-sport endpoints, see [docs/sports/_global.md](docs/sports/_global.md).

---

## API Endpoint Patterns

### Site API v2 (Scores, Teams, Standings)

```
GET https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/{resource}
```

| Resource | Description |
|----------|-------------|
| `scoreboard` | Live & scheduled events with scores |
| `teams` | All teams in the league |
| `teams/{id}` | Single team detail |
| `teams/{id}/roster` | Team roster |
| `teams/{id}/schedule` | Team schedule |
| `teams/{id}/depthcharts` | Depth chart by position |
| `teams/{id}/injuries` | Current injury report |
| `teams/{id}/transactions` | Recent transactions/moves |
| `teams/{id}/history` | Franchise historical record |
| `athletes/{id}` | Individual athlete profile |
| `athletes/{id}/gamelog` | Game-by-game log |
| `athletes/{id}/splits` | Statistical splits |
| `athletes/{id}/news` | Athlete news |
| `athletes/{id}/bio` | Athlete bio |
| `standings` | League standings ⚠️ use `/apis/v2/` — `/apis/site/v2/` returns a stub |
| `injuries` | League-wide injury report |
| `transactions` | Recent signings/trades/waivers |
| `groups` | Conferences/divisions |
| `news` | Latest news articles |
| `rankings` | Rankings (college sports) |
| `calendar` | Season calendar (all weeks/dates) |
| `calendar/offseason` | Offseason date range |
| `calendar/regular-season` | Regular season weeks |
| `calendar/postseason` | Postseason date ranges |
| `summary?event={id}` | Full game summary |

### Site API v3 (Richer Game Data)

```
GET https://site.api.espn.com/apis/site/v3/sports/{sport}/{league}/{resource}
```

| Resource | Description |
|----------|-------------|
| `scoreboard` | Scoreboard with enriched v3 schema |
| `summary?event={id}` | Enriched game summary (v3 schema) |

### Core API v2 (Athletes, Stats, Events, Odds)

```
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/{resource}
```

| Resource | Description |
|----------|-------------|
| `athletes` | Full athlete list with pagination |
| `athletes/{id}` | Single athlete |
| `athletes/{id}/statistics` | Career stats |
| `athletes/{id}/statisticslog` | Game-by-game log |
| `athletes/{id}/eventlog` | Event history |
| `athletes/{id}/contracts` | Contract info |
| `athletes/{id}/awards` | Awards |
| `athletes/{id}/seasons` | Seasons played |
| `athletes/{id}/records` | Career records |
| `athletes/{id}/hotzones` | Hot zones (baseball) |
| `athletes/{id}/injuries` | Athlete injury history |
| `athletes/{id}/vsathlete/{opponentId}` | Head-to-head stats |
| `events` | Events with full detail |
| `events/{id}/competitions/{id}/odds` | Betting odds |
| `events/{id}/competitions/{id}/probabilities` | Win probabilities |
| `events/{id}/competitions/{id}/plays` | Play-by-play |
| `events/{id}/competitions/{id}/situation` | Current game situation (down/distance/ball) |
| `events/{id}/competitions/{id}/broadcasts` | Broadcast network info |
| `events/{id}/competitions/{id}/predictor` | ESPN game predictor |
| `events/{id}/competitions/{id}/powerindex` | ESPN Power Index for game |
| `events/{id}/competitions/{id}/competitors/{id}/linescores` | Period-by-period scores |
| `events/{id}/competitions/{id}/competitors/{id}/statistics` | Competitor stats |
| `seasons` | Season list |
| `seasons/{year}/teams` | Teams in a season |
| `seasons/{year}/coaches` | Coaching staff |
| `seasons/{year}/draft` | Draft data |
| `seasons/{year}/futures` | Futures odds |
| `seasons/{year}/powerindex` | Season-level Power Index / BPI |
| `seasons/{year}/types/{type}/groups/{group}/qbr/{split}` | ESPN QBR (football) |
| `standings` | League standings |
| `teams` | Teams (detailed) |
| `venues` | Venues/stadiums |
| `leaders` | Statistical leaders |
| `rankings` | Rankings |
| `franchises` | Franchise history |
| `coaches/{id}` | Individual coach profile |
| `coaches/{id}/record/{type}` | Coaching record by type |

### Core API v3 (Enriched Schema)

```
GET https://sports.core.api.espn.com/v3/sports/{sport}/{league}/{resource}
```

| Resource | Description |
|----------|-------------|
| `athletes` | Athletes (enriched schema) |
| `athletes/{id}` | Single athlete (enriched) |
| `athletes/{id}/statisticslog` | Game log (enriched) |
| `athletes/{id}/plays` | Athlete play history |
| `leaders` | Statistical leaders |

### Search & Web API

```
GET https://site.web.api.espn.com/apis/{path}
```

| Endpoint | Description |
|----------|-------------|
| `/search/v2?query={q}&limit={n}` | Global ESPN search |
| `/search/v2?query={q}&sport={sport}` | Sport-scoped search |
| `/v2/scoreboard/header` | Scoreboard header/nav state |
| `/apis/personalized/v2/scoreboard/header?sport={sport}&region={region}&tz={tz}` | Personalized multi-sport header. Returns `sports[].leagues[]` (each an active series/competition with numeric `id`, `name`, `isTournament`, `events[]`) — ideal for **cricket series discovery** |
| `/apis/site/v2/sports/golf/{tour}/leaderboard/{eventId}/playersummary?season={year}&player={id}` | Golf hole-by-hole player scoring (`rounds[].linescores[]` = per-hole strokes/par/scoreType) |
| `/apis/site/v2/sports/cricket/{leagueId}/summary?event={id}&lang=en&region=in` | Cricket match summary/scorecard (web API, numeric `leagueId` from the personalized header) |
| `/apis/common/v3/sports/{sport}/{league}/athletes/{id}/overview` | Athlete overview (stats snapshot, news, next game) |
| `/apis/common/v3/sports/{sport}/{league}/athletes/{id}/stats` | Season stats (NFL/NBA/NHL/MLB ✅, Soccer ❌) |
| `/apis/common/v3/sports/{sport}/{league}/athletes/{id}/gamelog` | Game-by-game log (NFL/NBA/MLB ✅) |
| `/apis/common/v3/sports/{sport}/{league}/athletes/{id}/splits` | Home/away/opponent splits |
| `/apis/common/v3/sports/{sport}/{league}/statistics/byathlete` | Stats leaderboard with `category=` + `sort=` |

### CDN API (Real-Time Optimized)

```
GET https://cdn.espn.com/core/{sport}/{resource}?xhr=1
```

| Endpoint | Description |
|----------|-------------|
| `/{sport}/scoreboard?xhr=1` | CDN-optimized live scoreboard |
| `/{sport}/scoreboard?xhr=1&league={league}` | Soccer scoreboard (league slug required, e.g. `eng.1`) |
| `/{sport}/game?xhr=1&gameId={id}` | Full game package — drives, plays, win probability, boxscore, odds |
| `/{sport}/boxscore?xhr=1&gameId={id}` | Boxscore only |
| `/{sport}/playbyplay?xhr=1&gameId={id}` | Play-by-play only |

> **Note:** CDN endpoints return JSON when `xhr=1` is passed. The `gamepackageJSON` key holds the full game data object.

### Now API (Real-Time News)

```
GET https://now.core.api.espn.com/v1/sports/news
```

| Endpoint | Description |
|----------|-------------|
| `/v1/sports/news?limit={n}` | Global real-time news feed |
| `/v1/sports/news?sport={sport}&limit={n}` | Sport-filtered news |
| `/v1/sports/news?leagues={league}&limit={n}` | League-filtered news |
| `/v1/sports/news?team={abbrev}&limit={n}` | Team-filtered news |

### Image & Asset URLs (CDN)

ESPN serves athlete headshots and team logos from `a.espncdn.com`. **All patterns below were live-verified (HTTP 200) on 2026-07-04.**

| URL pattern | Description |
|-------------|-------------|
| `https://a.espncdn.com/i/headshots/{sport}/players/full/{playerId}.png` | Athlete headshot (full size) |
| `https://a.espncdn.com/i/teamlogos/{sport}/500/{abbrev}.png` | Team logo (500 px) |

**Verified sport slugs for headshots:** `nfl`, `nba`, `mlb`, `nhl`, `soccer`
**Verified sport slugs for team logos:** `nfl`, `nba`, `mlb` (uses the team's lowercase abbreviation, e.g. `dal`, `lal`, `nyy`)

Verified examples:

```bash
curl -I "https://a.espncdn.com/i/headshots/nba/players/full/1966.png"   # LeBron James
curl -I "https://a.espncdn.com/i/headshots/mlb/players/full/33039.png"
curl -I "https://a.espncdn.com/i/headshots/soccer/players/full/45843.png"
curl -I "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"             # Dallas Cowboys
```

> **Note:** Not every athlete ID has a headshot on file — missing IDs return 404. Prefer the `headshot` / `logos` URLs returned inline by team, roster, and athlete endpoints when available. Team-logo sizes other than `500` (e.g. `100`) also exist.

---

## Common League Slugs

### 🏈 Football (sport: `football`)

| League | Slug |
|--------|------|
| NFL | `nfl` |
| College Football | `college-football` |
| CFL | `cfl` |
| UFL | `ufl` |
| XFL | `xfl` |

### 🏀 Basketball (sport: `basketball`)

| League | Slug |
|--------|------|
| NBA | `nba` |
| WNBA | `wnba` |
| NBA G League | `nba-development` |
| NCAA Men's | `mens-college-basketball` |
| NCAA Women's | `womens-college-basketball` |
| NBL | `nbl` |
| FIBA World Cup | `fiba` |

### ⚾ Baseball (sport: `baseball`)

| League | Slug |
|--------|------|
| MLB | `mlb` |
| NCAA Baseball | `college-baseball` |
| World Baseball Classic | `world-baseball-classic` |
| Dominican Winter League | `dominican-winter-league` |

### 🏒 Hockey (sport: `hockey`)

| League | Slug |
|--------|------|
| NHL | `nhl` |
| NCAA Men's | `mens-college-hockey` |
| NCAA Women's | `womens-college-hockey` |

### ⚽ Soccer (sport: `soccer`)

| League | Slug |
|--------|------|
| FIFA World Cup | `fifa.world` |
| UEFA Champions League | `uefa.champions` |
| English Premier League | `eng.1` |
| Spanish LALIGA | `esp.1` |
| German Bundesliga | `ger.1` |
| Italian Serie A | `ita.1` |
| French Ligue 1 | `fra.1` |
| MLS | `usa.1` |
| Liga MX | `mex.1` |
| NWSL | `usa.nwsl` |
| UEFA Europa League | `uefa.europa` |
| FIFA Women's World Cup | `fifa.wwc` |

### ⛳ Golf (sport: `golf`)

| Tour | Slug |
|------|------|
| PGA TOUR | `pga` |
| LPGA | `lpga` |
| DP World Tour | `eur` |
| LIV Golf | `liv` |
| PGA TOUR Champions | `champions-tour` |
| Korn Ferry Tour | `ntw` |

### 🏎️ Racing (sport: `racing`)

| Series | Slug |
|--------|------|
| Formula 1 | `f1` |
| IndyCar | `irl` |
| NASCAR Cup | `nascar-premier` |
| NASCAR Xfinity | `nascar-secondary` |
| NASCAR Truck | `nascar-truck` |

### 🎾 Tennis (sport: `tennis`)

| Tour | Slug |
|------|------|
| ATP | `atp` |
| WTA | `wta` |

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
?view=mMatchupScore
?view=mSettings
?view=mDraftDetail
?view=mScoreboard
?view=mStandings
?view=mStatus
?view=kona_player_info
```

### Segments

| Segment | Description |
|---------|-------------|
| `0` | Entire season |
| `1` | Playoff round 1 |
| `2` | Playoff round 2 |
| `3` | Championship |

### Authentication (Private Leagues)

Private leagues require cookies: `espn_s2` and `SWID`

---

## Betting & Odds

Base: `sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}`

| Endpoint | Description |
|----------|-------------|
| `/events/{id}/competitions/{id}/odds` | Game odds |
| `/events/{id}/competitions/{id}/probabilities` | Win probabilities |
| `/events/{id}/competitions/{id}/predictor` | ESPN game predictor |
| `/seasons/{year}/futures` | Season futures |
| `/seasons/{year}/types/{type}/teams/{id}/ats` | ATS records |
| `/seasons/{year}/types/{type}/teams/{id}/odds-records` | Team odds records |

**Betting Provider IDs:**

| Provider | ID |
|----------|----|
| Caesars | 38 |
| FanDuel | 37 |
| DraftKings | 41 |
| BetMGM | 58 |
| ESPN BET | 68 |
| Bet365 | 2000 |

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
| `page` | Page number | `1` |
| `groups` | Conference ID | `8` (SEC) |
| `enable` | Inline-expand extra data | `roster`, `stats`, `injuries`, `projection` |
| `active` | Active filter | `true` / `false` |
| `lang` | Language / locale | `en`, `es`, `pt` |
| `region` | Regional content filter | `us`, `gb`, `au` |
| `xhr` | CDN JSON signal | `1` (returns JSON on cdn.espn.com) |
| `calendartype` | Calendar view type | `ondays`, `offdays`, `blacklist` |
| `tz` | Timezone (personalized header) | `Asia/Calcutta`, `America/New_York` |

> 💡 **Getting *every* game (college sports):** the scoreboard endpoint truncates results by default. For NCAA sports pass `groups=50` (all Division I) together with a high `limit` (e.g. `limit=500`) to retrieve the full slate for a date or date range. **Verified 2026-07-04:** `.../mens-college-basketball/scoreboard?dates=20260120` returned **12** events, while adding `&groups=50&limit=500` returned **36** events for the same date.

### Season Types

| Type | Value |
|------|-------|
| Preseason | 1 |
| Regular Season | 2 |
| Postseason | 3 |
| Off Season | 4 |

### College Football Conference IDs (`groups` param)

| Conference | ID |
|------------|----|
| SEC | 8 |
| Big Ten | 5 |
| ACC | 1 |
| Big 12 | 4 |
| Mountain West | 17 |
| Top 25 | 80 |

---

## ESPN Service (Django Implementation)

This repository includes a production-ready Django REST API that wraps ESPN's endpoints.

### Features

- Full support for **17 sports** and **139 leagues**
- Data ingestion and persistence (teams, events, competitors, athletes, venues)
- Clean REST API with filtering and pagination
- Background jobs (Celery)
- Docker support
- OpenAPI documentation via drf-spectacular

### Quick Start

```bash
cd espn_service
docker compose up --build

# API: http://localhost:8000
# Docs: http://localhost:8000/api/docs/
```

### API Endpoints

#### Discovery & Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Health check |
| `/api/v1/sports/` | GET | List sports |
| `/api/v1/leagues/` | GET | List leagues (`?sport=basketball`) |
| `/api/v1/teams/` | GET | List teams (`?sport=`, `?league=`, `?search=`) |
| `/api/v1/teams/{id}/` | GET | Team details |
| `/api/v1/teams/espn/{espn_id}/` | GET | Team by ESPN ID |
| `/api/v1/events/` | GET | List events (`?league=`, `?date=`, `?status=`) |
| `/api/v1/events/{id}/` | GET | Event details |
| `/api/v1/events/espn/{espn_id}/` | GET | Event by ESPN ID |
| `/api/v1/news/` | GET | News articles (`?sport=`, `?league=`, `?date_from=`) |
| `/api/v1/news/{id}/` | GET | Article detail |
| `/api/v1/injuries/` | GET | Injury reports (`?sport=`, `?league=`, `?status=`, `?team=`) |
| `/api/v1/injuries/{id}/` | GET | Injury detail |
| `/api/v1/transactions/` | GET | Transactions (`?sport=`, `?league=`, `?date_from=`) |
| `/api/v1/transactions/{id}/` | GET | Transaction detail |
| `/api/v1/athlete-stats/` | GET | Season stats (`?sport=`, `?league=`, `?season=`, `?athlete_espn_id=`) |
| `/api/v1/athlete-stats/{id}/` | GET | Stats detail |

#### Ingest Triggers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ingest/teams/` | POST | Ingest ESPN teams |
| `/api/v1/ingest/scoreboard/` | POST | Ingest ESPN events |
| `/api/v1/ingest/news/` | POST | Ingest news articles (`limit` optional) |
| `/api/v1/ingest/injuries/` | POST | Refresh injury snapshot |
| `/api/v1/ingest/transactions/` | POST | Ingest transactions |

### ESPN Client Methods

The `ESPNClient` in `clients/espn_client.py` provides methods covering all major endpoints:

| Category | Methods |
|----------|---------|
| Scoreboard | `get_scoreboard()` |
| Teams | `get_teams()`, `get_team()`, `get_team_roster()`, `get_core_teams()` |
| Events | `get_event()`, `get_core_events()` |
| Standings | `get_standings()` (/apis/v2/), `get_core_standings()` |
| News | `get_news()`, `get_now_news()` |
| Rankings | `get_rankings()` |
| League info | `get_league_injuries()`, `get_league_transactions()`, `get_groups()` |
| Athletes | `get_athletes()`, `get_athlete()`, `get_athletes_v3()`, `get_athlete_statistics()` |
| Athlete v3 | `get_athlete_overview()`, `get_athlete_stats()`, `get_athlete_gamelog()`, `get_athlete_splits()` |
| Stats | `get_leaders()`, `get_leaders_v3()`, `get_statistics_by_athlete()` |
| Seasons | `get_seasons()` |
| Betting | `get_odds()`, `get_win_probabilities()` |
| Play data | `get_plays()`, `get_game_situation()`, `get_game_predictor()`, `get_game_broadcasts()` |
| CDN | `get_cdn_game()`, `get_cdn_scoreboard()` |
| Venues | `get_venues()` |
| Coaches | `get_coaches()`, `get_coach()` |
| Metadata | `get_league_info()` |
| Power Index | `get_power_index()` |
| QBR | `get_qbr()` |

### Database Models

| Model | Key Fields | Updated Via |
|-------|-----------|-------------|
| `Sport` | slug, name | `ingest/teams/` |
| `League` | slug, name, abbreviation | `ingest/teams/` |
| `Team` | espn_id, display_name, logos, color | `ingest/teams/` |
| `Event` | espn_id, date, status, season_year | `ingest/scoreboard/` |
| `Competitor` | team, home_away, score, winner | `ingest/scoreboard/` |
| `Athlete` | espn_id, position, headshot | manual/client |
| `Venue` | espn_id, name, city, capacity | `ingest/scoreboard/` |
| `NewsArticle` | espn_id, headline, published, league | `ingest/news/` |
| `Injury` | athlete_name, status, injury_type, team | `ingest/injuries/` |
| `Transaction` | espn_id, date, description, type | `ingest/transactions/` |
| `AthleteSeasonStats` | athlete_espn_id, season_year, stats (JSON) | `AthleteStatsIngestionService` |

### Celery Beat Schedule

| Task | Frequency |
|------|-----------|
| `refresh_all_news_task` | Every 30 minutes |
| `refresh_all_injuries_task` | Every 4 hours |
| `refresh_all_transactions_task` | Every 6 hours |
| `refresh_scoreboard_task` (NBA/NFL) | Every hour |
| `refresh_all_teams_task` | Weekly |

### Management Commands

```bash
# Ingest news for a single league
python manage.py ingest_news --sport basketball --league nba

# Ingest news for all configured leagues
python manage.py ingest_news

# Refresh injury report for a league
python manage.py ingest_injuries --sport football --league nfl

# Ingest transactions
python manage.py ingest_transactions --sport basketball --league nba

# Ingest all teams (all configured leagues)
python manage.py ingest_all_teams
```

### Docker Testing

```bash
cd espn_service

# Build and run full test suite
docker compose -f docker-compose.test.yml run --rm test

# Run a specific test file
docker compose -f docker-compose.test.yml run --rm test \
  python -m pytest tests/test_ingestion_new.py -v --no-cov
```

### Example Usage

```bash
# Ingest NBA teams
curl -X POST http://localhost:8000/api/v1/ingest/teams/ \
  -H "Content-Type: application/json" \
  -d '{"sport": "basketball", "league": "nba"}'

# Ingest NFL injury report
curl -X POST http://localhost:8000/api/v1/ingest/injuries/ \
  -H "Content-Type: application/json" \
  -d '{"sport": "football", "league": "nfl"}'

# Ingest NBA news (last 25 articles)
curl -X POST http://localhost:8000/api/v1/ingest/news/ \
  -H "Content-Type: application/json" \
  -d '{"sport": "basketball", "league": "nba", "limit": 25}'

# Query injuries by status
curl "http://localhost:8000/api/v1/injuries/?league=nfl&status=out"

# Query latest NBA news
curl "http://localhost:8000/api/v1/news/?league=nba&date_from=2024-01-01"

# Query events
curl "http://localhost:8000/api/v1/events/?league=nfl&date=2024-12-15"
```

See [espn_service/README.md](espn_service/README.md) for full service documentation.

---

## Notable Specialized Endpoints

These endpoints are available but not part of the standard sport-scoped pattern:

### 🏈 QBR (Quarterback Rating)

```bash
# Season QBR by conference
GET https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/{type}/groups/{group}/qbr/{split}

# Weekly QBR
GET https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/types/{type}/weeks/{week}/qbr/{split}
```

> `split` values: `0` = totals, `1` = home, `2` = away

### 🏀 Bracketology (NCAA Tournament)

```bash
# Live bracket projections
GET https://sports.core.api.espn.com/v2/tournament/{tournamentId}/seasons/{year}/bracketology

# Snapshot at a specific iteration
GET https://sports.core.api.espn.com/v2/tournament/{tournamentId}/seasons/{year}/bracketology/{iteration}
```

### 📊 Power Index (BPI / SP+)

```bash
# Season-level
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/powerindex

# Leaders
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/powerindex/leaders

# By team
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/powerindex/{teamId}
```

### 🎓 Recruiting (College Sports)

```bash
# Recruit rankings by year
GET https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/seasons/{year}/recruits

# Recruiting class by team
GET https://sports.core.api.espn.com/v2/sports/football/leagues/college-football/seasons/{year}/classes/{teamId}
```

### 👔 Coaches

```bash
# All coaches for a season
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/seasons/{year}/coaches

# Individual coach
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/coaches/{coachId}

# Coach career record by type
GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/coaches/{coachId}/record/{type}
```

---

## Contributing

Found a new endpoint? Please open an issue or PR!

## License

MIT License — See LICENSE file

---

*Last Updated: July 2026 · 17 sports · 139 leagues · 370 v2 + 79 v3 endpoints · 7 API domains*

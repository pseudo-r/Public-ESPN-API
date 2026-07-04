# Changelog

All notable changes to the Public ESPN API documentation are listed here.

---

## [2.1.0] — July 2026

### 🆕 Added

#### Documentation — Newly Discovered Endpoints
> All endpoints below were **live-verified (HTTP 200) on 2026-07-04**, and their response structures were inspected and documented field-by-field.

- **Personalized Scoreboard Header** — `site.api.espn.com/apis/personalized/v2/scoreboard/header?sport={sport}&region={region}&tz={tz}` — returns `sports[].leagues[]`, each an active series/competition with numeric `id`, `name`, `isTournament`, `smartdates`, and `events[]`. Notably useful for **cricket series discovery** (the series `id` feeds the cricket web-API summary). Added to README Search & Web API table, `docs/README.md` routing guide/quick links, and `cricket.md` (with a documented discovery → summary workflow).
- **Golf Player Summary (hole-by-hole)** — `site.web.api.espn.com/apis/site/v2/sports/golf/{tour}/leaderboard/{eventId}/playersummary?season={year}&player={id}`. Verified structure: `profile`, `rounds[]` (each with `linescores[]` = per-hole `value`/`par`/`scoreType`), and `stats[]`. Added to README and `golf.md` with a response-field table.
- **Cricket Match Summary (web API)** — `site.web.api.espn.com/apis/site/v2/sports/cricket/{leagueId}/summary?event={id}&lang=en&region=in`. Verified top-level keys: `notes`, `gameInfo`, `rosters`, `matchcards`, `debuts`, `news`, `leaders`, `article`, `videos`, `header`, `meta`. Added to README and `cricket.md`.
- **Image & Asset URLs** — new `a.espncdn.com` section documenting athlete headshot (`/i/headshots/{sport}/players/full/{id}.png`) and team logo (`/i/teamlogos/{sport}/500/{abbrev}.png`) URL patterns. Verified across `nfl`, `nba`, `mlb`, `nhl`, `soccer` headshots and `nfl`/`nba`/`mlb` logos. Added to README, and as a new row in the `docs/README.md` domain routing guide (now **7 API domains**).

#### Documentation — MMA (`mma.md`) rewrite
> Live-verified 2026-03-27.
- Replaced the estimated "50+ promotions" list with **48 confirmed slugs** and a Core API status matrix.
- Added **Core v2 / v3 live-status tables** (working vs. 400/500 endpoints), a **Site API status table** (scoreboard works only for `ufc`, `bellator`, `pfl`), the personalized scoreboard header, and a step-by-step **fight-statistics data-flow** guide (event → competition → competitor statistics/linescores/plays/odds).
- Documented MMA-specific caveats: `common/v3` athlete stats are unavailable; athletes use a different ID space (resolve via competitor `$ref` URLs); `active` filter unsupported.

#### Documentation — Parameters
- **`tz` parameter** documented (timezone for the personalized header).
- **`groups` + `limit` guidance** — added a tip explaining how to retrieve *every* college game for a date/range using `groups=50` (all Division I) with a high `limit`. **Verified:** `mens-college-basketball/scoreboard?dates=20260120` returned 12 events vs. 36 with `&groups=50&limit=500`.

### 🔧 Changed
- README footer updated to **July 2026 · 7 API domains**.
- `docs/README.md` domain routing note now records the **2026-07-04** re-verification for the image domain and personalized/web-API endpoints.

---

## [Unreleased] — March 2026

### 🆕 Added

#### Documentation
- **`cdn.espn.com` section** — CDN API endpoints for real-time, cached scoreboards
- **`now.core.api.espn.com` section** — Real-time news feed endpoints
- **`site.web.api.espn.com` section** — Search API and rich athlete overview endpoints
- **Site API v3 section** — `site.api.espn.com/apis/site/v3` scoreboard and game summary
- **Notable Specialized Endpoints** section in README covering:
  - QBR (Total Quarterback Rating) — season, weekly, NFL + NCAAF
  - Bracketology (NCAA Tournament live projections)
  - Power Index (BPI / SP+ / FPI)
  - Recruiting (college football & basketball)
  - Coaches (season rosters, career records)
- **Site API endpoint tables** added to all 17 sport-specific docs (`football.md`, `basketball.md`, `baseball.md`, `hockey.md`, `soccer.md`, `golf.md`, `racing.md`, `tennis.md`, `mma.md`, `rugby.md`, `rugby_league.md`, `lacrosse.md`, `cricket.md`, `volleyball.md`, `water_polo.md`, `field_hockey.md`, `australian_football.md`)
- **Specialized Endpoints sections** for:
  - `football.md` — QBR, Recruiting, SP+ Power Index
  - `basketball.md` — Bracketology (with tournament IDs), BPI
- **Core API v2 table expanded** — added `situation`, `broadcasts`, `predictor`, `powerindex`, `competitors/{id}/linescores`, `competitors/{id}/statistics`, `coaches`, `QBR`, seasonal `powerindex`
- **Core API v3 table expanded** — added `athletes/{id}`, `statisticslog`, `plays`
- **Site API v2 table expanded** — added `teams/{id}/depthcharts`, `teams/{id}/injuries`, `teams/{id}/transactions`, `teams/{id}/history`, `athletes/{id}` sub-resources, `calendar` variants
- **Fantasy API improvements** — added `mMatchupScore`, `mScoreboard`, `mStandings`, `mStatus`, `kona_player_info` views and a Segments table (`0`=season, `1–3`=playoff rounds)
- **Betting providers expanded** — FanDuel (37), BetMGM (58), ESPN BET (68) added; `predictor` and `odds-records` endpoints added
- **Parameters Reference expanded** — `lang`, `region`, `xhr`, `calendartype` added
- **CHANGELOG.md** (this file)
- **`docs/response_schemas.md`** — example JSON response structures for common endpoints

#### Code (`espn_service`)
New methods added to `ESPNClient`:
- `get_team_injuries(sport, league, team_id)` — Site API team injury report
- `get_team_depth_chart(sport, league, team_id)` — Site API depth chart
- `get_team_transactions(sport, league, team_id)` — Site API team transactions
- `get_game_situation(sport, league, event_id)` — Core API game situation (down/distance)
- `get_game_predictor(sport, league, event_id)` — ESPN game predictor
- `get_game_broadcasts(sport, league, event_id)` — Broadcast network info
- `get_coaches(sport, league, season)` — Season coaching staff
- `get_coach(sport, league, coach_id)` — Individual coach profile
- `get_qbr(league, season, ...)` — ESPN QBR data (football only)
- `get_power_index(sport, league, season)` — ESPN BPI / SP+ / FPI

### 🔧 Fixed
- **`http://` → `https://`** in `docs/sports/_global.md` — all 350+ Core API v2 endpoints now use secure protocol
- **`http://` → `https://`** in all 17 sport-specific doc files (football, basketball, soccer, etc.)
- **README Table of Contents** — sub-items under "API Endpoint Patterns" now render as proper nested list (fixed 2-space → 4-space indent)

---

## [2.0.0] — February 2026

### 🆕 Added
- Full Django-based `espn_service` with REST API, management commands, and admin
- `ESPNClient` with retry logic, timeouts, structured logging
- `TeamIngestionService` and `ScoreboardIngestionService`
- 17-sport, 139-league WADL mapping in `SPORT_NAMES` and `LEAGUE_INFO`
- `docs/sports/` — individual doc files for all 17 sports

### 🔧 Fixed
- Consolidated all v2/v3 endpoint patterns from ESPN WADL

---

## [1.0.0] — Initial Release

### 🆕 Added
- Initial ESPN API documentation
- README with base URLs, quick start, common endpoints
- `docs/sports/_global.md` with full WADL-sourced endpoint list

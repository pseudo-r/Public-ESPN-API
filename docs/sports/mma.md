# 🥊 MMA

> Mixed Martial Arts from the UFC, Bellator, PFL, and 45+ international promotions.

**Sport slug:** `mma`  
**Base URL (v2):** `https://sports.core.api.espn.com/v2/sports/mma/`  
**Base URL (v3):** `https://sports.core.api.espn.com/v3/sports/mma/`

---

## Leagues & Competitions

> ESPN tracks **48 confirmed MMA organizations** (live-verified 2026-03-27). Use `https://sports.core.api.espn.com/v2/sports/mma/leagues` for the authoritative list.

### Major Promotions

| Slug | League Name | Site Scoreboard |
|------|-------------|-----------------|
| `ufc` | Ultimate Fighting Championship | ✅ |
| `bellator` | Bellator MMA (now PFL) | ✅ |
| `pfl` | Professional Fighters League | ✅ |
| `one-championship` | ONE Championship | ❌ (400) |
| `ifc` | Invicta FC (Women's) | ❌ (400) |
| `lfa` | Legacy Fighting Alliance | ❌ (400) |
| `ksw` | Konfrontacja Sztuk Walki | ❌ (400) |
| `cage-warriors` | Cage Warriors | ❌ (400) |

### All 48 Confirmed Slugs (Core API Only)

| Slug | Slug | Slug | Slug |
|------|------|------|------|
| `absolute` | `affliction` | `bang-fighting` | `banni-fight` |
| `banzay` | `barracao` | `battlezone` | `bellator` |
| `benevides` | `big-fight` | `blackout` | `boku` |
| `bosnia` | `boxe` | `brazilian-freestyle` | `budo` |
| `cage-warriors` | `dream` | `fng` | `ifc` |
| `ifl` | `k1` | `ksw` | `lfa` |
| `lfc` | `m1` | `mfc` | `one-championship` |
| `pfl` | `pride` | `resurrection` | `rings` |
| `road-fc` | `shoxc` | `shooto-japan` | `strikeforce` |
| `tfc` | `tpf` | `ufc` | `vfc` |
| `wec` | `xfc` | `xfcbrazil` | *(+ 4 additional)* |

---

## Core v2 API Endpoints — Live Status

> All endpoints: `https://sports.core.api.espn.com/v2/sports/mma/leagues/{league}/`

### ✅ Working Endpoints

| Endpoint | Notes |
|----------|-------|
| `seasons` | Full season list |
| `season` | Current season shortcut |
| `athletes` | All fighters (no `active` filter — see warning) |
| `events` | All events; supports `?dates=YYYY` |
| `events?dates=YYYY` | Date-filtered event list |
| `teams` | Returns (empty — MMA has no teams) |
| `rankings` | Weight class rankings |
| `venues` | Arenas/octagon venues |
| `circuits` | |
| `countries` | Participating countries |
| `providers` | Broadcast providers |
| `casinos` | Sportsbooks/odds providers |
| `recruiting` | (empty — MMA has no recruiting) |
| `calendar` | Event calendar |
| `seasons/{year}/athletes` | Season-scoped fighters |
| `seasons/{year}/draft` | (empty — MMA has no draft) |
| `seasons/{year}/freeagents` | |
| `seasons/{year}/manufacturers` | |
| `seasons/{year}/types` | Season types |
| `seasons/{year}/standings` | (empty — MMA has no standings) |
| `seasons/{year}/rankings` | Season rankings by weight class |
| `seasons/{year}/powerindex` | |
| `seasons/{year}/leaders` | |
| `seasons/{year}/weeks` | |
| `seasons/{year}/groups` | Weight class groups |

### ❌ Broken Endpoints (return 500 — not applicable for MMA)

| Endpoint | Status | Reason |
|----------|--------|--------|
| `media` | ❌ 500 | Not supported for MMA |
| `franchises` | ❌ 500 | Not applicable |
| `positions` | ❌ 500 | Not applicable |
| `tournaments` | ❌ 500 | Not applicable |
| `seasons/{year}/draft` | ❌ 500 | No draft system |
| `athletes?active=true` | ❌ 400 | `active` filter unsupported for MMA |

---

## Core v3 API Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `https://sports.core.api.espn.com/v3/sports/mma/athletes` | ✅ 200 | All MMA athletes (cross-league) |
| `https://sports.core.api.espn.com/v3/sports/mma/ufc` | ✅ 200 | League detail |
| `https://sports.core.api.espn.com/v3/sports/mma/ufc/seasons/{year}` | ✅ 200 | Season detail |
| `https://sports.core.api.espn.com/v3/sports/mma/ufc/events` | ✅ 200 | Event list |
| `https://sports.core.api.espn.com/v3/sports/mma/ufc/teams` | ✅ 200 | (empty) |
| `https://sports.core.api.espn.com/v3/sports/mma/ufc/athletes` | ✅ 200 | League-scoped athletes |
| `…/athletes?active=true` | ❌ 400 | Same v2 limitation |

---

## Site API Endpoints

> Base: `https://site.api.espn.com/apis/site/v2/sports/mma/{league}/`

| Resource | Status | Notes |
|----------|--------|-------|
| `scoreboard` | ✅ 200 | Current/upcoming fight cards |
| `scoreboard?dates=YYYYMMDD` | ✅ 200 | Date-specific events |
| `news` | ✅ 200 | MMA news feed |
| `teams` | ✅ 200 | (returns empty array) |
| `athletes/{id}/news` | ✅ 200 | Fighter-specific news |
| `summary?event={id}` | ✅ 200 | Full fight card summary with results |
| `injuries` | ❌ 500 | Not supported for MMA |
| `standings` | ❌ 400 | Not applicable for MMA |
| `schedule` | ❌ 400 | Use `scoreboard` instead |
| `roster` | ❌ 400 | Not applicable |
| `leaders` | ❌ 400 | Not applicable |
| `statistics` | ❌ 400 | Not applicable |
| `depth-charts` | ❌ 400 | Not applicable |
| `groups` | ❌ 400 | Not applicable |
| `draft` | ❌ 500 | Not applicable |
| `transactions` | ❌ 400 | Not applicable |

> ✅ **Site API scoreboard** works for: `ufc`, `bellator`, `pfl`  
> ❌ All other league slugs return 400 for scoreboard.

---

## Personalized Scoreboard Header (NEW)

```
GET https://site.api.espn.com/apis/personalized/v2/scoreboard/header?sport=mma&league=ufc
```

Returns scoreboard header data for widget/app embedding. Supports `?league=ufc` or omit for all MMA.

---

## 🔥 Fight Statistics — Correct Data Flow

> **`common/v3` athlete stats are NOT available for MMA.** Use the event drill-down below instead.

### Step-by-Step: Get Fight Statistics

```
1. GET https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events?dates=YYYYMMDD&limit=5
   → Returns items[] with $ref URLs → extract event_id

2. GET https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events/{event_id}
   → Returns event metadata + competitions[] (one per fight)
   → Extract: competition.id, competition.competitors[].id

3. GET …/events/{event_id}/competitions/{comp_id}/competitors/{competitor_id}/statistics
   → ✅ 200 — Returns: significant strikes landed/attempted, takedowns, grappling control time

4. GET …/events/{event_id}/competitions/{comp_id}/competitors/{competitor_id}/linescores
   → ✅ 200 — Returns: round-by-round judging scores

5. GET …/events/{event_id}/competitions/{comp_id}/plays
   → ✅ 200 — Returns: play-by-play (strikes, takedowns per round)

6. GET …/events/{event_id}/competitions/{comp_id}/odds
   → ✅ 200 — Returns: pre-fight moneyline odds per fighter

7. GET …/events/{event_id}/competitions/{comp_id}/officials
   → ✅ 200 — Returns: referee + judge names

8. GET …/events/{event_id}/competitions/{comp_id}/broadcasts
   → ✅ 200 — Returns: ESPN/ESPN+ broadcast info

9. GET …/events/{event_id}/competitions/{comp_id}/status
   → ✅ 200 — Returns: fight result (KO/TKO/Decision/Sub), winner, rounds
```

### Competition Sub-Resources Summary

| Sub-resource | Status | Returns |
|-------------|--------|---------|
| `competitors/{id}/statistics` | ✅ 200 | Strikes, takedowns, grappling control |
| `competitors/{id}/linescores` | ✅ 200 | Round-by-round judging |
| `competitors/{id}/plays` | ❌ 404 | Not supported at competitor level |
| `odds` | ✅ 200 | Moneyline odds |
| `officials` | ✅ 200 | Referee + judges |
| `broadcasts` | ✅ 200 | Broadcast networks |
| `plays` | ✅ 200 | Play-by-play sequence |
| `status` | ✅ 200 | Fight result |
| `linescores` | ❌ 404 | Not supported at competition level |

---

## Athlete Sub-Resources

> ⚠️ Athlete IDs in MMA use a **different ID space** than other sports.  
> Get the correct ID from competitor `$ref` URLs in event/scoreboard responses — do not assume an ID.

| Sub-resource | Status | Notes |
|-------------|--------|-------|
| `athletes/{id}` (profile) | ⚠️ Context-dependent | Use ID from event $ref |
| `athletes/{id}/eventlog` | ✅ 200 | Fighter's event history |
| `athletes/{id}/statistics` | ❌ 404 (league path) | Use event drill-down instead |
| `athletes/{id}/statisticslog` | ❌ 404 | |
| `athletes/{id}/splits` | ❌ 404 | |
| `athletes/{id}/injuries` | ❌ 404 | |
| `common/v3/.../athletes/{id}/overview` | ❌ 404 | **Not available for MMA** |
| `common/v3/.../athletes/{id}/stats` | ❌ 404 | **Not available for MMA** |
| `common/v3/.../athletes/{id}/gamelog` | ❌ 404 | **Not available for MMA** |

---

## CDN

> ❌ `cdn.espn.com/core/mma/scoreboard` returns **404** — CDN scoreboard is **not available** for MMA.

---

## Example API Calls

```bash
# Get all 48 MMA leagues
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues?limit=100"

# UFC scoreboard (current events)
curl "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"

# PFL scoreboard
curl "https://site.api.espn.com/apis/site/v2/sports/mma/pfl/scoreboard"

# UFC events with date filter
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events?dates=2025&limit=10"

# UFC weight class rankings
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/rankings"

# Get fight statistics for a specific fight
EVENT_ID=600051442   # UFC 311
COMP_ID=401737005    # Main event fight
FIGHTER_ID=4423876   # Competitor ID (from $ref)
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events/${EVENT_ID}/competitions/${COMP_ID}/competitors/${FIGHTER_ID}/statistics"

# Round-by-round scoring
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events/${EVENT_ID}/competitions/${COMP_ID}/competitors/${FIGHTER_ID}/linescores"

# Fight play-by-play
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events/${EVENT_ID}/competitions/${COMP_ID}/plays"

# Moneyline odds
curl "https://sports.core.api.espn.com/v2/sports/mma/leagues/ufc/events/${EVENT_ID}/competitions/${COMP_ID}/odds"

# Event summary (fight card results)
curl "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/summary?event=${EVENT_ID}"

# Fighter news
curl "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/athletes/3023164/news"

# Personalized scoreboard header
curl "https://site.api.espn.com/apis/personalized/v2/scoreboard/header?sport=mma&league=ufc"
```

# ESPN API Documentation

> Comprehensive reference for the unofficial ESPN API — endpoints, parameters, league slugs, response schemas, and a working Django service.

---

## 📁 File Index

### Root
| File | Description |
|------|-------------|
| [README.md](../README.md) | Full documentation — base URLs, endpoint patterns, fantasy, betting, specialized endpoints |
| [CHANGELOG.md](../CHANGELOG.md) | History of all documented changes |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | How to contribute endpoints, fixes, and code |

### Sports Reference (`docs/sports/`)

Each file covers leagues & competitions, API endpoints, Site API resources, and curl examples for that sport.

| File | Sport | Key Leagues |
|------|-------|-------------|
| [_global.md](sports/_global.md) | All Sports | Every v2 endpoint — full WADL listing |
| [football.md](sports/football.md) | 🏈 Football | NFL, NCAAF, CFL, UFL, XFL |
| [basketball.md](sports/basketball.md) | 🏀 Basketball | NBA, WNBA, NCAAM, NCAAW, NBL, FIBA |
| [soccer.md](sports/soccer.md) | ⚽ Soccer | EPL, La Liga, Bundesliga, MLS, UCL, 260+ leagues |
| [baseball.md](sports/baseball.md) | ⚾ Baseball | MLB, NCAAB, WBC, Caribbean/Winter Leagues |
| [hockey.md](sports/hockey.md) | 🏒 Hockey | NHL, NCAAH, Olympics |
| [golf.md](sports/golf.md) | ⛳ Golf | PGA TOUR, LPGA, LIV, DP World Tour, TGL |
| [racing.md](sports/racing.md) | 🏎️ Racing | Formula 1, IndyCar, NASCAR Cup/Xfinity/Truck |
| [tennis.md](sports/tennis.md) | 🎾 Tennis | ATP, WTA |
| [mma.md](sports/mma.md) | 🥊 MMA | UFC, Bellator, LFA, and 50+ promotions |
| [rugby.md](sports/rugby.md) | 🏉 Rugby Union | World Cup, Six Nations, Premiership, Super Rugby |
| [rugby_league.md](sports/rugby_league.md) | 🏉 Rugby League | NRL, Super League |
| [lacrosse.md](sports/lacrosse.md) | 🥍 Lacrosse | PLL, NLL, NCAA Men's/Women's |
| [cricket.md](sports/cricket.md) | 🏏 Cricket | ICC T20, ICC ODI, IPL |
| [volleyball.md](sports/volleyball.md) | 🏐 Volleyball | FIVB Men/Women, NCAA Men's/Women's |
| [water_polo.md](sports/water_polo.md) | 🤽 Water Polo | FINA Men/Women, NCAA Men's/Women's |
| [field_hockey.md](sports/field_hockey.md) | 🏑 Field Hockey | FIH Men/Women, NCAA Women's |
| [australian_football.md](sports/australian_football.md) | 🦘 Australian Football | AFL |

### API Reference
| File | Description |
|------|-------------|
| [response_schemas.md](response_schemas.md) | Example JSON responses for scoreboard, teams, roster, injuries, game summary, athlete, odds, standings, Now API |

### Domain Routing Guide

> All domains below were **live-verified via browser HTTP tests on 2026-03-26** — all returned HTTP 200 OK. The `a.espncdn.com` image domain and the personalized/web-API endpoints were additionally verified on **2026-07-04**.

| Domain | Use for | Verified Response Keys |
|--------|---------|----------------------|
| `site.api.espn.com/apis/site/v2/` | Scoreboard, teams, news, injuries, transactions, statistics, groups, draft, summary, rankings | `leagues`, `season`, `week`, `events` (scoreboard); `header`, `articles` (news); `uid`, `children` (standings) |
| `site.api.espn.com/apis/v2/` | **Standings only** — site/v2 returns a stub | `uid`, `id`, `name`, `abbreviation`, `children` |
| `site.web.api.espn.com/apis/common/v3/` | Athlete stats, gamelog, overview, splits (`statistics/byathlete`) | `leagues`, `season`, `day`, `events` (same as site.api) |
| `cdn.espn.com/core/` | Full game packages — drives, plays, odds (requires `?xhr=1`) | Varies by sport |
| `now.core.api.espn.com/v1/` | Real-time news feed — filter by `sport=`, `league=`, `team=` | `resultsCount`, `resultsLimit`, `resultsOffset`, `headlines[]` |
| `sports.core.api.espn.com/v2/` | Core data — events, odds, play-by-play, athletes, coaches | Leagues: `$ref`, `id`, `name`, `season`, `teams`, `athletes`; Collections: `count`, `pageIndex`, `pageSize`, `items[]` |
| `a.espncdn.com/i/` | Athlete headshots & team logos (image assets) | Binary PNG (`headshots/{sport}/players/full/{id}.png`, `teamlogos/{sport}/500/{abbrev}.png`) |

**Sport-specific exceptions:**
- 🏏 **Cricket scoreboard** → core API: `sports.core.api.espn.com/v2/sports/cricket/leagues/{league}/events`
- 🏉 **Rugby Union standings** → core API: `sports.core.api.espn.com/v2/sports/rugby/leagues/{league}/standings`
- ⛳ **Golf / 🎾 Tennis scoreboard** → slug required: `pga`, `lpga`, `atp`, `wta` (not numeric IDs)

**Known quirks:**
- ⚠️ **`$ref` URLs with `.pvt` domain:** Some Core API responses return `$ref` URLs pointing to `sports.core.api.espn.pvt` — ESPN's internal domain. Replace `.pvt` with `.com` to get a working public URL.
- ⚠️ **Season dates vs. scoreboard data:** Season start/end dates from the `/seasons` endpoint may not align with actual scoreboard data availability. If a scoreboard query returns empty for the reported start date, adjust the date range to when matches actually begin.


---

## 🚀 Quick Links

| Data | Endpoint |
|------|----------|
| Scoreboard | `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard` |
| Teams | `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams` |
| Standings | `https://site.api.espn.com/apis/v2/sports/{sport}/{league}/standings` |
| Game summary | `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={id}` |
| Full game package | `https://cdn.espn.com/core/{sport}/game?xhr=1&gameId={id}` |
| Athlete overview | `https://site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/overview` |
| Athlete stats | `https://site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/stats` |
| Stats leaderboard | `https://site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/statistics/byathlete` |
| Real-time news | `https://now.core.api.espn.com/v1/sports/news?sport=football` |
| Core API | `https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/...` |
| Personalized header | `https://site.api.espn.com/apis/personalized/v2/scoreboard/header?sport={sport}&region={region}&tz={tz}` |
| Golf player summary | `https://site.web.api.espn.com/apis/site/v2/sports/golf/{tour}/leaderboard/{eventId}/playersummary?season={year}&player={id}` |
| Cricket match summary | `https://site.web.api.espn.com/apis/site/v2/sports/cricket/{leagueId}/summary?event={id}&lang=en&region=in` |
| Athlete headshot | `https://a.espncdn.com/i/headshots/{sport}/players/full/{playerId}.png` |


# ⛳ Golf

> Professional golf tours including PGA TOUR, LPGA, DP World Tour (European Tour), LIV Golf, and more.

**Sport slug:** `golf`  
**Base URL (v2):** `https://sports.core.api.espn.com/v2/sports/golf/`  
**Base URL (v3):** `https://sports.core.api.espn.com/v3/sports/golf/`

---

## Leagues & Competitions

| Abbreviation | League Name | Slug | Full URL |
| --- | --- | --- | --- |
| `SGA` | PGA TOUR Champions | `champions-tour` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/champions-tour` |
| `EUR` | DP World Tour | `eur` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/eur` |
| `LIV` | LIV Golf Invitational Series | `liv` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/liv` |
| `LPGA` | Ladies Pro Golf Association | `lpga` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/lpga` |
| `OLYM` | Olympic Golf - Men | `mens-olympics-golf` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/mens-olympics-golf` |
| `KORN FERRY` | Korn Ferry Tour | `ntw` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/ntw` |
| `PGA` | PGA TOUR | `pga` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/pga` |
| `TGL` | TGL | `tgl` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/tgl` |
| `OLYW` | Olympic Golf - Women | `womens-olympics-golf` | `https://sports.core.api.espn.com/v2/sports/golf/leagues/womens-olympics-golf` |

---

## API Endpoints

> All endpoints below follow the pattern:  
> `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}<sub-path>`  
> Replace `{league}` with a league slug from the table above.

### Common Query Parameters

Most list endpoints support: `page` (int), `limit` (int). Additional filters are documented per endpoint.

### Seasons & Calendar

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/calendar` | `getCalendars` | `dates`, `page`, `limit`, `dates`, `groups`, `smartdates`, `advance`, `utcOffset`, `weeks`, `seasontype` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/seasons` | `getSeasons` | `page`, `limit`, `utcOffset`, `dates`, `start`, `end`, `eventsback`, `eventsforward`, `eventsrange`, `eventcompleted`, `groups`, `profile`, `competitions.types`, `types`, `season`, `weeks`, `tournamentId`, `dates`, `sort`, `type`, `date`, `group`, `position`, `week`, `qualified`, `types`, `limit`, `page`, `sort`, `position`, `status`, `sort`, `sortByRanks`, `stats`, `groupId`, `position`, `qualified`, `rookie`, `international`, `category`, `type`, `sort`, `sortByRanks`, `stats`, `groupId`, `qualified`, `category`, `sort`, `groupId`, `allStar`, `group`, `gender`, `types`, `country`, `association`, `lastNameInitial`, `lastName`, `active`, `statuses`, `sort`, `position`, `dates`, `groups`, `smartdates`, `advance`, `utcOffset`, `weeks`, `seasontype` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/seasons/{season}/athletes` | `getAthletes` | `active`, `sort`, `page`, `limit`, `seasontypes`, `played`, `teamtypes`, `group`, `gender`, `types`, `country`, `association`, `lastNameInitial`, `lastName`, `active`, `statuses`, `sort`, `position` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/seasons/{season}/draft` | `getDraftByYear` | `page`, `limit`, `available`, `position`, `team`, `sort`, `filter` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/seasons/{season}/freeagents` | `getFreeAgents` | `page`, `limit`, `types`, `oldteams`, `newteams`, `position`, `sort` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/seasons/{season}/manufacturers` | `getManufacturers` | `page`, `limit` |

### Teams

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/teams` | `getTeams` | `page`, `limit`, `utcOffset`, `dates`, `start`, `end`, `eventsback`, `eventsforward`, `eventsrange`, `eventcompleted`, `groups`, `profile`, `competitions.types`, `types`, `season`, `weeks`, `tournamentId`, `active`, `national`, `start`, `group`, `dates`, `recent`, `types`, `winnertype`, `date`, `eventsback`, `excludestatuses`, `includestatuses`, `dates`, `groups`, `smartdates`, `advance`, `utcOffset`, `weeks`, `seasontype` |

### Athletes / Players

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/athletes` | `getAthletes` | `page`, `limit`, `group`, `gender`, `types`, `country`, `association`, `lastNameInitial`, `lastName`, `active`, `statuses`, `sort`, `position` |

### Events / Games

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}` | `getEvent` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}/competitions/{competition}` | `getCompetition` | `page`, `limit`, `date`, `group`, `position`, `week`, `qualified`, `types`, `limit`, `page`, `types`, `period`, `sort`, `source`, `showsubplays` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}/competitions/{competition}/broadcasts` | `getBroadcasts` | `lang`, `region`, `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}/competitions/{competition}/competitors/{competitor}` | `getCompetitor` | `page`, `limit`, `date`, `group`, `position`, `week`, `qualified`, `types`, `limit`, `page` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}/competitions/{competition}/odds` | `getCompetitionOdds` | `provider.priority`, `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}/competitions/{competition}/officials` | `getOfficials` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/events/{event}/competitions/{competition}/plays/{play}/personnel` | `getPersonnel` | `page`, `limit` |

### News & Media

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/media` | `getMedia` | `page`, `limit` |

### Rankings & Awards

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/rankings` | `getRankings` | `page`, `limit` |

### Venues

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/venues` | `getVenues` | `page`, `limit` |

### Other

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/casinos` | `getCasinos` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/circuits` | `getCircuits` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/countries` | `getCountries` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/franchises` | `getFranchises` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/positions` | `getPositions` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/providers` | `getProviders` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/recruiting` | `getRecruitingSeasons` | `page`, `limit`, `sort`, `position`, `status` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/season` | `getCurrentSeason` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/golf/leagues/{league}/tournaments` | `getTournaments` | `majorsOnly`, `page`, `limit` |

---

## V3 Endpoints

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v3/sports/{sport}/athletes` | `getAthletes` | `page`, `limit`, `_hoist`, `_help`, `_trace`, `_nocache`, `enable`, `disable`, `pq`, `q`, `page`, `limit`, `lang`, `region`, `utcOffset`, `dates`, `weeks`, `advance`, `event.recurring`, `ids`, `type`, `types`, `seasontypes`, `calendar.type`, `calendar.groups`, `status`, `statuses`, `groups`, `provider`, `provider.priority`, `site`, `league.type`, `split`, `splits`, `record.splits`, `record.seasontype`, `statistic.splits`, `statistic.seasontype`, `statistic.qualified`, `statistic.context`, `sort`, `roster.positions`, `roster.athletes`, `team.athletes`, `powerindex.rundatetimekey`, `eventsback`, `eventsforward`, `eventsrange`, `eventstates`, `eventresults`, `seek`, `tournaments`, `competitions`, `competition.types`, `teams`, `situation.play`, `oldteams`, `newteams`, `played`, `period`, `position`, `filter`, `available`, `active`, `ids.sportware`, `profile`, `opponent`, `eventId`, `homeAway`, `season`, `athlete.position`, `postalCode`, `award.type`, `notes.type`, `tidbit.type`, `networks`, `bets.promotion`, `guids`, `competitors`, `source` |
| `https://sports.core.api.espn.com/v3/sports/{sport}/{league}` | `getLeague` | `page`, `limit`, `_hoist`, `_help`, `_trace`, `_nocache`, `enable`, `disable`, `pq`, `q`, `page`, `limit`, `lang`, `region`, `utcOffset`, `dates`, `weeks`, `advance`, `event.recurring`, `ids`, `type`, `types`, `seasontypes`, `calendar.type`, `calendar.groups`, `status`, `statuses`, `groups`, `provider`, `provider.priority`, `site`, `league.type`, `split`, `splits`, `record.splits`, `record.seasontype`, `statistic.splits`, `statistic.seasontype`, `statistic.qualified`, `statistic.context`, `sort`, `roster.positions`, `roster.athletes`, `team.athletes`, `powerindex.rundatetimekey`, `eventsback`, `eventsforward`, `eventsrange`, `eventstates`, `eventresults`, `seek`, `tournaments`, `competitions`, `competition.types`, `teams`, `situation.play`, `oldteams`, `newteams`, `played`, `period`, `position`, `filter`, `available`, `active`, `ids.sportware`, `profile`, `opponent`, `eventId`, `homeAway`, `season`, `athlete.position`, `postalCode`, `award.type`, `notes.type`, `tidbit.type`, `networks`, `bets.promotion`, `guids`, `competitors`, `source` |
| `https://sports.core.api.espn.com/v3/sports/{sport}/{league}/seasons/{season}` | `getSeason` | `page`, `limit`, `_hoist`, `_help`, `_trace`, `_nocache`, `enable`, `disable`, `pq`, `q`, `page`, `limit`, `lang`, `region`, `utcOffset`, `dates`, `weeks`, `advance`, `event.recurring`, `ids`, `type`, `types`, `seasontypes`, `calendar.type`, `calendar.groups`, `status`, `statuses`, `groups`, `provider`, `provider.priority`, `site`, `league.type`, `split`, `splits`, `record.splits`, `record.seasontype`, `statistic.splits`, `statistic.seasontype`, `statistic.qualified`, `statistic.context`, `sort`, `roster.positions`, `roster.athletes`, `team.athletes`, `powerindex.rundatetimekey`, `eventsback`, `eventsforward`, `eventsrange`, `eventstates`, `eventresults`, `seek`, `tournaments`, `competitions`, `competition.types`, `teams`, `situation.play`, `oldteams`, `newteams`, `played`, `period`, `position`, `filter`, `available`, `active`, `ids.sportware`, `profile`, `opponent`, `eventId`, `homeAway`, `season`, `athlete.position`, `postalCode`, `award.type`, `notes.type`, `tidbit.type`, `networks`, `bets.promotion`, `guids`, `competitors`, `source` |

---

## Site API Endpoints

> These use `site.api.espn.com` and return user-friendly data (scores, rosters, news, etc.)

```
GET https://site.api.espn.com/apis/site/v2/sports/golf/{league}/{resource}
```

| Resource | Description |
|----------|-------------|
| `scoreboard` | Live tournament scores |
| `scoreboard?dates={YYYYMMDD}` | Scores for a specific date range |
| `leaderboard?tournamentId={id}` | Tournament leaderboard |
| `news` | Latest news |
| `athletes/{id}/news` | Player-specific news |
| `summary?event={id}` | Tournament summary + results |

> ⚠️ **Slug required:** Golf scoreboard requires a named league slug — numeric IDs return 400.
> Use: `pga`, `lpga`, `liv`, `eur` (European Tour)

### Player Summary (Hole-by-Hole) — Web API

> ✅ **Live-verified 2026-07-04 (HTTP 200).** Per-round, per-hole scoring breakdown for a single player in a tournament.

```
GET https://site.web.api.espn.com/apis/site/v2/sports/golf/{tour}/leaderboard/{eventId}/playersummary?season={year}&player={playerId}
```

| Param | Description |
|-------|-------------|
| `{tour}` | Tour slug (`pga`, `lpga`, `liv`, `eur`) |
| `{eventId}` | Tournament/event ID (from the leaderboard/scoreboard) |
| `season` | Season year, e.g. `2026` |
| `player` | Athlete ID |

**Response structure** (verified 2026-07-04):

| Key | Type | Contents |
|-----|------|----------|
| `profile` | object | `id`, `uid`, `guid`, `displayName`, `age`, `dateOfBirth`, `college`, `hand`, `headshot`, `link`, `birthPlace`, `rank`, `earnings` |
| `rounds[]` | array | One entry per round played. Each has `value`, `displayValue`, `period` (round #), `inScore`, `outScore`, `courseId`, `startTee`, `groupNumber`, `teeTime`, `hasStream`, `currentPosition`, `linescores[]`, `statistics[]` |
| `rounds[].linescores[]` | array | **Per-hole scoring** — each hole: `value` (strokes), `displayValue`, `period` (hole #), `par`, `scoreType` → `{ name (e.g. PAR/BIRDIE), displayName, displayValue }` |
| `stats[]` | array | Player tournament stats — each: `{ name, displayName, displayValue }` (e.g. `tournamentsPlayed`) |

```bash
curl "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/401811952/playersummary?season=2026&player=4690755"
```

> 💡 The `{eventId}` is the same tournament ID returned by `site.api.espn.com/apis/site/v2/sports/golf/{tour}/scoreboard` (`events[].id`) and the `leaderboard` endpoint. `player` is the athlete `id` from the leaderboard's competitor list.

> ⚠️ **Injuries endpoint returns 500** for Golf — not supported.

> ⚠️ **`$ref` URLs may use internal domain:** Scoreboard and event responses may contain `$ref` URLs pointing to `sports.core.api.espn.pvt` — this is ESPN's internal domain and is not publicly accessible. Replace `.pvt` with `.com` to resolve. See [#20](https://github.com/pseudo-r/Public-ESPN-API/issues/20).

---

## Example API Calls

```bash
# PGA TOUR scoreboard
curl "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"

# LPGA scoreboard
curl "https://site.api.espn.com/apis/site/v2/sports/golf/lpga/scoreboard"

# LIV Golf scoreboard
curl "https://site.api.espn.com/apis/site/v2/sports/golf/liv/scoreboard"

# Get all golf leagues (core API)
curl "https://sports.core.api.espn.com/v2/sports/golf/leagues"

# PGA TOUR athletes (core API)
curl "https://sports.core.api.espn.com/v2/sports/golf/leagues/pga/athletes?limit=100&active=true"

# PGA TOUR events (core API)
curl "https://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events"
```

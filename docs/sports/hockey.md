# 🏒 Ice Hockey

> Ice hockey from the NHL, college, and international play.

**Sport slug:** `hockey`  
**Base URL (v2):** `https://sports.core.api.espn.com/v2/sports/hockey/`  
**Base URL (v3):** `https://sports.core.api.espn.com/v3/sports/hockey/`

---

## Leagues & Competitions

| Abbreviation | League Name | Slug | Full URL |
| --- | --- | --- | --- |
| `WCH` | World Cup of Hockey | `hockey-world-cup` | `https://sports.core.api.espn.com/v2/sports/hockey/leagues/hockey-world-cup` |
| `NCAAH` | NCAA Men's Ice Hockey | `mens-college-hockey` | `https://sports.core.api.espn.com/v2/sports/hockey/leagues/mens-college-hockey` |
| `NHL` | National Hockey League | `nhl` | `https://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl` |
| `MEN'S ICE HOCKEY` | Men's Ice Hockey | `olympics-mens-ice-hockey` | `https://sports.core.api.espn.com/v2/sports/hockey/leagues/olympics-mens-ice-hockey` |
| `WOMEN'S ICE HOCKEY` | Women's Ice Hockey | `olympics-womens-ice-hockey` | `https://sports.core.api.espn.com/v2/sports/hockey/leagues/olympics-womens-ice-hockey` |
| `CWHOC` | NCAA Women's Hockey | `womens-college-hockey` | `https://sports.core.api.espn.com/v2/sports/hockey/leagues/womens-college-hockey` |

---

## API Endpoints

> All endpoints below follow the pattern:  
> `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}<sub-path>`  
> Replace `{league}` with a league slug from the table above.

### Common Query Parameters

Most list endpoints support: `page` (int), `limit` (int). Additional filters are documented per endpoint.

### Seasons & Calendar

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/calendar` | `getCalendars` | `dates`, `page`, `limit`, `dates`, `groups`, `smartdates`, `advance`, `utcOffset`, `weeks`, `seasontype` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/seasons` | `getSeasons` | `page`, `limit`, `utcOffset`, `dates`, `start`, `end`, `eventsback`, `eventsforward`, `eventsrange`, `eventcompleted`, `groups`, `profile`, `competitions.types`, `types`, `season`, `weeks`, `tournamentId`, `dates`, `sort`, `type`, `date`, `group`, `position`, `week`, `qualified`, `types`, `limit`, `page`, `sort`, `position`, `status`, `sort`, `sortByRanks`, `stats`, `groupId`, `position`, `qualified`, `rookie`, `international`, `category`, `type`, `sort`, `sortByRanks`, `stats`, `groupId`, `qualified`, `category`, `sort`, `groupId`, `allStar`, `group`, `gender`, `types`, `country`, `association`, `lastNameInitial`, `lastName`, `active`, `statuses`, `sort`, `position`, `dates`, `groups`, `smartdates`, `advance`, `utcOffset`, `weeks`, `seasontype` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/seasons/{season}/athletes` | `getAthletes` | `active`, `sort`, `page`, `limit`, `seasontypes`, `played`, `teamtypes`, `group`, `gender`, `types`, `country`, `association`, `lastNameInitial`, `lastName`, `active`, `statuses`, `sort`, `position` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/seasons/{season}/draft` | `getDraftByYear` | `page`, `limit`, `available`, `position`, `team`, `sort`, `filter` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/seasons/{season}/freeagents` | `getFreeAgents` | `page`, `limit`, `types`, `oldteams`, `newteams`, `position`, `sort` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/seasons/{season}/manufacturers` | `getManufacturers` | `page`, `limit` |

### Teams

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/teams` | `getTeams` | `page`, `limit`, `utcOffset`, `dates`, `start`, `end`, `eventsback`, `eventsforward`, `eventsrange`, `eventcompleted`, `groups`, `profile`, `competitions.types`, `types`, `season`, `weeks`, `tournamentId`, `active`, `national`, `start`, `group`, `dates`, `recent`, `types`, `winnertype`, `date`, `eventsback`, `excludestatuses`, `includestatuses`, `dates`, `groups`, `smartdates`, `advance`, `utcOffset`, `weeks`, `seasontype` |

### Athletes / Players

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/athletes` | `getAthletes` | `page`, `limit`, `group`, `gender`, `types`, `country`, `association`, `lastNameInitial`, `lastName`, `active`, `statuses`, `sort`, `position` |

### Events / Games

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}` | `getEvent` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}/competitions/{competition}` | `getCompetition` | `page`, `limit`, `date`, `group`, `position`, `week`, `qualified`, `types`, `limit`, `page`, `types`, `period`, `sort`, `source`, `showsubplays` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}/competitions/{competition}/broadcasts` | `getBroadcasts` | `lang`, `region`, `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}/competitions/{competition}/competitors/{competitor}` | `getCompetitor` | `page`, `limit`, `date`, `group`, `position`, `week`, `qualified`, `types`, `limit`, `page` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}/competitions/{competition}/odds` | `getCompetitionOdds` | `provider.priority`, `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}/competitions/{competition}/officials` | `getOfficials` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/events/{event}/competitions/{competition}/plays/{play}/personnel` | `getPersonnel` | `page`, `limit` |

### News & Media

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/media` | `getMedia` | `page`, `limit` |

### Rankings & Awards

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/rankings` | `getRankings` | `page`, `limit` |

### Venues

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/venues` | `getVenues` | `page`, `limit` |

### Other

| Endpoint | Method ID | Query Params |
| --- | --- | --- |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/casinos` | `getCasinos` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/circuits` | `getCircuits` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/countries` | `getCountries` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/franchises` | `getFranchises` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/positions` | `getPositions` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/providers` | `getProviders` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/recruiting` | `getRecruitingSeasons` | `page`, `limit`, `sort`, `position`, `status` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/season` | `getCurrentSeason` | `page`, `limit` |
| `https://sports.core.api.espn.com/v2/sports/hockey/leagues/{league}/tournaments` | `getTournaments` | `majorsOnly`, `page`, `limit` |

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
GET https://site.api.espn.com/apis/site/v2/sports/hockey/{league}/{resource}
```

| Resource | Description |
|----------|-------------|
| `scoreboard` | Live scores & schedules |
| `scoreboard?dates={YYYYMMDD}` | Scores for a specific date |
| `teams` | All teams |
| `teams/{id}` | Single team |
| `teams/{id}/roster` | Team roster |
| `teams/{id}/schedule` | Team schedule |
| `teams/{id}/injuries` | Injury report |
| `standings` | League standings |
| `injuries` | Injuries across the league |
| `news` | Latest news |
| `summary?event={id}` | Full game summary |

---

## Example API Calls

```bash
# NHL scoreboard (today)
curl "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"

# NHL scoreboard for a specific date
curl "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates=20250415"

# NHL standings
curl "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/standings"

# Toronto Maple Leafs roster
curl "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/28/roster"

# Toronto Maple Leafs injuries
curl "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/28/injuries"

# College Hockey Men scoreboard
curl "https://site.api.espn.com/apis/site/v2/sports/hockey/mens-college-hockey/scoreboard"

# Get all hockey leagues (core API)
curl "https://sports.core.api.espn.com/v2/sports/hockey/leagues"

# NHL teams (core API)
curl "https://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/teams?limit=50"

# NHL athletes (core API)
curl "https://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/athletes?limit=100&active=true"

# NHL standings (core API)
curl "https://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/standings"
```

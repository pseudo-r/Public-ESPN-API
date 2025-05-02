## DISCLAIMER: 

This is a public API provided by ESPN, and I am not affiliated with ESPN or responsible for any usage of this API. This information is provided solely for educational and informational purposes. Please use this API responsibly and abide by ESPN's terms of service.

# Comprehensive Guide to Community-Discovered ESPN API Endpoints

## 1. Introduction

### 1.1. Purpose

This document provides a consolidated and expanded collection of known ESPN Application Programming Interface (API) endpoints, compiled from publicly available, community-driven resources. Its objective is to serve as a comprehensive reference for developers seeking to interact with ESPN's data programmatically, potentially supplementing or replacing existing unofficial documentation found in community repositories such as `pseudo-r/Public-ESPN-API`.[1, 2] The information presented herein is derived from analysis of various community findings, including GitHub Gists and repositories.[3, 4, 5, 6, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

### 1.2. Crucial Caveat: The Unofficial Nature of the ESPN API

It is imperative to understand that ESPN does not offer an officially supported, publicly documented API for general developer consumption.[12, 13, 14, 15, 19, 17, 20, 21, 22] The endpoints detailed in this guide are considered "hidden" or "undocumented." They have been primarily identified through the process of reverse-engineering, specifically by observing the network requests made by ESPN's own web properties (e.g., `espn.com`) and mobile applications.[7, 12, 14, 15, 23, 17, 20, 18]

This unofficial status carries significant implications and risks for developers:

*   **Instability:** As these APIs are not intended for public use, ESPN may modify, deprecate, or remove them entirely without any prior notification. Changes to endpoint paths, parameters, or response structures can occur unexpectedly, leading to broken functionality in applications relying on them.[13, 24, 17] Base URLs for services like the Fantasy API have been observed to change over time.[24, 17]
*   **Lack of Support:** ESPN provides no official documentation, developer support, or service level agreements (SLAs) for these endpoints.[13, 19, 17, 21] Developers are reliant on community knowledge and troubleshooting.
*   **Terms of Service:** Utilizing these APIs might contravene ESPN's Terms of Service, potentially leading to access restrictions or other actions if usage is detected and deemed inappropriate.[19, 20]

Given these factors, developers should exercise caution. It is strongly recommended to implement robust error handling mechanisms, employ defensive coding practices (e.g., validating response structures before processing), and avoid relying solely on these undocumented APIs for critical systems or commercial applications where stability and guaranteed access are essential.[13, 17, 18] Community-driven resources, including GitHub repositories, Gists, and wrapper libraries (available for languages like Python, R, and JavaScript), remain the primary source of information and updates regarding these endpoints.[3, 4, 5, 6, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 16, 17, 18]

### 1.3. How to Discover Endpoints

A common technique employed by the community to identify and understand these endpoints involves using web browser developer tools. By monitoring the "Network" tab (often filtering for XHR or Fetch requests) while navigating and interacting with `espn.com` or its fantasy sports platform, developers can observe the API calls being made in the background, including the target URLs, request methods, parameters, and response payloads.[7, 12, 14, 15, 23, 20, 18] This method of discovery, while effective, further underscores that the APIs were likely designed for internal consumption by ESPN's own front-end applications rather than as a stable, documented interface for external developers. The necessity of such reverse-engineering implies a higher potential for unannounced changes compared to formally documented APIs.

## 2. Core API Domains (Base URLs)

Analysis of community findings reveals that ESPN utilizes several distinct API subdomains. This segmentation likely reflects different backend services, API generations, or specific functional areas within ESPN's infrastructure. Understanding these domains is the first step in targeting the correct service for desired data.

The presence of multiple distinct API domains, such as `site.api.espn.com` often associated with general website data (scores, news) and `sports.core.api.espn.com` frequently linked to deeper statistical or structural data (athletes, seasons, odds), points towards a potentially segmented backend architecture.[3, 4, 5, 6, 2, 7, 8, 9, 10, 13, 15, 23, 16] Developers should be aware that data consistency or update timing across these different domains might vary. For instance, data might appear on a core endpoint slightly before or after it appears on a site-facing endpoint.

**Table 1: Identified ESPN API Base URLs**

| Base URL | Likely Purpose/Data Type | Key References |
| :------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :---------------------- |
| `site.api.espn.com` | General site data: Scores, news, teams, summaries, standings, basic league/sport info. | [3, 4, 5, 6, 2, 7, 9, 13, 23, 16] |
| `sports.core.api.espn.com` | Core sports data: Athletes, seasons, detailed stats, odds, probabilities, venues, franchises, deeper game details (plays). | [3, 4, 6, 8, 10, 15] |
| `site.web.api.espn.com` | Web-specific APIs: Search, headers, athlete overviews/gamelogs/splits, possibly newer/different structures for web use. | [3, 6, 2, 8, 16] |
| `fantasy.espn.com` | Fantasy sports data (FFL, etc.). Base URL for current season (>2018). Note: Prone to changes. | [3, 6, 7, 12, 14, 15, 24, 17] |
| `lm-api-reads.fantasy.espn.com` | Fantasy sports data. Observed as a base URL, potentially for reads or specific fantasy versions/years. | [6, 7, 12, 14] |
| `cdn.espn.com` | Content Delivery Network: Delivers core data (scoreboards, schedules, standings, game details) possibly optimized for speed. | [6] |
| `now.core.api.espn.com` | Real-time or breaking news feeds. | [6] |
| `partners.api.espn.com` | Likely intended for official partners; may offer different data sets or stability (publicly undocumented). | [6] |
| `gambit-api.fantasy.espn.com` | Specific API for "Pick'em" style fantasy games/challenges. | [6] |

## 3. Common Parameters and Headers

Across the various ESPN API endpoints, several common patterns emerge regarding path parameters, query string parameters, and HTTP headers.

### 3.1. Path Parameters

These are placeholders within the URL path that specify the exact resource being requested. Common placeholders include:

*   `{sport}`: Identifies the sport (e.g., `football`, `basketball`, `baseball`, `soccer`, `hockey`). [2]
*   `{league}`: Identifies the league within a sport (e.g., `nfl`, `college-football`, `nba`, `mlb`, `nhl`, `eng.1` for English Premier League soccer). [5, 2, 9]
*   `{team_id}` or `{team}`: Identifies a specific team, usually by a numerical ID, but sometimes by an abbreviation (especially in older or college sports endpoints). [3, 4, 5, 6, 2, 7, 8, 9, 16]
*   `{athlete_id}` or `{id}`: Identifies a specific player/athlete, typically by a numerical ID. [3, 6, 2, 8, 10, 16]
*   `{game_id}` or `{event_id}`: Identifies a specific game or event, usually by a numerical ID. [3, 5, 6, 7, 8, 9, 10]
*   `{year}` or `{season}`: Specifies the season year (e.g., `2023`). [3, 4, 6, 2, 7, 8, 10]
*   `{seasontype}`: Specifies the type of season (e.g., `1` for preseason, `2` for regular season, `3` for postseason). [3, 4, 6, 8, 10, 25]
*   `{week}` or `{week_num}` or `{weeknum}`: Specifies the week number within a season. [3, 6, 8]
*   `{tour}`: Used in Tennis endpoints to specify the tour (e.g., `atp`, `wta`). [2]
*   `{bet_provider_id}`: Numerical ID for a specific sportsbook providing odds. [3, 6]

### 3.2. Query Parameters

These are appended to the URL after a `?` and provide filtering, pagination, or modification instructions. Common query parameters include:

*   `limit`: Controls the maximum number of items returned in a list (e.g., `limit=1000` is often used to attempt retrieving all items). [3, 6, 8, 10, 15]
*   `dates`: Filters results by date or date range. Formats observed include `YYYYMMDD`, `YYYYMMDD-YYYYMMDD`, and `YYYY`. [3, 5, 6, 7, 8, 9]
*   `season`, `seasontype`, `week`: Used for filtering scoreboard, schedule, or statistical data by time period. [3, 6, 2, 8, 10]
*   `group` or `groups`: Filters by conference or division ID, particularly relevant for college sports (Note: inconsistency observed, sometimes `group=ID`, sometimes `groups=ID`). [4, 15]
*   `view`: Critically important for the Fantasy API. Specifies the type or "view" of data to return for a league (e.g., `mTeam`, `mRoster`, `mDraftDetail`, `kona_player_info`). Multiple `view` parameters can sometimes be combined. [3, 6, 7, 12, 14, 15, 24, 17]
*   `enable`: Used in some `site.api.espn.com` endpoints (like team details) to request inclusion of additional related data sections in the response (e.g., `enable=roster,projection,stats`). [3, 4, 6]
*   `active=true`: Filters athlete lists to include only currently active players. [3, 6]
*   `xhr=1`: Frequently observed with `cdn.espn.com` endpoints. Likely signifies an XMLHttpRequest (AJAX) request, instructing the server to return data (e.g., JSON) rather than a full HTML page. [6]
*   `query`: Used in search endpoints to specify the search term. [3, 6, 8]
*   `calendar`: Used with some college football scoreboard endpoints (e.g., `calendar=blacklist`). [5, 7, 8, 9]

The existence and usage of parameters like `view` and `enable` suggest that certain endpoints are designed with flexibility for ESPN's internal front-end applications. Rather than adhering strictly to REST principles where each resource type might have its own dedicated endpoint (e.g., `/teams/{id}/roster`, `/teams/{id}/stats`), these parameters allow a single endpoint (e.g., `/teams/{id}`) to serve varied data payloads by bundling related information.[3, 4, 6] This approach can reduce the number of network requests needed by a client but makes the API less predictable and discoverable for third-party developers compared to more granular, resource-oriented designs.

### 3.3. HTTP Headers

While many requests may work without special headers, some are crucial, particularly for the Fantasy API:

*   `X-Fantasy-Filter`: Used exclusively with Fantasy API endpoints. Takes a JSON string as its value, allowing for complex filtering (e.g., by player ID, stat ID, scoring period), sorting, and pagination/limiting of the response data. [7, 12, 14, 15, 19, 22]
*   `Accept: application/json`: A standard HTTP header indicating that the client prefers the response in JSON format. While often not strictly required (as the API usually defaults to JSON), it's good practice to include it.[13, 17]
*   Authentication Headers/Cookies: For accessing private fantasy leagues, authentication cookies (`espn_s2`, `SWID`) obtained through a login process are necessary and typically handled by wrapper libraries or manual request crafting. Public league data generally does not require authentication.[7, 12, 14, 15]

## 4. General & Cross-Sport Endpoints

These endpoints provide foundational information or functionality that spans multiple sports or leagues. They are often starting points for discovering available data or performing broad searches.

**Table 2: General API Endpoints**

| Function | Base URL | Path | Key Parameters | Example / Notes | References |
| :----------------------- | :----------------------- | :---------------------------------------------------------------- | :-------------------------------- | :---------------------------------------------------------------------------------------- | :--------------- |
| List All Sports | `site.api.espn.com` | `/apis/site/v2/sports` | - | `http://site.api.espn.com/apis/site/v2/sports` | [2] |
| List Leagues (Sport) | `site.api.espn.com` | `/apis/site/v2/sports/{sport}` | `{sport}` | `https://site.api.espn.com/apis/site/v2/sports/football` | [2] |
| General Search (v3) | `site.web.api.espn.com` | `/apis/common/v3/search` | `query`, `limit`, `mode` | `.../search?query=nfl&limit=5&mode=prefix` | [3, 6] |
| Search (v2) | `site.web.api.espn.com` | `/apis/search/v2` | `query`, `limit` | `.../search/v2?limit=100&query=Tom+Brady` | [6] |
| Calendar - Ondays | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/calendar/ondays` | `{sport}`, `{league}` | `.../football/leagues/nfl/calendar/ondays` | [6] |
| Calendar - Offdays | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/calendar/offdays` | `{sport}`, `{league}` | `.../football/leagues/nfl/calendar/offdays` | [6] |
| Calendar - Whitelist | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/calendar/whitelist` | `{sport}`, `{league}` | `.../football/leagues/nfl/calendar/whitelist` | [6, 10] |
| Calendar - Blacklist | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/calendar/blacklist` | `{sport}`, `{league}` | `.../football/leagues/nfl/calendar/blacklist` | [6, 10] |
| List Venues | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/venues` | `{sport}`, `{league}`, `limit` | `.../football/leagues/nfl/venues?limit=700` | [6] |
| List Franchises | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/franchises` | `{sport}`, `{league}`, `limit` | `.../football/leagues/nfl/franchises?limit=50` | [4, 6] |
| List Seasons | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/seasons` | `{sport}`, `{league}`, `limit` | `.../football/leagues/nfl/seasons?limit=100` | [4, 6, 8] |
| Get Season Details | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/seasons/{year}` | `{sport}`, `{league}`, `{year}` | `.../football/leagues/nfl/seasons/2023` | [4, 6, 8, 10] |
| List Weeks for Season | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/seasons/{year}/types/{st}/weeks` | `{sport}`, `{league}`, `{year}`, `{st}` | `.../nfl/seasons/2023/types/2/weeks` (`st` = seasontype) | [4, 6, 8, 10] |
| Get Week Details | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/seasons/{year}/types/{st}/weeks/{wn}` | `{sport..wn}` | `.../nfl/seasons/2023/types/2/weeks/1` (`wn` = weeknum) | [6, 8, 10] |
| List Events (Games) | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/events` | `{sport}`, `{league}`, `dates`, `limit` | `.../football/leagues/nfl/events?dates=2023` | [4, 6, 8, 10] |
| List Events by Week | `sports.core.api.espn.com` | `/v2/sports/{sport}/leagues/{league}/seasons/{year}/types/{st}/weeks/{wk}/events` | `{sport..wk}` | `.../nfl/seasons/2023/types/2/weeks/1/events` | [4, 6, 8, 10] |
| List News (League) | `site.api.espn.com` | `/apis/site/v2/sports/{sport}/{league}/news` | `{sport}`, `{league}`, `limit` | `.../football/nfl/news?limit=50` | [3, 4, 5, 6, 2, 7, 9, 16] |
| News Feed (Now) | `now.core.api.espn.com` | `/v1/sports/news` | `sport`, `limit` | `.../news?limit=1000&sport=football` (Provides links to events) | [6] |
| Scoreboard Header | `site.web.api.espn.com` | `/apis/v2/scoreboard/header` | `sport`, `league` | `.../header?sport=football&league=nfl` | [3, 6] |

## 5. Sport-Specific Endpoints

While many API structures are similar across sports, specific endpoints, parameters, and data availability can vary. The following sections detail endpoints discovered for major sports leagues. The general pattern often follows `/{base_url}/apis/{version}/{domain}/{sport}/{league}/{resource}`.[5, 2, 7, 9, 23, 16, 18] However, variations exist, such as the use of league abbreviations in soccer paths [5, 2, 9] or team abbreviations in some college sports endpoints [5, 7, 9], requiring careful attention to the specific sport being queried.

### 5.1. Football (NFL)

The NFL is extensively covered in the discovered API endpoints, reflecting its popularity. Data spans scores, schedules, team information, player statistics, game details, news, and draft information. Many examples across the different base URLs (`site.api`, `sports.core.api`, `site.web.api`, `cdn.espn`) relate to the NFL.[3, 4, 5, 6, 2, 7, 8, 9, 10, 13, 15, 23, 16]

**Table 3: Selected NFL API Endpoints**

| Function | Base URL | Path | Key Parameters | Notes / Example | References |
| :----------------------- | :----------------------- | :------------------------------------------------------------------------- | :-------------------------------- | :---------------------------------------------------------------------------------- | :--------------- |
| Scoreboard (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/scoreboard` | `dates`, `week`, `seasontype` | `...?dates=2023&seasontype=2&week=1` | [3, 5, 6, 2, 7, 9, 13, 23, 16] |
| Scoreboard (CDN) | `cdn.espn.com` | `/core/nfl/scoreboard` | `xhr=1`, `limit` | `...?xhr=1&limit=50` (Live updates) | [6] |
| Schedule (CDN) | `cdn.espn.com` | `/core/nfl/schedule` | `xhr=1`, `year`, `week` | `...?xhr=1&year=2023&week=1` | [6] |
| Standings (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/standings` | `season` | `...?season=2023` | [2] |
| Standings (CDN) | `cdn.espn.com` | `/core/nfl/standings` | `xhr=1` | `...?xhr=1` | [6] |
| Conference Standings | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/types/{st}/groups/{id}/standings` | `{yr}`, `{st}`, `{id}` | `{id}`=7 (NFC), 8 (AFC) | [6, 10] |
| List Teams (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/teams` | - | Provides list with IDs, names, logos | [5, 6, 2, 7, 9, 16] |
| Get Team (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/teams/{team_id}` | `{team_id}` | `.../teams/1` (Team ID or Abbreviation sometimes works) | [5, 6, 7, 9, 10, 16] |
| Get Team (Core API) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/teams/{team_id}` | `{yr}`, `{team_id}` | Provides core team data for a season | [3, 4, 6] |
| Team Roster (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/teams/{team_id}/roster` | `{team_id}`, `enable` | `...?enable=roster,projection,stats` for detailed view | [3, 4, 6, 2] |
| Team Schedule (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/teams/{team_id}/schedule` | `{team_id}`, `season` | `...?season=2023` | [3, 4, 6, 2] |
| Team Injuries | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/teams/{team_id}/injuries` | `{team_id}` | | [6, 10] |
| Team Depth Chart | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/teams/{team_id}/depthcharts` | `{yr}`, `{team_id}` | | [3, 4, 6] |
| List Athletes (Core API) | `sports.core.api.espn.com` | `/v3/sports/football/nfl/athletes` | `limit`, `active=true`, `page` | `...?limit=20000&active=true` (v3 endpoint) | [6] |
| Athlete Overview | `site.web.api.espn.com` | `/apis/common/v3/sports/football/nfl/athletes/{ath_id}/overview` | `{ath_id}` | Comprehensive player overview | [6] |
| Athlete Gamelog | `site.web.api.espn.com` | `/apis/common/v3/sports/football/nfl/athletes/{ath_id}/gamelog` | `{ath_id}` | Player stats per game | [6, 10] |
| Athlete Eventlog | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/athletes/{ath_id}/eventlog` | `{yr}`, `{ath_id}` | Log of events/stats for a player in a season | [3, 6, 10] |
| Athlete Splits | `site.web.api.espn.com` | `/apis/common/v3/sports/football/nfl/athletes/{ath_id}/splits` | `{ath_id}` | Player stats broken down by various conditions | [6, 10] |
| Game Summary (Site API) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/summary` | `event={event_id}` | Key game details, box score info | [4, 6, 2] |
| Game Boxscore (CDN) | `cdn.espn.com` | `/core/nfl/boxscore` | `xhr=1`, `gameId={event_id}` | Detailed box score data | [6] |
| Game Play-by-Play (CDN) | `cdn.espn.com` | `/core/nfl/playbyplay` | `xhr=1`, `gameId={event_id}` | Detailed play list | [6] |
| Game Plays (Core API) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/plays` | `{eid}`, `limit` | `{eid}`=event_id, `limit=300`+ recommended | [3, 6, 10] |
| Game Drives (Core API) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/drives` | `{eid}` | Drive summaries for the game | [6] |
| Leaders (Site API v3) | `site.api.espn.com` | `/apis/site/v3/sports/football/nfl/leaders` | `season`, `seasontype` | League leaders for various stats | [3, 6, 10] |
| Leaders (Core API) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/types/{st}/leaders` | `{yr}`, `{st}` | Season leaders | [6, 10] |
| Draft | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/draft` | `{yr}` | Draft results | [4, 6, 8, 10] |
| News (Team Specific) | `site.api.espn.com` | `/apis/site/v2/sports/football/nfl/news` | `team={team_id}` | News filtered for a specific team | [6] |
| Specific Nights | `site.api.espn.com` | `/apis/site/v2/{night}nightfootball` | - | `{night}` = `monday`, `thursday`, `sunday` | [6] |

### 5.2. Football (College)

College football shares similarities with the NFL structure but includes unique elements like rankings and conference/group filtering. Some endpoints may also accept team abbreviations instead of numerical IDs.[5, 7, 9] A notable issue was reported where the query parameter `group=ID` returned default results, while `groups=ID` worked correctly for filtering scoreboards by conference.[15]

**Table 4: Selected College Football API Endpoints**

| Function | Base URL | Path | Key Parameters | Notes / Example | References |
| :----------------------- | :------------------ | :---------------------------------------------------------------- | :-------------------------------- | :------------------------------------------------------------------ | :--------------- |
| Scoreboard | `site.api.espn.com` | `/apis/site/v2/sports/football/college-football/scoreboard` | `dates`, `groups`, `week` | `...?groups=8&week=5` (Group 8 = SEC) | [3, 5, 7, 9, 23] |
| Rankings | `site.api.espn.com` | `/apis/site/v2/sports/football/college-football/rankings` | - | AP Top 25, Coaches Poll, CFP Rankings | [5, 7, 9] |
| List Teams | `site.api.espn.com` | `/apis/site/v2/sports/football/college-football/teams` | - | List of college teams | [5, 7, 9] |
| Get Team | `site.api.espn.com` | `/apis/site/v2/sports/football/college-football/teams/:team` | `:team` (abbreviation) | `.../teams/gt` (Georgia Tech) | [5, 7, 9] |
| News | `site.api.espn.com` | `/apis/site/v2/sports/football/college-football/news` | - | Latest college football news | [5, 2, 7, 9] |
| Game Summary | `site.api.espn.com` | `/apis/site/v2/sports/football/college-football/summary` | `event={gameId}` | `...?event=400934572` (2017 Army-Navy) | [5, 7, 9] |
| Season Info | `site.api.espn.com` | `/apis/common/v3/sports/football/college-football/season` | - | Provides season start/end dates, types (pre, regular, post) | [7] |
| Core League Info | `sports.core.api.espn.com` | `/v2/sports/football/leagues/college-football/` | - | Root endpoint for core college football data | [15] |

### 5.3. Basketball (NBA)

NBA endpoints follow the common structure observed for major professional leagues.[5, 2, 7, 9, 23, 16, 18]

**Table 5: Selected NBA API Endpoints**

| Function | Base URL | Path | Key Parameters | Notes / Example | References |
| :----------------------- | :------------------ | :-------------------------------------------------------- | :---------------------- | :-------------------------------------------- | :--------------- |
| Scoreboard | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/scoreboard` | `dates` | `...?dates=YYYYMMDD` | [5, 7, 9, 23, 16] |
| List Teams | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/teams` | - | | [5, 2, 7, 9, 16] |
| Get Team | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/teams/:team` | `:team` (ID or Abbrev) | `.../teams/lal` or `.../teams/13` (Lakers) | [5, 7, 9, 16] |
| Team Roster | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/{team}/roster` | `{team}` (ID or Abbrev) | | [2] |
| Team Schedule | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/{team}/schedule` | `{team}`, `season` | | [2] |
| List Players | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/players` | - | | [2] |
| Player Stats | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/statistics/players` | - | Aggregate player statistics | [2] |
| News | `site.api.espn.com` | `/apis/site/v2/sports/basketball/nba/news` | - | | [5, 7, 9, 16] |

### 5.4. Basketball (WNBA)

Endpoints for the WNBA mirror the NBA structure.[5, 7, 9, 23, 18]

*   **Scores:** `http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard` [5, 7, 9, 23]
*   **News:** `http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/news` [5, 7, 9]
*   **All Teams:** `http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams` [5, 7, 9]
*   **Specific Team:** `http://site.api.espn.com/apis/site/v2/sports/basketball/wnba/teams/:team` [5, 7, 9]

### 5.5. Basketball (College - Men's & Women's)

Both Men's and Women's college basketball follow similar endpoint patterns, distinguished by `mens-college-basketball` or `womens-college-basketball` in the path.[5, 7, 9, 23, 18] Specific endpoints for bracketology have also been identified, although their reliability for recent years may be questionable.[8]

*   **Scores (Men's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard` [5, 7, 9, 23]
*   **News (Men's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/news` [5, 7, 9]
*   **Teams (Men's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams` [5, 7, 9]
*   **Specific Team (Men's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/:team` [5, 7, 9]
*   **Scores (Women's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard` [5, 7, 9, 23]
*   **News (Women's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/news` [5, 7, 9]
*   **Teams (Women's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/teams` [5, 7, 9]
*   **Specific Team (Women's):** `http://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/teams/:team` [5, 7, 9]
*   **Bracketology (Men's - Historical):** `http://sports.core.api.espn.com/v2/sports/basketball/leagues/mens-college-basketball/tournaments/22/seasons/${season}/bracketology` (Reported working up to 2021) [8]
*   **Bracket Fastcast (Men's):** `https://fcast.espncdn.com/FastcastService/pubsub/profiles/12000/topic/bracket-basketball-mens-college-basketball-22-en/message/24624/checkpoint` (Observed endpoint) [8]

### 5.6. Baseball (MLB)

MLB endpoints are available for standard data types like scores, teams, players, and news.[5, 2, 7, 9, 23, 16, 18]

**Table 6: Selected MLB API Endpoints**

| Function | Base URL | Path | Key Parameters | Notes / Example | References |
| :----------------------- | :----------------------- | :-------------------------------------------------------- | :--------------------- | :-------------------------------------------- | :--------------- |
| Scoreboard | `site.api.espn.com` | `/apis/site/v2/sports/baseball/mlb/scoreboard` | `dates` | `...?dates=YYYYMMDD` | [5, 7, 9, 23, 16] |
| List Teams | `site.api.espn.com` | `/apis/site/v2/sports/baseball/mlb/teams` | - | | [5, 2, 7, 9, 16] |
| Get Team | `site.api.espn.com` | `/apis/site/v2/sports/baseball/mlb/teams/:team` | `:team` (ID or Abbrev) | | [5, 7, 9, 16] |
| List Players | `site.api.espn.com` | `/apis/site/v2/sports/baseball/mlb/players` | - | | [2] |
| Player Stats (Aggregate) | `site.api.espn.com` | `/apis/site/v2/sports/baseball/mlb/statistics/players` | - | | [2] |
| Player Details | `site.web.api.espn.com` | `/apis/common/v3/sports/baseball/mlb/athletes/{ath_id}` | `{ath_id}` | `.../athletes/5883` (Zack Greinke) | [16] |
| News | `site.api.espn.com` | `/apis/site/v2/sports/baseball/mlb/news` | - | | [5, 7, 9, 16] |

### 5.7. Baseball (College)

Endpoints for college baseball include scores and season information.[5, 7, 9, 23, 18]

*   **Scores:** `https://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/scoreboard` [5, 9, 23, 18]
*   **Season Info:** `http://site.api.espn.com/apis/common/v3/sports/baseball/college-baseball/season` [7]

### 5.8. Hockey (NHL)

Standard endpoints exist for the NHL.[5, 2, 7, 9, 23, 18]

*   **Scores:** `http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard` [5, 7, 9, 23]
*   **News:** `http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/news` [5, 7, 9]
*   **All Teams:** `http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams` [5, 7, 9]
*   **Specific Team:** `http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/:team` [5, 7, 9]
*   **Players:** `https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/players` [2]
*   **Player Stats:** `https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/statistics/players` [2]

### 5.9. Soccer

Soccer endpoints often require a specific league abbreviation within the path (e.g., `eng.1` for Premier League, `usa.1` for MLS, `UEFA.EUROPA` for Europa League).[5, 2, 8, 9, 23, 18] This differs from sports like NFL or NBA where the league is typically part of the base path segment.

**Table 7: Selected Soccer API Endpoints**

| Function | Base URL | Path | Key Parameters | Notes / Example | References |
| :----------------------- | :------------------ | :----------------------------------------------------------------- | :-------------------------------- | :---------------------------------------------------------------------------- | :--------------- |
| List Leagues | `site.api.espn.com` | `/apis/site/v2/sports/soccer` | - | Provides a list of available soccer leagues and their slugs | [2] |
| Scoreboard / Schedule | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{league}/scoreboard` | `{league}`, `dates` | `{league}`=e.g., `eng.1`, `usa.1` | [5, 2, 9, 23] |
| Team Schedule | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{competition}/teams/{teamId}/schedule`| `{competition}`, `{teamId}` | `{competition}`=e.g., `UEFA.EUROPA` | [8] |
| Standings | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{league}/standings` | `{league}`, `season` | `...?season=YYYY` | [2] |
| List Teams | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{league}/teams` | `{league}` | | [5, 9] |
| List Players | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{league}/players` | `{league}` | | [2] |
| Player Stats | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{league}/statistics/players` | `{league}` | | [2] |
| News | `site.api.espn.com` | `/apis/site/v2/sports/soccer/{league}/news` | `{league}` | | [5, 9, 16] |

### 5.10. Other Sports (Golf, Racing, Tennis, etc.)

While less extensively documented in the analyzed sources, endpoints likely exist for other sports covered by ESPN, often following similar structural patterns.

*   **Golf:** Leagues mentioned include `pga`, `lpga`, `eur`, `ntw`, `champions-tour`, `mens-olympics-golf`.[3] Endpoints would likely follow patterns like `.../sports/golf/{league}/...`.
*   **Racing:** Leagues mentioned include `f1`, `irl`, `nascar-premier`, `nascar-secondary`, `nascar-truck`, `nhra`.[3] Endpoints would likely follow patterns like `.../sports/racing/{league}/...`.
*   **Tennis:** Endpoints for players and stats exist, using a `{tour}` parameter (e.g., `atp`, `wta`).
    *   Players: `https://site.api.espn.com/apis/site/v2/sports/tennis/{tour}/players` [2]
    *   Player Stats: `https://site.api.espn.com/apis/site/v2/sports/tennis/{tour}/statistics/players` [2]
*   **Other Hockey:** Leagues like `mens-college-hockey`, `womens-college-hockey`, `hockey-world-cup`, `mens-olympic-hockey`, `womens-olympic-hockey` are mentioned [3], suggesting specific endpoints exist.

Developers interested in these or other sports should explore using the identified base URLs and adapt the patterns observed for the major sports, potentially using browser developer tools to confirm specific paths and parameters.[7, 12, 14, 15, 23, 20, 18]

## 6. Fantasy Sports API Endpoints

ESPN's Fantasy Sports platform utilizes a distinct set of API endpoints, primarily under the `fantasy.espn.com` or related domains like `lm-api-reads.fantasy.espn.com`.[3, 6, 7, 12, 14, 15, 24, 17] Accessing private league data typically requires authentication using cookies (`espn_s2`, `SWID`) obtained after user login.[7, 12, 14, 15] Public league data is generally accessible without authentication.

A key characteristic of the Fantasy API is its heavy reliance on the `view` query parameter to specify the desired data payload.[3, 6, 7, 12, 14, 15, 24, 17] Instead of numerous specific endpoints for different data types (like settings, roster, draft), a base league endpoint is often used, and the `view` parameter dictates the content of the response. Multiple `view` parameters can sometimes be included in a single request.[7, 14]

Furthermore, the `X-Fantasy-Filter` HTTP header plays a crucial role in enabling server-side filtering, sorting, and pagination of data, particularly for large datasets like player information.[7, 12, 14, 15, 19, 22] This header accepts a JSON string specifying the filtering criteria.

The structure, reliance on `view` parameters, and use of a custom filter header deviate significantly from typical REST API conventions. This suggests an API design optimized for the specific needs and efficiency of ESPN's own complex fantasy web application, likely minimizing network round trips by bundling data based on views. However, this makes the API less intuitive and discoverable for external developers, often necessitating the use of community-developed wrapper libraries (e.g., Python's `espn-api` [7, 13, 14, 24], R's `ffscrapr` [7, 12, 14, 15, 19, 22], or JavaScript clients [12, 14]) that encapsulate these complexities.

Base URLs for the Fantasy API have also shown instability, with different URLs used for historical versus current seasons, and documented changes in the base URL over time.[7, 12, 14, 15, 24, 17] Developers should be prepared for potential future changes.

**Table 8: Selected Fantasy API Endpoints (FFL Example)**

| Function | Base URL Pattern | Path/Query Structure | Key Parameters/Headers | Notes | References |
| :------------------------------ | :------------------------------------ | :--------------------------------------------------------------------------------- | :---------------------------------------------------------- | :--------------------------------------------------------------------- | :------------------ |
| League Data (Current >2018) | `fantasy.espn.com` | `/apis/v3/games/ffl/seasons/{yr}/segments/0/leagues/{id}` | `view={view_name}`, `X-Fantasy-Filter` | Base endpoint for recent seasons. Check for latest base URL. | [3, 7, 12, 14, 15, 24, 17] |
| League Data (Historical <2018) | `fantasy.espn.com` | `/apis/v3/games/ffl/leagueHistory/{id}?seasonId={yr}` | `view={view_name}`, `X-Fantasy-Filter` | Separate endpoint for older seasons. Check for latest base URL. | [3, 7, 12, 14, 15, 24, 17] |
| Player Info List | `fantasy.espn.com` | `/apis/v3/games/ffl/seasons/{yr}/players?view=players_wl` | `view=players_wl`, `X-Fantasy-Filter` (for filtering) | Retrieves list of players available in the fantasy game for the season. | [3, 6] |
| Player Info Detailed | `fantasy.espn.com` | `/apis/v3/games/ffl/seasons/{yr}/segments/0/leaguedefaults/{PPR_ID}?view=kona_player_info` | `view=kona_player_info`, `X-Fantasy-Filter` | Provides rich player data including stats, projections. `{PPR_ID}` may vary. | [3, 6, 7, 12, 14, 15, 17] |
| Team Bye Weeks | `fantasy.espn.com` | `/apis/v3/games/ffl/seasons/{yr}?view=proTeamSchedules_wl` | `view=proTeamSchedules_wl` | Includes NFL team schedules, useful for determining bye weeks. | [3, 6] |
| Player News (Fantasy) | `site.api.espn.com` | `/apis/fantasy/v2/games/ffl/news/players` | `playerId={ath_id}`, `limit` | News specifically curated for fantasy players. | [6] |
| Fantasy Games List (v2) | `site.web.api.espn.com` | `/apis/fantasy/v2/games/ffl/games` | `dates=YYYYMMDD` or `YYYYMMDD-YYYYMMDD` | Lists games relevant to fantasy context for given dates. | [3, 6] |
| Get % Owned Players | `fantasy.espn.com` | `/apis/v3/games/ffl/seasons/{yr}/players?scoringPeriodId=0&view=players_wl` | `view=players_wl`, `X-Fantasy-Filter` (filter by player id) | Use filter to get specific player ownership percentages. | [3, 6] |
| Pick'em Challenge Scoring | `gambit-api.fantasy.espn.com` | `/apis/v1/challenges/{chal_name}?scoringPeriodId={wk}&view={view}` | `{chal_name}`, `{wk}`, `{view}` | Data for Pick'em games. | [6] |
| Pick'em Challenge Group | `gambit-api.fantasy.espn.com` | `/apis/v1/challenges/{chal_name}/groups/{grp_id}?view={view}` | `{chal_name}`, `{grp_id}`, `{view}` | Group details for Pick'em games. | [6] |
| Pick'em Challenge User Entry | `gambit-api.fantasy.espn.com` | `/apis/v1/challenges/{chal_name}/entries/{user_id}?view={view}` | `{chal_name}`, `{user_id}`, `{view}` | User's picks/entry in a Pick'em game. | [6] |
| Pick'em Challenge Leaderboard | `gambit-api.fantasy.espn.com` | `/apis/v1/challenges/{chal_name}/leaderboard?view={view}` | `{chal_name}`, `{view}` | Leaderboard for Pick'em games. | [6] |
| Pick'em Propositions | `gambit-api.fantasy.espn.com` | `/apis/v1/propositions?challengeId={chal_id}&view={view}` | `{chal_id}`, `{view}` | Propositions/questions for Pick'em games. | [6] |

**Known Fantasy `view` parameters:** `mTeam`, `mRoster`, `mMatchup`, `mSettings`, `mDraftDetail`, `mLiveScoring`, `mPendingTransactions`, `mPositionalRatings`, `modular`, `mNav`, `kona_player_info`, `players_wl`, `proTeamSchedules_wl`, `player_wl`.[3, 6, 7, 12, 14, 15, 24, 17]

## 7. Betting & Odds Endpoints

A significant number of endpoints, primarily hosted on `sports.core.api.espn.com`, are dedicated to betting odds and related data.[3, 4, 6, 8, 10] These endpoints provide access to win probabilities, point spreads, moneylines, futures, and historical odds data from various sportsbooks.

The level of detail available, including endpoints for specific betting providers (identified by `bet_provider_id`), odds movement tracking, head-to-head odds, and team performance against the spread (ATS), suggests a system designed to aggregate and display comprehensive betting information, likely reflecting the data shown on ESPN's own platforms.[3, 6] This highlights the increasing integration between sports media and the sports betting industry.

Known `bet_provider_id` values include: 38 (Caesars), 31 (William Hill), 41 (SugarHouse), 36 (Unibet), 2000 (Bet365), 25 (Westgate), 45 (William Hill NJ), 1001 (accuscore), 1004 (consensus), 1003 (numberfire), 1002 (teamrankings).[3, 6]

**Table 9: Selected Betting & Odds API Endpoints (NFL Example)**

| Function | Base URL | Path | Key Parameters | Notes | References |
| :--------------------------------- | :----------------------- | :----------------------------------------------------------------------------------- | :----------------------------------- | :-------------------------------------------------------------------- | :--------------- |
| Win Probabilities | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/probabilities` | `{eid}`, `limit` | Game win probabilities, often updated live. | [3, 6, 10] |
| Odds (List Providers) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/odds` | `{eid}` | Lists available odds from multiple providers for a game. | [3, 6, 10] |
| Odds (Specific Provider) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/odds/{prov_id}` | `{eid}`, `{prov_id}` | Gets odds from a single specified provider. | [6, 10] |
| Odds History/Movement | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/odds/{prov_id}/history/0/movement` | `{eid}`, `{prov_id}`, `limit` | Shows how odds from a provider have changed over time. | [6] |
| Head-to-Head Odds | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/odds/{prov_id}/head-to-heads` | `{eid}`, `{prov_id}` | Specific head-to-head betting lines. | [3, 6] |
| Futures | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/futures` | `{yr}` | Season-long future bets (e.g., championship winner). | [3, 6, 10] |
| Against-the-Spread (ATS) Records | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/types/{st}/teams/{team_id}/ats` | `{yr}`, `{st}`, `{team_id}` | Team's performance record against the point spread. | [3, 6, 10] |
| Odds Records | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/types/0/teams/{team_id}/odds-records` | `{yr}`, `{team_id}` | Team's win/loss record based on betting odds (e.g., as favorite/underdog). | [3, 6] |
| Team Past Performance (Odds) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/teams/{team_id}/odds/{prov_id}/past-performances` | `{team_id}`, `{prov_id}`, `limit` | Historical performance relative to a provider's odds. | [3, 6] |
| Predictor (Matchup Quality/Proj) | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/predictor` | `{eid}` | ESPN's internal prediction metrics for the game. | [6] |
| Power Index | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/powerindex/{team_id}` | `{eid}`, `{team_id}` | ESPN's power index rating applied to the game matchup. | [6] |

## 8. Utility & Miscellaneous Endpoints

This category includes endpoints providing supplementary data or functionalities that don't fit neatly into the primary sport, fantasy, or betting categories.

**Table 10: Miscellaneous API Endpoints (NFL Example)**

| Function | Base URL | Path | Key Parameters | Notes | References |
| :------------------- | :----------------------- | :---------------------------------------------------------------------------- | :-------------------------------- | :------------------------------------------------ | :--------------- |
| List Positions | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/positions` | `limit` | Lists player positions (e.g., QB, WR, RB). | [3, 6, 10] |
| List Transactions | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/transactions` | - | Player signings, trades, cuts, etc. | [6] |
| List Talent Picks | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/talentpicks` | - | General ESPN talent predictions/picks. | [6, 10] |
| Weekly Talent Picks | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/types/{st}/weeks/{wk}/talentpicks` | `{yr}`, `{st}`, `{wk}`, `limit` | Week-specific talent picks. | [6, 10] |
| List Coaches | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/coaches` | `{yr}`, `limit` | Lists coaches for the specified season. | [6, 10] |
| List Free Agents | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/seasons/{yr}/freeagents` | `{yr}` | Lists free agents for the specified season. | [6] |
| Game Officials | `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/events/{eid}/competitions/{eid}/officials` | `{eid}` | Lists referees and officials for a specific game. | [6] |
| Athlete Statistics Log| `sports.core.api.espn.com` | `/v2/sports/football/leagues/nfl/athletes/{ath_id}/statisticslog` | `{ath_id}` | Log of player statistics across seasons/games. | [3, 6, 10] |

## 9. Conclusion & Recommendations

This document has synthesized community knowledge to provide a comprehensive overview of known, albeit unofficial, ESPN API endpoints. It covers various domains including general site data, core sports statistics, fantasy platforms, betting odds, and miscellaneous utilities across numerous sports.

**Reiteration of Warning:** Developers must remain acutely aware that these APIs are undocumented and unsupported by ESPN.[13, 24, 19, 17, 20, 22] They are subject to change or removal without notice, posing a significant risk to application stability. Usage may also conflict with ESPN's Terms of Service.[19, 20]

**Best Practices for Usage:**

*   **Error Handling:** Implement robust error checking for every API call. Verify HTTP status codes and validate the structure of the received JSON data before attempting to parse or use it.[13, 18]
*   **Defensive Coding:** Do not assume endpoint stability or consistent response formats. Code defensively to handle potential changes gracefully.[13, 17]
*   **Caching:** Implement intelligent caching strategies for data that does not change frequently (e.g., historical stats, team info) to reduce reliance on live API calls and mitigate potential rate-limiting (though official rate limits are unknown).
*   **Configuration:** Avoid hardcoding API URLs directly in the codebase. Use configuration files or environment variables for easier updates if base URLs or paths change.
*   **Community Monitoring:** Stay informed about potential API changes or breakages by monitoring community discussions, such as issues filed against popular wrapper libraries on GitHub.[13, 24, 17]
*   **Wrapper Libraries:** Consider utilizing existing community-built wrapper libraries for languages like Python [7, 13, 14, 24], R [7, 12, 14, 15, 19, 22], or JavaScript.[12, 14] These libraries often abstract away some of the API's complexities and may be updated by maintainers when changes are discovered.

**Alternatives:**

For applications requiring high reliability, guaranteed stability, official support, and clear documentation, developers should investigate commercial or officially supported sports data providers. Alternatives mentioned in the community include SportsRadar, Yahoo Fantasy Sports API, The Sports DB (open database), API-Football, and others.[13, 26] These services typically offer formal APIs with SLAs, though they usually involve subscription costs.

**Contribution:**

The understanding of these hidden APIs relies entirely on community effort. Developers who discover new endpoints, parameters, or changes are encouraged to share their findings by contributing to relevant GitHub repositories (like `pseudo-r/Public-ESPN-API`), Gists, or discussions within wrapper library communities. This collective effort helps maintain the usability of these resources for everyone.

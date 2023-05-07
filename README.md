## DISCLAIMER: 

This is a public API provided by ESPN, and I am not affiliated with ESPN or responsible for any usage of this API. This information is provided solely for educational and informational purposes. Please use this API responsibly and abide by ESPN's terms of service.

#  Public ESPN API Endpoints

The ESPN API provides access to a wide range of sports-related data and content, including news, scores, schedules, and standings. Here are some of the available endpoints:


# General Endpoints
- Leagues: https://site.api.espn.com/apis/site/v2/sports/{sport}
- Teams: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams
- Scores and Schedules: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard
- Standings: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/standings
- Top Headlines: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/news
-  Play by Play: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary
# Sport-Specific Endpoints
# Baseball (MLB)
- Players: https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/players
- Player Stats: https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/statistics/players
# Basketball (NBA)
- Players: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/players
- Player Stats: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/statistics/players
- Team Roster: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/{team}/roster
- Team Schedule: https://site.api.espn.com/apis/site/v2/sports/basketball/nba/{team}/schedule
# Football (NFL)
- Players: https://site.api.espn.com/apis/site/v2/sports/football/nfl/players
- Player Stats: https://site.api.espn.com/apis/site/v2/sports/football/nfl/statistics/players
- Team Roster: https://site.api.espn.com/apis/site/v2/sports/football/nfl/{team}/roster
- Team Schedule: https://site.api.espn.com/apis/site/v2/sports/football/nfl/{team}/schedule
# Hockey (NHL)
- Players: https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/players
- Player Stats: https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/statistics/players
# Soccer
- Leagues: https://site.api.espn.com/apis/site/v2/sports/soccer
- Players: https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/players
- Player Stats: https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/statistics/players
- Standings: https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/standings
- Scores and Schedule: https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard

# Tennis
- Players: https://site.api.espn.com/apis/site/v2/sports/tennis/{tour}/players
- Player Stats: https://site.api.espn.com/apis/site/v2/sports/tennis/{tour}/statistics/players



## Sports
- http://site.api.espn.com/apis/site/v2/sports: Returns a list of all sports available on ESPN, along with basic information such as their ID, name, and slug.
Example: http://site.api.espn.com/apis/site/v2/sports

## News
- http://site.api.espn.com/apis/site/v2/sports/{sport}/news: Returns the latest news articles for the specified sport. Replace {sport} in the URL with the slug of the sport you're interested in.
Example: http://site.api.espn.com/apis/site/v2/sports/football/college-football/news

## Scores

- http://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard: Returns the current or upcoming scores for the specified league. Replace {sport} with the sport slug and {league} with the league slug.
Example: http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard

## Standings

- https://site.web.api.espn.com/apis/site/v2/sports/{sport}/{league}/standings?season={year}: Returns the standings for the specified league and season. Replace {sport} with the sport slug, {league} with the league slug, and {year} with the desired season year.
Example: https://site.web.api.espn.com/apis/v2/sports/soccer/eng.1/standings?season=2001

## Athletes

https://site.web.api.espn.com/apis/site/v2/sports/{sport}/{league}/athletes/{id}: Returns information about the specified athlete. Replace {sport} with the sport slug, {league} with the league slug, and {id} with the athlete ID.
Example: https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/athletes/13982

## Teams

- https://site.web.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{id}: Returns information about the specified team. Replace {sport} with the sport slug, {league} with the league slug, and {id} with the team ID.
Example: https://site.web.api.espn.com/apis/site/v2/sports/soccer/eng.1/teams/360

## Events

- https://site.web.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard: Returns information about the events for the specified league. Replace {sport} with the sport slug and {league} with the league slug.
Example: https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/events


## Videos
- https://api.espn.com/v1/sports/{sport}/{league}/videos: Returns the latest videos for the specified sport and league. Replace {sport} with the sport slug and {league} with the league slug.

Example: https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/videos


## Endpoints

### Sports

Returns information about the available sports.

Endpoint: `https://site.api.espn.com/apis/site/v2/sports`

Example: `https://site.api.espn.com/apis/site/v2/sports`

### Leagues

Returns information about the available leagues for a specific sport.

Endpoint: `https://site.api.espn.com/apis/site/v2/sports/{sport}`

Replace `{sport}` with the sport slug (e.g. `baseball`, `basketball`, `football`).

Example: `https://site.api.espn.com/apis/site/v2/sports/football`

### Teams

Returns information about the teams for a specific league.

Endpoint: `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams`

Replace `{sport}` with the sport slug (e.g. `baseball`, `basketball`, `football`) and `{league}` with the league slug (e.g. `mlb`, `nba`, `nfl`).

Example: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams`

### Standings

Returns the current standings for a specific league.

Endpoint: `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/standings`

Replace `{sport}` with the sport slug (e.g. `baseball`, `basketball`, `football`) and `{league}` with the league slug (e.g. `mlb`, `nba`, `nfl`).

Example: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings`

### Events

Returns information about the events for a specific league.

Endpoint: `https://site.web.api.espn.com/apis/v2/sports/{sport}/{league}/scoreboard`

Replace `{sport}` with the sport slug and `{league}` with the league slug.

Example: `https://site.web.api.espn.com/apis/v2/sports/football/nfl/events`

### Videos

Returns the latest videos for a specific sport and league.

Endpoint: `https://api.espn.com/v1/sports/{sport}/{league}/videos`

Replace `{sport}` with the sport slug and `{league}` with the league slug.

Example: `https://api.espn.com/v1/sports/football/nfl/videos`

## Player and Player Stats Information

Unfortunately, it does not seem like there is a public ESPN API endpoint for retrieving player and player stats information for baseball. If you come across any new information, please feel free to share.

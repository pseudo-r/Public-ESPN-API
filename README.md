## DISCLAIMER: 

This is a public API provided by ESPN, and I am not affiliated with ESPN or responsible for any usage of this API. This information is provided solely for educational and informational purposes. Please use this API responsibly and abide by ESPN's terms of service.

#  Public ESPN API Endpoints

The ESPN API provides access to a wide range of sports-related data and content, including news, scores, schedules, and standings. Here are some of the available endpoints:

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

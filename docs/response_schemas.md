# ESPN API Response Schemas

> Example JSON response structures for the most commonly used endpoints.  
> All responses are truncated for brevity — actual responses contain more fields.

---

## Scoreboard (`/apis/site/v2/sports/{sport}/{league}/scoreboard`)

```json
{
  "leagues": [
    {
      "id": "46",
      "name": "National Basketball Association",
      "abbreviation": "NBA",
      "slug": "nba",
      "season": {
        "year": 2025,
        "type": 2,
        "slug": "regular-season"
      },
      "logos": [{ "href": "https://...", "width": 500, "height": 500 }]
    }
  ],
  "events": [
    {
      "id": "401765432",
      "uid": "s:40~l:46~e:401765432",
      "date": "2025-03-15T00:00Z",
      "name": "Boston Celtics at Golden State Warriors",
      "shortName": "BOS @ GSW",
      "season": { "year": 2025, "type": 2, "slug": "regular-season" },
      "week": { "number": 18 },
      "status": {
        "clock": "0.0",
        "displayClock": "0.0",
        "period": 4,
        "type": {
          "id": "3",
          "name": "STATUS_FINAL",
          "state": "post",
          "completed": true,
          "description": "Final",
          "detail": "Final",
          "shortDetail": "Final"
        }
      },
      "competitions": [
        {
          "id": "401765432",
          "attendance": 18064,
          "venue": {
            "id": "1234",
            "fullName": "Chase Center",
            "address": { "city": "San Francisco", "state": "CA" },
            "capacity": 18064,
            "indoor": true
          },
          "broadcasts": [
            {
              "market": { "id": "1", "type": "National" },
              "media": { "shortName": "ESPN" },
              "type": { "id": "1", "shortName": "TV" }
            }
          ],
          "competitors": [
            {
              "id": "17",
              "homeAway": "home",
              "team": {
                "id": "9",
                "uid": "s:40~l:46~t:9",
                "abbreviation": "GSW",
                "displayName": "Golden State Warriors",
                "shortDisplayName": "Warriors",
                "color": "006BB6",
                "alternateColor": "FDB927",
                "logo": "https://..."
              },
              "score": "121",
              "winner": true,
              "records": [{ "name": "overall", "summary": "42-24" }],
              "leaders": [
                {
                  "name": "points",
                  "displayName": "Points Leader",
                  "leaders": [
                    {
                      "displayValue": "32",
                      "athlete": { "id": "3136776", "displayName": "Stephen Curry" }
                    }
                  ]
                }
              ]
            },
            {
              "id": "2",
              "homeAway": "away",
              "team": {
                "id": "2",
                "abbreviation": "BOS",
                "displayName": "Boston Celtics",
                "score": "115",
                "winner": false
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Teams (`/apis/site/v2/sports/{sport}/{league}/teams`)

```json
{
  "sports": [
    {
      "id": "46",
      "name": "Basketball",
      "leagues": [
        {
          "id": "46",
          "name": "NBA",
          "teams": [
            {
              "team": {
                "id": "9",
                "uid": "s:40~l:46~t:9",
                "slug": "golden-state-warriors",
                "abbreviation": "GSW",
                "displayName": "Golden State Warriors",
                "shortDisplayName": "Warriors",
                "name": "Warriors",
                "nickname": "Warriors",
                "location": "Golden State",
                "color": "006BB6",
                "alternateColor": "FDB927",
                "isActive": true,
                "isAllStar": false,
                "logos": [
                  {
                    "href": "https://...",
                    "width": 500,
                    "height": 500,
                    "rel": ["full", "default"]
                  }
                ],
                "links": [
                  {
                    "rel": ["clubhouse"],
                    "href": "https://www.espn.com/nba/team/_/id/9/golden-state-warriors",
                    "text": "Clubhouse"
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  ],
  "count": 30,
  "pageIndex": 1,
  "pageSize": 100
}
```

---

## Team Roster (`/apis/site/v2/sports/{sport}/{league}/teams/{id}/roster`)

```json
{
  "team": {
    "id": "9",
    "abbreviation": "GSW",
    "displayName": "Golden State Warriors"
  },
  "athletes": [
    {
      "position": "G",
      "items": [
        {
          "id": "3136776",
          "uid": "s:40~l:46~a:3136776",
          "guid": "...",
          "firstName": "Stephen",
          "lastName": "Curry",
          "displayName": "Stephen Curry",
          "shortName": "S. Curry",
          "jersey": "30",
          "position": {
            "id": "2",
            "name": "Shooting Guard",
            "displayName": "Shooting Guard",
            "abbreviation": "SG"
          },
          "age": 36,
          "height": 74,
          "weight": 185,
          "birthDate": "1988-03-14",
          "experience": { "years": 15 },
          "status": { "id": "1", "name": "Active", "type": "active" },
          "headshot": { "href": "https://..." }
        }
      ]
    }
  ],
  "coach": [
    {
      "id": "6010",
      "firstName": "Steve",
      "lastName": "Kerr",
      "experience": 10
    }
  ]
}
```

---

## Team Injuries (`/apis/site/v2/sports/{sport}/{league}/teams/{id}/injuries`)

```json
{
  "team": {
    "id": "9",
    "abbreviation": "GSW"
  },
  "injuries": [
    {
      "id": "12345",
      "athlete": {
        "id": "3136776",
        "displayName": "Stephen Curry",
        "position": { "abbreviation": "SG" },
        "headshot": { "href": "https://..." }
      },
      "type": {
        "id": "1",
        "name": "knee",
        "description": "Knee",
        "abbreviation": "KNEE"
      },
      "location": "left knee",
      "detail": "Left knee soreness",
      "side": "left",
      "fantasy": { "status": "doubtful", "injuryType": "KNEE" },
      "status": "Doubtful",
      "date": "2025-03-10T00:00Z"
    }
  ]
}
```

---

## Game Summary (`/apis/site/v2/sports/{sport}/{league}/summary?event={id}`)

```json
{
  "boxscore": {
    "teams": [
      {
        "team": { "id": "9", "displayName": "Golden State Warriors" },
        "statistics": [
          { "name": "assists", "displayValue": "28", "label": "Assists" },
          { "name": "rebounds", "displayValue": "41", "label": "Rebounds" },
          { "name": "fieldGoalPct", "displayValue": "48.5", "label": "FG%" }
        ],
        "players": [
          {
            "team": { "id": "9" },
            "position": { "displayName": "Guard" },
            "statistics": [
              {
                "names": ["MIN", "FG", "3PT", "FT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "+/-", "PTS"],
                "athletes": [
                  {
                    "athlete": { "id": "3136776", "displayName": "Stephen Curry" },
                    "didNotPlay": false,
                    "stats": ["36", "12-24", "4-10", "4-4", "0", "5", "5", "7", "1", "0", "2", "2", "+8", "32"]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "plays": [
    {
      "id": "4017654340001",
      "sequenceNumber": "1",
      "text": "S. Curry makes 2-pt jump shot from 14 ft",
      "clock": { "displayValue": "11:42" },
      "period": { "number": 1 },
      "team": { "id": "9" },
      "scoreValue": 2,
      "scoringPlay": true
    }
  ],
  "leaders": [
    {
      "name": "points",
      "displayName": "Points Leaders",
      "leaders": [
        {
          "displayValue": "32",
          "team": { "id": "9" },
          "athlete": { "id": "3136776", "displayName": "Stephen Curry" }
        }
      ]
    }
  ],
  "broadcasts": [
    { "market": "national", "names": ["ESPN"] }
  ],
  "predictor": {
    "header": "ESPN BPI Win Probability",
    "homeTeam": {
      "team": { "id": "9" },
      "gameProjection": "63.4",
      "teamChanceLoss": "36.6"
    }
  }
}
```

---

## Athlete (Core API v2)

`GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/athletes/{id}`

```json
{
  "id": "3136776",
  "uid": "s:40~l:46~a:3136776",
  "guid": "...",
  "firstName": "Stephen",
  "lastName": "Curry",
  "displayName": "Stephen Curry",
  "shortName": "S. Curry",
  "weight": 185,
  "displayWeight": "185 lbs",
  "height": 74,
  "displayHeight": "6'2\"",
  "age": 36,
  "dateOfBirth": "1988-03-14T00:00Z",
  "birthPlace": { "city": "Charlotte", "state": "NC", "country": "USA" },
  "citizenship": "United States",
  "jersey": "30",
  "active": true,
  "position": {
    "id": "2",
    "name": "Shooting Guard",
    "abbreviation": "SG"
  },
  "linked": true,
  "team": {
    "$ref": "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/teams/9"
  },
  "experience": { "years": 15 },
  "college": {
    "guid": "...",
    "mascot": "Bulldogs",
    "name": "Davidson"
  },
  "draft": {
    "year": 2009,
    "round": 1,
    "selection": 7
  },
  "headshot": {
    "href": "https://a.espncdn.com/...",
    "alt": "Stephen Curry"
  },
  "statistics": {
    "$ref": "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/athletes/3136776/statistics"
  }
}
```

---

## Event (Core API v2)

`GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{id}`

```json
{
  "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988?lang=en&region=us",
  "id": "401772988",
  "uid": "s:20~l:28~e:401772988",
  "date": "2026-02-08T23:30Z",
  "name": "Seattle Seahawks at New England Patriots",
  "shortName": "SEA VS NE",
  "season": {
    "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025?lang=en&region=us"
  },
  "seasonType": {
    "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/3?lang=en&region=us"
  },
  "week": {
    "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/3/weeks/5?lang=en&region=us"
  },
  "timeValid": true,
  "competitions": [
    {
      "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988?lang=en&region=us",
      "id": "401772988",
      "guid": "db65e2af-b39e-3d1a-9ccd-ea444480b1df",
      "uid": "s:20~l:28~e:401772988~c:401772988",
      "date": "2026-02-08T23:30Z",
      "attendance": 70823,
      "type": {
        "id": "1",
        "text": "Standard",
        "abbreviation": "STD",
        "slug": "standard",
        "type": "standard"
      },
      "timeValid": true,
      "dateValid": true,
      "neutralSite": true,
      "divisionCompetition": false,
      "conferenceCompetition": false,
      "previewAvailable": false,
      "recapAvailable": false,
      "boxscoreAvailable": true,
      "lineupAvailable": false,
      "gamecastAvailable": true,
      "playByPlayAvailable": true,
      "conversationAvailable": true,
      "commentaryAvailable": false,
      "pickcenterAvailable": true,
      "summaryAvailable": true,
      "liveAvailable": false,
      "ticketsAvailable": false,
      "shotChartAvailable": false,
      "timeoutsAvailable": false,
      "possessionArrowAvailable": false,
      "onWatchESPN": false,
      "recent": false,
      "bracketAvailable": false,
      "wallclockAvailable": false,
      "highlightsAvailable": true,
      "gameSource": {
        "id": "1",
        "description": "basic/manual",
        "state": "basic"
      },
      "boxscoreSource": {
        "id": "2",
        "description": "feed",
        "state": "full"
      },
      "playByPlaySource": {
        "id": "2",
        "description": "feed",
        "state": "full"
      },
      "linescoreSource": {
        "id": "1",
        "description": "basic/manual",
        "state": "basic"
      },
      "statsSource": {
        "id": "3",
        "description": "scrubbed",
        "state": "full"
      },
      "venue": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/venues/4738?lang=en&region=us",
        "id": "4738",
        "guid": "ad9d3113-9b26-3c9a-98a9-250109205ef9",
        "fullName": "Levi's Stadium",
        "address": {
          "city": "Santa Clara",
          "state": "CA",
          "zipCode": "95054",
          "country": "USA"
        },
        "grass": true,
        "indoor": false,
        "images": [
          {
            "href": "https://a.espncdn.com/i/venues/nfl/day/4738.jpg",
            "width": 2000,
            "height": 1125,
            "alt": "",
            "rel": [
              "full",
              "day"
            ]
          },
          {
            "href": "https://a.espncdn.com/i/venues/nfl/day/interior/4738.jpg",
            "width": 2000,
            "height": 1125,
            "alt": "",
            "rel": [
              "full",
              "day",
              "interior"
            ]
          }
        ]
      },
      "competitors": [
        {
          "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/17?lang=en&region=us",
          "id": "17",
          "uid": "s:20~l:28~t:17",
          "type": "team",
          "order": 0,
          "homeAway": "home",
          "winner": false,
          "team": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/teams/17?lang=en&region=us"
          },
          "score": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/17/score?lang=en&region=us"
          },
          "linescores": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/17/linescores?lang=en&region=us"
          },
          "roster": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/17/roster?lang=en&region=us"
          },
          "statistics": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/17/statistics?lang=en&region=us"
          },
          "leaders": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/17/leaders?lang=en&region=us"
          },
          "record": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/2/teams/17/record?lang=en&region=us"
          }
        },
        {
          "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/26?lang=en&region=us",
          "id": "26",
          "uid": "s:20~l:28~t:26",
          "type": "team",
          "order": 1,
          "homeAway": "away",
          "winner": true,
          "team": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/teams/26?lang=en&region=us"
          },
          "score": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/26/score?lang=en&region=us"
          },
          "linescores": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/26/linescores?lang=en&region=us"
          },
          "roster": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/26/roster?lang=en&region=us"
          },
          "statistics": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/26/statistics?lang=en&region=us"
          },
          "leaders": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/competitors/26/leaders?lang=en&region=us"
          },
          "record": {
            "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/2/teams/26/record?lang=en&region=us"
          }
        }
      ],
      "notes": [
        {
          "type": "event",
          "headline": "Super Bowl LX"
        }
      ],
      "situation": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/situation?lang=en&region=us"
      },
      "status": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/status?lang=en&region=us"
      },
      "odds": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/odds?lang=en&region=us"
      },
      "broadcasts": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/broadcasts?lang=en&region=us"
      },
      "officials": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/officials?lang=en&region=us"
      },
      "details": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/plays?lang=en&region=us"
      },
      "leaders": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/leaders?lang=en&region=us"
      },
      "links": [
        {
          "language": "en-US",
          "rel": [
            "summary",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/game/_/gameId/401772988/seahawks-patriots",
          "text": "Gamecast",
          "shortText": "Summary",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "summary",
            "sportscenter",
            "app",
            "event"
          ],
          "href": "sportscenter://x-callback-url/showGame?sportName=football&leagueAbbrev=nfl&gameId=401772988",
          "text": "Gamecast",
          "shortText": "Summary",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "now",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/game/_/gameId/401772988",
          "text": "Now",
          "shortText": "Now",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "teamstats",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/matchup?gameId=401772988",
          "text": "Team Stats",
          "shortText": "Team Stats",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "boxscore",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/boxscore/_/gameId/401772988",
          "text": "Box Score",
          "shortText": "Box Score",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "boxscore",
            "sportscenter",
            "app",
            "event"
          ],
          "href": "sportscenter://x-callback-url/showGame?sportName=football&leagueAbbrev=nfl&gameId=401772988",
          "text": "Box Score",
          "shortText": "Box Score",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "gamecast",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/game/_/gameId/401772988",
          "text": "Gamecast",
          "shortText": "Gamecast",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "gamecast",
            "mobile",
            "event"
          ],
          "href": "http://m.espn.com/nfl/gamecast?gameId=401772988&action=summary",
          "text": "Gamecast",
          "shortText": "Gamecast",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "gamecast",
            "sportscenter",
            "app",
            "event"
          ],
          "href": "sportscenter://x-callback-url/showGame?sportName=football&leagueAbbrev=nfl&gameId=401772988",
          "text": "Gamecast",
          "shortText": "Gamecast",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "pbp",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/playbyplay/_/gameId/401772988",
          "text": "Play-by-Play",
          "shortText": "Play-by-Play",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "videos",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/video?gameId=401772988",
          "text": "Videos",
          "shortText": "Videos",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "fantasy",
            "desktop",
            "event"
          ],
          "href": "https://fantasy.espn.com/football/welcome?addata=nfl_gamecast_ffl2025",
          "text": "Play Fantasy Football",
          "shortText": "Play Fantasy Football",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "odds",
            "desktop",
            "event"
          ],
          "href": "https://www.espn.com/nfl/odds/_/gameId/401772988",
          "text": "Odds",
          "shortText": "Odds",
          "isExternal": false,
          "isPremium": false
        },
        {
          "language": "en-US",
          "rel": [
            "odds",
            "mobile",
            "event"
          ],
          "href": "https://m.espn.com/nfl/odds/_/gameId/401772988",
          "text": "Odds",
          "shortText": "Odds",
          "isExternal": false,
          "isPremium": false
        }
      ],
      "predictor": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/predictor?lang=en&region=us"
      },
      "probabilities": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/probabilities?lang=en&region=us"
      },
      "powerIndexes": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/powerindex?lang=en&region=us"
      },
      "format": {
        "regulation": {
          "periods": 4,
          "displayName": "Quarter",
          "slug": "quarter",
          "clock": 900
        },
        "overtime": {
          "displayName": "sudden-death",
          "slug": "sudden-death",
          "clock": 900
        },
        "suddenDeath": {
          "periods": 0,
          "clock": 900
        }
      },
      "relevancy": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/relevancy?lang=en&region=us"
      },
      "drives": {
        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/401772988/competitions/401772988/drives?lang=en&region=us"
      },
      "hasDefensiveStats": false
    }
  ],
  "links": [
    {
      "language": "en-US",
      "rel": [
        "summary",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/game/_/gameId/401772988/seahawks-patriots",
      "text": "Gamecast",
      "shortText": "Summary",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "summary",
        "sportscenter",
        "app",
        "event"
      ],
      "href": "sportscenter://x-callback-url/showGame?sportName=football&leagueAbbrev=nfl&gameId=401772988",
      "text": "Gamecast",
      "shortText": "Summary",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "now",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/game/_/gameId/401772988",
      "text": "Now",
      "shortText": "Now",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "teamstats",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/matchup?gameId=401772988",
      "text": "Team Stats",
      "shortText": "Team Stats",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "boxscore",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/boxscore/_/gameId/401772988",
      "text": "Box Score",
      "shortText": "Box Score",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "boxscore",
        "sportscenter",
        "app",
        "event"
      ],
      "href": "sportscenter://x-callback-url/showGame?sportName=football&leagueAbbrev=nfl&gameId=401772988",
      "text": "Box Score",
      "shortText": "Box Score",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "gamecast",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/game/_/gameId/401772988",
      "text": "Gamecast",
      "shortText": "Gamecast",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "gamecast",
        "mobile",
        "event"
      ],
      "href": "http://m.espn.com/nfl/gamecast?gameId=401772988&action=summary",
      "text": "Gamecast",
      "shortText": "Gamecast",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "gamecast",
        "sportscenter",
        "app",
        "event"
      ],
      "href": "sportscenter://x-callback-url/showGame?sportName=football&leagueAbbrev=nfl&gameId=401772988",
      "text": "Gamecast",
      "shortText": "Gamecast",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "pbp",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/playbyplay/_/gameId/401772988",
      "text": "Play-by-Play",
      "shortText": "Play-by-Play",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "videos",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/video?gameId=401772988",
      "text": "Videos",
      "shortText": "Videos",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "fantasy",
        "desktop",
        "event"
      ],
      "href": "https://fantasy.espn.com/football/welcome?addata=nfl_gamecast_ffl2025",
      "text": "Play Fantasy Football",
      "shortText": "Play Fantasy Football",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "odds",
        "desktop",
        "event"
      ],
      "href": "https://www.espn.com/nfl/odds/_/gameId/401772988",
      "text": "Odds",
      "shortText": "Odds",
      "isExternal": false,
      "isPremium": false
    },
    {
      "language": "en-US",
      "rel": [
        "odds",
        "mobile",
        "event"
      ],
      "href": "https://m.espn.com/nfl/odds/_/gameId/401772988",
      "text": "Odds",
      "shortText": "Odds",
      "isExternal": false,
      "isPremium": false
    }
  ],
  "venues": [
    {
      "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/venues/4738?lang=en&region=us"
    }
  ],
  "league": {
    "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl?lang=en&region=us"
  }
}
```
---

## Betting Odds (Core API v2)

`GET https://sports.core.api.espn.com/v2/sports/{sport}/leagues/{league}/events/{id}/competitions/{id}/odds`

```json
{
  "count": 3,
  "items": [
    {
      "provider": {
        "id": "41",
        "name": "DraftKings",
        "priority": 1
      },
      "details": "-3.5",
      "overUnder": 222.5,
      "spread": -3.5,
      "overOdds": -110,
      "underOdds": -110,
      "awayTeamOdds": {
        "favorite": false,
        "underdog": true,
        "moneyLine": 140,
        "spreadOdds": -110
      },
      "homeTeamOdds": {
        "favorite": true,
        "underdog": false,
        "moneyLine": -165,
        "spreadOdds": -110
      },
      "open": {
        "over": { "value": 220.0 },
        "under": { "value": 220.0 },
        "spread": { "home": { "line": -4.5 } }
      }
    }
  ]
}
```

---

## Win Probabilities (Core API v2)

`GET .../events/{id}/competitions/{id}/probabilities`

```json
{
  "count": 1,
  "items": [
    {
      "homeWinPercentage": 0.634,
      "awayWinPercentage": 0.366,
      "tiePercentage": 0.0,
      "lastModified": "2025-03-15T02:14:00Z",
      "play": {
        "$ref": "https://sports.core.api.espn.com/v2/..."
      }
    }
  ]
}
```

---

## Standings (`/apis/site/v2/sports/{sport}/{league}/standings`)

```json
{
  "uid": "s:40~l:46",
  "season": { "year": 2025, "displayName": "2024-25" },
  "fullViewLink": { "href": "https://www.espn.com/nba/standings" },
  "children": [
    {
      "name": "Eastern Conference",
      "abbreviation": "EAST",
      "standings": {
        "entries": [
          {
            "team": {
              "id": "2",
              "uid": "s:40~l:46~t:2",
              "displayName": "Boston Celtics",
              "abbreviation": "BOS",
              "logo": "https://..."
            },
            "note": { "color": "03A653", "description": "Clinched Playoffs" },
            "stats": [
              { "name": "wins", "displayName": "Wins", "displayValue": "52" },
              { "name": "losses", "displayName": "Losses", "displayValue": "14" },
              { "name": "winPercent", "displayName": "PCT", "displayValue": ".788" },
              { "name": "gamesBehind", "displayName": "GB", "displayValue": "-" },
              { "name": "streak", "displayName": "Strk", "displayValue": "W3" }
            ]
          }
        ]
      }
    }
  ]
}
```

---

## Now API News (`now.core.api.espn.com/v1/sports/news`)

```json
{
  "resultsCount": 1000,
  "resultsLimit": 20,
  "resultsOffset": 0,
  "feed": [
    {
      "dataSourceIdentifier": "espn_wire_12345",
      "description": "Stephen Curry scores 32 points as Golden State Warriors beat Boston Celtics",
      "nowId": "11-12345",
      "premium": false,
      "published": "2025-03-15T02:00:00Z",
      "lastModified": "2025-03-15T02:30:00Z",
      "type": "HeadlineNews",
      "headline": "Curry scores 32, Warriors top Celtics",
      "links": {
        "web": { "href": "https://www.espn.com/nba/story/_/id/12345" },
        "api": { "href": "https://api.espn.com/v1/sports/news/12345" }
      },
      "images": [
        {
          "id": 98765,
          "name": "stephen-curry.jpg",
          "url": "https://a.espncdn.com/photo/...",
          "width": 576,
          "height": 324
        }
      ],
      "categories": [
        { "type": "league", "id": 46, "description": "NBA" },
        { "type": "team", "id": 9, "description": "Golden State Warriors" },
        { "type": "athlete", "id": 3136776, "description": "Stephen Curry" }
      ]
    }
  ]
}
```

---

## CDN Game Package (`cdn.espn.com/core/{sport}/{endpoint}?xhr=1`)

> Returns a large `gamepackageJSON` object containing all game data. Requires `?xhr=1`.

```bash
curl "https://cdn.espn.com/core/nfl/game?xhr=1&gameId=401671793"
```

```json
{
  "gameId": "401671793",
  "gamepackageJSON": {
    "header": {
      "id": "401671793",
      "season": { "year": 2025, "type": 3 },
      "competitions": [
        {
          "id": "401671793",
          "competitors": [
            { "id": "12", "homeAway": "home", "score": "27", "winner": true },
            { "id": "25", "homeAway": "away", "score": "24", "winner": false }
          ],
          "status": {
            "type": { "name": "STATUS_FINAL", "state": "post", "completed": true }
          }
        }
      ]
    },
    "boxscore": { "teams": [], "players": [] },
    "drives": {
      "previous": [
        {
          "id": "4016717931\",",
          "description": "10 plays, 75 yards, 4:32",
          "team": { "id": "12" },
          "plays": [ { "id": "...", "type": { "text": "Rush" }, "text": "..." } ],
          "result": "Touchdown",
          "yards": 75
        }
      ]
    },
    "plays": [ { "id": "...", "text": "...", "scoringPlay": true } ],
    "winprobability": [ { "homeWinPercentage": 0.72, "playId": "..." } ],
    "news": { "articles": [] },
    "standings": {}
  }
}
```

---

## Athlete Overview (`site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/overview`)

> Works for NFL, NBA, NHL, MLB. Response includes stats snapshot, next game, recent news, and rotowire notes.

```json
{
  "statistics": {
    "labels": ["GP", "PTS", "REB", "AST"],
    "names": ["gamesPlayed", "avgPoints", "avgRebounds", "avgAssists"],
    "values": [56.0, 26.4, 4.5, 6.1],
    "displayValues": ["56", "26.4", "4.5", "6.1"]
  },
  "news": { "articles": [ { "headline": "...", "published": "2025-03-14T21:00Z" } ] },
  "nextGame": {
    "id": "401765999",
    "date": "2025-03-16T17:30Z",
    "name": "Golden State Warriors at Boston Celtics",
    "competitions": []
  },
  "gameLog": {
    "events": [
      { "id": "401765000", "gameResult": "W", "stats": ["34", "5", "7"] }
    ]
  },
  "rotowire": { "injury": null, "news": "Curry is healthy and expected to play Friday." }
}
```

---

## Athlete Stats (`site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/stats`)

> Works for NFL, NBA, NHL, MLB. Soccer uses a different path.

```json
{
  "filters": [
    {
      "displayName": "Season Type",
      "name": "seasontype",
      "value": "2",
      "options": [
        { "value": "2", "displayValue": "Regular Season" },
        { "value": "3", "displayValue": "Playoffs" }
      ]
    }
  ],
  "teams": [
    { "id": "9", "uid": "s:40~l:46~t:9", "displayName": "Golden State Warriors" }
  ],
  "categories": [
    {
      "name": "general",
      "displayName": "General",
      "labels": ["GP", "GS", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "FG%", "3P%", "FT%"],
      "totals": ["56", "56", "34.2", "26.4", "4.5", "6.1", "0.9", "0.4", "3.1", ".502", ".408", ".924"]
    }
  ],
  "glossary": [
    { "abbreviation": "GP", "displayName": "Games Played", "description": "Total games played" }
  ]
}
```

---

## Athlete Gamelog (`site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/gamelog`)

```json
{
  "filters": [ { "displayName": "Season", "name": "season", "value": "2025" } ],
  "labels": ["DATE", "OPP", "RESULT", "MIN", "FG", "3PT", "FT", "REB", "AST", "STL", "BLK", "PTS"],
  "names": ["date", "opponent", "gameResult", "minutes", "fieldGoalsMade", "threePointsMade", "freeThrowsMade", "rebounds", "assists", "steals", "blocks", "points"],
  "displayNames": ["Date", "OPP", "RESULT", "MIN", "FG", "3PT", "FT", "REB", "AST", "STL", "BLK", "PTS"],
  "events": [
    {
      "id": "401765000",
      "date": "2025-03-14T00:00Z",
      "opponent": { "id": "2", "displayName": "Boston Celtics", "abbreviation": "BOS" },
      "gameResult": "W",
      "stats": ["36", "12-24", "4-10", "4-4", "5", "7", "1", "0", "32"]
    }
  ]
}
```

---

## Athlete Splits (`site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/athletes/{id}/splits`)

```json
{
  "filters": [ { "displayName": "Season Type", "name": "seasontype" } ],
  "displayName": "Stephen Curry",
  "categories": [
    {
      "name": "home",
      "displayName": "Home",
      "labels": ["GP", "PTS", "REB", "AST"],
      "totals": ["28", "27.1", "4.8", "6.4"]
    },
    {
      "name": "away",
      "displayName": "Away",
      "labels": ["GP", "PTS", "REB", "AST"],
      "totals": ["28", "25.7", "4.2", "5.8"]
    }
  ]
}
```

---

## Statistics by Athlete (`site.web.api.espn.com/apis/common/v3/sports/{sport}/{league}/statistics/byathlete`)

> Statistical leaderboard across all athletes. Works for NBA, NFL, MLB, NHL.

```bash
curl "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete"
curl "https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/statistics/byathlete?category=batting&sort=batting.homeRuns:desc&season=2024"
```

```json
{
  "pagination": { "count": 500, "limit": 50, "page": 1, "pages": 10 },
  "league": { "id": "46", "name": "NBA" },
  "currentSeason": { "year": 2025, "type": 2 },
  "athletes": [
    {
      "athlete": {
        "id": "3136776",
        "displayName": "Stephen Curry",
        "team": { "id": "9", "abbreviation": "GSW" },
        "position": { "abbreviation": "PG" }
      },
      "statistics": [
        { "name": "avgPoints", "displayValue": "26.4", "rank": 5 }
      ]
    }
  ]
}
```

---

## League-wide Injuries (`/apis/site/v2/sports/{sport}/{league}/injuries`)

> Works for team sports: NBA, NFL, NHL, MLB, Soccer. Returns 500 for MMA, Tennis, Golf.

```json
{
  "timestamp": "2025-03-23T12:00:00Z",
  "status": "success",
  "season": { "year": 2025, "type": 2 },
  "injuries": [
    {
      "team": {
        "id": "9",
        "displayName": "Golden State Warriors",
        "abbreviation": "GSW"
      },
      "injuries": [
        {
          "id": "12345",
          "athlete": {
            "id": "3136776",
            "displayName": "Stephen Curry",
            "position": { "abbreviation": "PG" }
          },
          "type": { "name": "knee" },
          "status": "Day-To-Day",
          "date": "2025-03-20T00:00Z"
        }
      ]
    }
  ]
}
```

---

## Transactions (`/apis/site/v2/sports/{sport}/{league}/transactions`)

```json
{
  "timestamp": "2025-03-23T12:00:00Z",
  "status": "success",
  "season": { "year": 2025, "type": 2 },
  "requestedYear": 2025,
  "count": 42,
  "transactions": [
    {
      "id": "99001",
      "date": "2025-03-20T00:00Z",
      "description": "GSW signed F Joe Smith to a 10-day contract",
      "team": { "id": "9", "displayName": "Golden State Warriors" },
      "type": { "id": "1", "description": "Contract Signing" }
    }
  ]
}
```

---

## Groups / Conferences (`/apis/site/v2/sports/{sport}/{league}/groups`)

```json
{
  "status": "success",
  "groups": [
    {
      "id": "5",
      "name": "Eastern Conference",
      "abbreviation": "East",
      "children": [
        { "id": "1", "name": "Atlantic Division", "abbreviation": "Atlantic" },
        { "id": "2", "name": "Central Division", "abbreviation": "Central" },
        { "id": "3", "name": "Southeast Division", "abbreviation": "Southeast" }
      ]
    },
    {
      "id": "6",
      "name": "Western Conference",
      "abbreviation": "West"
    }
  ]
}
```

---

## Rankings (`/apis/site/v2/sports/{sport}/{league}/rankings`)

> Works for college sports: `college-football`, `mens-college-basketball`.

```bash
curl "https://site.api.espn.com/apis/site/v2/sports/football/college-football/rankings"
curl "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/rankings"
```

```json
{
  "sports": [ { "id": "23", "name": "College Football" } ],
  "leagues": [ { "id": "23", "name": "NCAA Football" } ],
  "rankings": [
    {
      "name": "AP Top 25",
      "shortName": "AP Poll",
      "type": "ap",
      "occurrence": { "number": 13, "value": 13, "displayValue": "Week 13" },
      "ranks": [
        {
          "current": 1,
          "previous": 1,
          "points": 1575,
          "firstPlaceVotes": 63,
          "team": {
            "id": "333",
            "displayName": "Alabama Crimson Tide",
            "abbreviation": "ALA",
            "record": { "summary": "11-0" }
          }
        }
      ]
    }
  ],
  "latestWeek": { "number": 13, "startDate": "2024-11-11" }
}
```

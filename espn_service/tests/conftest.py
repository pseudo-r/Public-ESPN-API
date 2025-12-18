"""Pytest configuration and fixtures."""

import pytest
from rest_framework.test import APIClient

from apps.espn.models import Competitor, Event, League, Sport, Team, Venue


@pytest.fixture
def api_client() -> APIClient:
    """Return a DRF API client."""
    return APIClient()


@pytest.fixture
def sport(db) -> Sport:
    """Create a test sport."""
    return Sport.objects.create(slug="basketball", name="Basketball")


@pytest.fixture
def league(db, sport: Sport) -> League:
    """Create a test league."""
    return League.objects.create(
        sport=sport,
        slug="nba",
        name="NBA",
        abbreviation="NBA",
    )


@pytest.fixture
def venue(db) -> Venue:
    """Create a test venue."""
    return Venue.objects.create(
        espn_id="1234",
        name="Test Arena",
        city="Test City",
        state="TS",
        country="USA",
        is_indoor=True,
        capacity=20000,
    )


@pytest.fixture
def team(db, league: League) -> Team:
    """Create a test team."""
    return Team.objects.create(
        league=league,
        espn_id="1",
        uid="s:40~l:46~t:1",
        slug="test-team",
        abbreviation="TST",
        display_name="Test Team",
        short_display_name="Test",
        name="Team",
        nickname="Test City",
        location="Test City",
        color="FF0000",
        alternate_color="0000FF",
        is_active=True,
        logos=[{"href": "https://example.com/logo.png", "rel": ["default"]}],
    )


@pytest.fixture
def team2(db, league: League) -> Team:
    """Create a second test team."""
    return Team.objects.create(
        league=league,
        espn_id="2",
        uid="s:40~l:46~t:2",
        slug="opponent-team",
        abbreviation="OPP",
        display_name="Opponent Team",
        short_display_name="Opponent",
        name="Opponent",
        nickname="Opponent City",
        location="Opponent City",
        color="00FF00",
        is_active=True,
    )


@pytest.fixture
def event(db, league: League, venue: Venue) -> Event:
    """Create a test event."""
    from datetime import datetime, timezone

    return Event.objects.create(
        league=league,
        venue=venue,
        espn_id="401584666",
        uid="s:40~l:46~e:401584666",
        date=datetime(2024, 12, 15, 19, 30, tzinfo=timezone.utc),
        name="Test Team at Opponent Team",
        short_name="TST @ OPP",
        season_year=2024,
        season_type=2,
        status=Event.STATUS_FINAL,
        status_detail="Final",
    )


@pytest.fixture
def competitor_home(db, event: Event, team: Team) -> Competitor:
    """Create home competitor."""
    return Competitor.objects.create(
        event=event,
        team=team,
        home_away=Competitor.HOME,
        score="110",
        winner=True,
        order=1,
    )


@pytest.fixture
def competitor_away(db, event: Event, team2: Team) -> Competitor:
    """Create away competitor."""
    return Competitor.objects.create(
        event=event,
        team=team2,
        home_away=Competitor.AWAY,
        score="105",
        winner=False,
        order=0,
    )


# ESPN API mock response fixtures


@pytest.fixture
def mock_teams_response() -> dict:
    """Mock ESPN teams API response."""
    return {
        "sports": [
            {
                "id": "40",
                "name": "Basketball",
                "slug": "basketball",
                "leagues": [
                    {
                        "id": "46",
                        "name": "NBA",
                        "slug": "nba",
                        "teams": [
                            {
                                "team": {
                                    "id": "1",
                                    "uid": "s:40~l:46~t:1",
                                    "slug": "atlanta-hawks",
                                    "abbreviation": "ATL",
                                    "displayName": "Atlanta Hawks",
                                    "shortDisplayName": "Hawks",
                                    "name": "Hawks",
                                    "nickname": "Atlanta",
                                    "location": "Atlanta",
                                    "color": "c8102e",
                                    "alternateColor": "fdb927",
                                    "isActive": True,
                                    "isAllStar": False,
                                    "logos": [
                                        {
                                            "href": "https://a.espncdn.com/i/teamlogos/nba/500/atl.png",
                                            "rel": ["full", "default"],
                                            "width": 500,
                                            "height": 500,
                                        }
                                    ],
                                    "links": [],
                                }
                            },
                            {
                                "team": {
                                    "id": "2",
                                    "uid": "s:40~l:46~t:2",
                                    "slug": "boston-celtics",
                                    "abbreviation": "BOS",
                                    "displayName": "Boston Celtics",
                                    "shortDisplayName": "Celtics",
                                    "name": "Celtics",
                                    "nickname": "Boston",
                                    "location": "Boston",
                                    "color": "007a33",
                                    "alternateColor": "ba9653",
                                    "isActive": True,
                                    "isAllStar": False,
                                    "logos": [],
                                    "links": [],
                                }
                            },
                        ],
                    }
                ],
            }
        ]
    }


@pytest.fixture
def mock_scoreboard_response() -> dict:
    """Mock ESPN scoreboard API response."""
    return {
        "leagues": [
            {
                "id": "46",
                "name": "NBA",
                "abbreviation": "NBA",
            }
        ],
        "events": [
            {
                "id": "401584666",
                "uid": "s:40~l:46~e:401584666",
                "date": "2024-12-15T19:30:00Z",
                "name": "Atlanta Hawks at Boston Celtics",
                "shortName": "ATL @ BOS",
                "season": {
                    "year": 2024,
                    "type": 2,
                    "slug": "regular-season",
                },
                "status": {
                    "type": {
                        "id": "3",
                        "state": "post",
                        "completed": True,
                        "description": "Final",
                        "detail": "Final",
                    },
                    "displayClock": "0:00",
                    "period": 4,
                },
                "competitions": [
                    {
                        "id": "401584666",
                        "attendance": 19156,
                        "venue": {
                            "id": "123",
                            "fullName": "TD Garden",
                            "address": {
                                "city": "Boston",
                                "state": "MA",
                                "country": "USA",
                            },
                            "indoor": True,
                            "capacity": 19580,
                        },
                        "competitors": [
                            {
                                "id": "2",
                                "homeAway": "home",
                                "winner": True,
                                "team": {
                                    "id": "2",
                                    "abbreviation": "BOS",
                                    "displayName": "Boston Celtics",
                                    "name": "Celtics",
                                    "location": "Boston",
                                },
                                "score": "115",
                                "linescores": [
                                    {"value": 28},
                                    {"value": 30},
                                    {"value": 27},
                                    {"value": 30},
                                ],
                                "records": [
                                    {"type": "total", "summary": "20-5"},
                                ],
                            },
                            {
                                "id": "1",
                                "homeAway": "away",
                                "winner": False,
                                "team": {
                                    "id": "1",
                                    "abbreviation": "ATL",
                                    "displayName": "Atlanta Hawks",
                                    "name": "Hawks",
                                    "location": "Atlanta",
                                },
                                "score": "108",
                                "linescores": [
                                    {"value": 25},
                                    {"value": 28},
                                    {"value": 30},
                                    {"value": 25},
                                ],
                                "records": [
                                    {"type": "total", "summary": "15-10"},
                                ],
                            },
                        ],
                        "broadcasts": [
                            {
                                "market": "national",
                                "names": ["ESPN"],
                            }
                        ],
                    }
                ],
                "links": [],
            }
        ],
    }

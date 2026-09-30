"""Routing contracts for the additional endpoint families."""

import pytest

from clients.espn_client import ESPNClient

CORE = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/"
EVENT = CORE + "events/e1/competitions/c2"


@pytest.mark.parametrize(
    "method,args,url",
    [
        ("get_core_event", ("football", "nfl", "e1"), CORE + "events/e1"),
        ("get_competition", ("football", "nfl", "e1", "c2"), EVENT),
        ("get_competition_status", ("football", "nfl", "e1", "c2"), EVENT + "/status"),
        (
            "get_competitor_roster",
            ("football", "nfl", "e1", "c2", "17", 2, 50),
            EVENT + "/competitors/17/roster?page=2&limit=50",
        ),
        (
            "get_competitor_statistics",
            ("football", "nfl", "e1", "c2", "17"),
            EVENT + "/competitors/17/statistics",
        ),
        (
            "get_competitor_linescores",
            ("football", "nfl", "e1", "c2", "17"),
            EVENT + "/competitors/17/linescores",
        ),
        ("get_drives", ("football", "nfl", "e1", "c2", 2, 10), EVENT + "/drives?page=2&limit=10"),
        (
            "get_athlete_eventlog",
            ("football", "nfl", "3139477", 2026),
            CORE + "athletes/3139477/eventlog?season=2026",
        ),
        (
            "get_athlete_statisticslog",
            ("football", "nfl", "3139477"),
            CORE + "athletes/3139477/statisticslog",
        ),
        ("get_calendar", ("football", "nfl"), CORE + "calendar"),
        ("get_season_types", ("football", "nfl", 2026), CORE + "seasons/2026/types"),
        ("get_season_weeks", ("football", "nfl", 2026, 3), CORE + "seasons/2026/types/3/weeks"),
        ("get_providers", ("football", "nfl", 2, 50), CORE + "providers?page=2&limit=50"),
        ("search", ("A&B", 2), "https://site.web.api.espn.com/apis/search/v2?query=A%26B&limit=2"),
        (
            "get_personalized_scoreboard",
            ("cricket", "in", "Asia/Tokyo"),
            "https://site.api.espn.com/apis/personalized/v2/scoreboard/header?sport=cricket&region=in&tz=Asia%2FTokyo",
        ),
        (
            "get_cricket_summary",
            ("8048", "123"),
            "https://site.web.api.espn.com/apis/site/v2/sports/cricket/8048/summary?event=123&lang=en&region=in",
        ),
        (
            "get_golf_player_summary",
            ("pga", "123", "456", 2026),
            "https://site.web.api.espn.com/apis/site/v2/sports/golf/pga/leaderboard/123/playersummary?season=2026&player=456",
        ),
    ],
)
def test_expanded_routes(httpx_mock, method, args, url):
    httpx_mock.add_response(url=url, json={"verified": True})
    with ESPNClient() as client:
        assert getattr(client, method)(*args).data == {"verified": True}

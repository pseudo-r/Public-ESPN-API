"""NHL transport, ingestion rollback, and read-only API contracts."""

from unittest.mock import patch

import httpx
import pytest

from apps.ingest.tasks import sync_standings, sync_team_rosters, sync_teams
from apps.nhl.models import Player, Standing, Team
from clients.nhl_client import NHLStatsClient, NHLWebClient


@pytest.mark.parametrize(
    "client_type,method,args,path",
    [
        (NHLWebClient, "get_standings", (), "https://api-web.nhle.com/v1/standings/now"),
        (NHLWebClient, "get_roster", ("TOR",), "https://api-web.nhle.com/v1/roster/TOR/current"),
        (
            NHLWebClient,
            "get_player_landing",
            (123,),
            "https://api-web.nhle.com/v1/player/123/landing",
        ),
        (NHLWebClient, "get_schedule", (), "https://api-web.nhle.com/v1/schedule/now"),
        (
            NHLWebClient,
            "get_schedule",
            ("2026-09-30",),
            "https://api-web.nhle.com/v1/schedule/2026-09-30",
        ),
        (
            NHLWebClient,
            "get_boxscore",
            (123,),
            "https://api-web.nhle.com/v1/gamecenter/123/boxscore",
        ),
        (NHLStatsClient, "get_teams", (), "https://api.nhle.com/stats/rest/en/team"),
        (
            NHLStatsClient,
            "get_skater_summary",
            ("20252026",),
            "https://api.nhle.com/stats/rest/en/skater/summary?cayenneExp=seasonId%3D20252026&limit=-1",
        ),
        (
            NHLStatsClient,
            "get_goalie_summary",
            ("20252026",),
            "https://api.nhle.com/stats/rest/en/goalie/summary?cayenneExp=seasonId%3D20252026&limit=-1",
        ),
    ],
)
def test_route_and_transport_cleanup(httpx_mock, client_type, method, args, path):
    httpx_mock.add_response(url=path, json={"data": []})
    with client_type() as client:
        assert getattr(client, method)(*args) == {"data": []}
    assert client.client.is_closed


@pytest.mark.parametrize("status", [403, 404, 429])
def test_terminal_http_errors_are_not_retried(httpx_mock, status):
    httpx_mock.add_response(status_code=status)
    with NHLWebClient() as client, pytest.raises(httpx.HTTPStatusError):
        client.get_standings()
    assert len(httpx_mock.get_requests()) == 1
    assert client.client.is_closed


@pytest.mark.django_db
def test_team_sync_is_idempotent_and_rejects_malformed_snapshot():
    with patch("apps.ingest.tasks.NHLStatsClient") as cls:
        client = cls.return_value.__enter__.return_value
        client.get_teams.return_value = {
            "data": [{"id": 10, "fullName": "Toronto Maple Leafs", "triCode": "TOR"}]
        }
        sync_teams.run()
        sync_teams.run()
        assert Team.objects.count() == 1
        client.get_teams.return_value = {"data": [{"fullName": "Missing ID"}]}
        with pytest.raises(ValueError):
            sync_teams.run()
        assert Team.objects.get().is_active
        client.get_teams.return_value = {}
        with pytest.raises(ValueError):
            sync_teams.run()
        assert Team.objects.get().is_active
        assert cls.return_value.__exit__.call_count == 4


@pytest.mark.django_db
def test_roster_failure_preserves_existing_players():
    team = Team.objects.create(team_id="10", abbreviation="TOR", name="Leafs", full_name="Toronto")
    with patch("apps.ingest.tasks.NHLWebClient") as cls:
        client = cls.return_value.__enter__.return_value
        player = {
            "id": 123,
            "firstName": {"default": "First"},
            "lastName": {"default": "Last"},
            "positionCode": "C",
        }
        client.get_roster.return_value = {"forwards": [player]}
        sync_team_rosters.run()
        sync_team_rosters.run()
        assert Player.objects.get().current_team == team
        client.get_roster.return_value = {
            "forwards": [{**player, "firstName": {"default": "Changed"}}, {}]
        }
        sync_team_rosters.run()
        assert Player.objects.get().first_name == "First"


@pytest.mark.django_db
@pytest.mark.parametrize("abbrev", ["TOR", {"default": "TOR"}])
def test_standings_accept_localized_and_plain_abbreviations(abbrev):
    Team.objects.create(team_id="10", abbreviation="TOR", name="Leafs", full_name="Toronto")
    with patch("apps.ingest.tasks.NHLWebClient") as cls:
        client = cls.return_value.__enter__.return_value
        client.get_standings.return_value = {
            "standings": [
                {"teamAbbrev": abbrev, "date": "2026-04-16", "points": 100},
                {"teamAbbrev": "UNKNOWN"},
            ]
        }
        sync_standings.run()
        sync_standings.run()
        assert Standing.objects.count() == 1
        assert str(Standing.objects.get().date) == "2026-04-16"
        assert Standing.objects.get().points == 100


@pytest.mark.django_db
@pytest.mark.parametrize(
    "route", ["teams", "players", "games", "standings", "skater-stats", "goalie-stats"]
)
def test_endpoints_are_read_only(api_client, route):
    assert api_client.get(f"/api/v1/{route}/").status_code == 200
    assert api_client.post(f"/api/v1/{route}/", {}).status_code == 405

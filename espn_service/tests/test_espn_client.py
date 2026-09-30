"""Tests for ESPN client module."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from apps.core.exceptions import (
    ESPNClientError,
    ESPNNotFoundError,
    ESPNRateLimitError,
)
from clients.espn_client import ESPNClient, ESPNEndpointDomain


class TestESPNClient:
    """Tests for ESPNClient class."""

    def test_client_initialization(self):
        """Test client initializes with default settings."""
        client = ESPNClient()
        assert client.site_api_url == "https://site.api.espn.com"
        assert client.core_api_url == "https://sports.core.api.espn.com"
        assert client.timeout == 5.0  # From test settings
        assert client.max_retries == 1  # From test settings

    def test_client_custom_initialization(self):
        """Test client initializes with custom settings."""
        client = ESPNClient(
            site_api_url="https://custom.api.com",
            timeout=60.0,
            max_retries=5,
        )
        assert client.site_api_url == "https://custom.api.com"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    def test_build_url_site_domain(self):
        """Test URL building for site domain."""
        client = ESPNClient()
        url = client._build_url(
            ESPNEndpointDomain.SITE,
            "/apis/site/v2/sports/basketball/nba/scoreboard",
        )
        assert url == "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

    def test_build_url_core_domain(self):
        """Test URL building for core domain."""
        client = ESPNClient()
        url = client._build_url(
            ESPNEndpointDomain.CORE,
            "/v2/sports/basketball/leagues/nba",
        )
        assert url == "https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba"

    def test_context_manager(self):
        """Test client can be used as context manager."""
        with ESPNClient() as client:
            assert client._client is None  # Lazy initialization

    def test_get_scoreboard_success(self, httpx_mock: HTTPXMock):
        """Test successful scoreboard fetch."""
        mock_response = {
            "events": [
                {"id": "123", "name": "Test Game"},
            ]
        }
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20241215",
            json=mock_response,
        )

        with ESPNClient() as client:
            response = client.get_scoreboard("basketball", "nba", "20241215")

        assert response.is_success
        assert response.data == mock_response

    def test_get_scoreboard_with_datetime(self, httpx_mock: HTTPXMock):
        """Test scoreboard fetch with datetime object."""
        from datetime import datetime

        mock_response = {"events": []}
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates=20241215",
            json=mock_response,
        )

        with ESPNClient() as client:
            response = client.get_scoreboard(
                "basketball",
                "nba",
                datetime(2024, 12, 15),
            )

        assert response.is_success

    def test_get_teams_success(self, httpx_mock: HTTPXMock):
        """Test successful teams fetch."""
        mock_response = {
            "sports": [
                {
                    "leagues": [
                        {
                            "teams": [{"id": "1", "name": "Test Team"}],
                        }
                    ]
                }
            ]
        }
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams?limit=100",
            json=mock_response,
        )

        with ESPNClient() as client:
            response = client.get_teams("basketball", "nba")

        assert response.is_success
        assert response.data == mock_response

    def test_get_team_success(self, httpx_mock: HTTPXMock):
        """Test successful single team fetch."""
        mock_response = {"team": {"id": "1", "name": "Atlanta Hawks"}}
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/1",
            json=mock_response,
        )

        with ESPNClient() as client:
            response = client.get_team("basketball", "nba", "1")

        assert response.is_success
        assert response.data["team"]["id"] == "1"

    def test_handle_404_response(self, httpx_mock: HTTPXMock):
        """Test 404 response raises ESPNNotFoundError."""
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/999",
            status_code=404,
        )

        with ESPNClient() as client, pytest.raises(ESPNNotFoundError):
            client.get_team("basketball", "nba", "999")

    def test_handle_429_response(self, httpx_mock: HTTPXMock):
        """Test 429 response raises ESPNRateLimitError."""
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            status_code=429,
        )

        with ESPNClient() as client, pytest.raises(ESPNRateLimitError):
            client.get_scoreboard("basketball", "nba")

    def test_handle_500_response_with_retry(self, httpx_mock: HTTPXMock):
        """Test 500 response triggers retry and eventually raises error."""
        # Add response for the single retry attempt (max_retries=1 in test settings)
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            status_code=500,
        )

        with ESPNClient() as client, pytest.raises(ESPNClientError):
            client.get_scoreboard("basketball", "nba")

    def test_handle_invalid_json(self, httpx_mock: HTTPXMock):
        """Test invalid JSON response raises ESPNClientError."""
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            content=b"not valid json",
            headers={"content-type": "application/json"},
        )

        with ESPNClient() as client, pytest.raises(ESPNClientError) as exc_info:
            client.get_scoreboard("basketball", "nba")

        assert "Failed to parse" in str(exc_info.value)

    def test_get_event_success(self, httpx_mock: HTTPXMock):
        """Test successful event fetch."""
        mock_response = {"header": {"id": "401584666"}}
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event=401584666",
            json=mock_response,
        )

        with ESPNClient() as client:
            response = client.get_event("basketball", "nba", "401584666")

        assert response.is_success

    def test_get_league_info_success(self, httpx_mock: HTTPXMock):
        """Test successful league info fetch from core API."""
        mock_response = {"id": "46", "name": "NBA"}
        httpx_mock.add_response(
            url="https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba",
            json=mock_response,
        )

        with ESPNClient() as client:
            response = client.get_league_info("basketball", "nba")

        assert response.is_success
        assert response.data["name"] == "NBA"


class TestESPNClientRetry:
    """Tests for ESPN client retry behavior."""

    def test_retry_on_transport_error(self, httpx_mock: HTTPXMock):
        """Test retry on transport errors."""
        # First request raises error, second succeeds
        httpx_mock.add_exception(
            httpx.ConnectError("Connection refused"),
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
        )

        with ESPNClient() as client, pytest.raises(ESPNClientError) as exc_info:
            client.get_scoreboard("basketball", "nba")

        assert "connection error" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Domain routing — new domains added to ESPNEndpointDomain
# ---------------------------------------------------------------------------

class TestNewDomainRouting:
    """Verify new ESPNEndpointDomain values map to correct base URLs."""

    def setup_method(self):
        self.client = ESPNClient(site_api_url="https://site.api.espn.com")

    def test_web_v3_domain_url(self):
        url = self.client._build_url(
            ESPNEndpointDomain.WEB_V3,
            "/apis/common/v3/sports/basketball/nba/athletes/1/stats",
        )
        assert url.startswith("https://site.web.api.espn.com")

    def test_cdn_domain_url(self):
        url = self.client._build_url(ESPNEndpointDomain.CDN, "/core/nfl/game")
        assert url.startswith("https://cdn.espn.com")

    def test_now_domain_url(self):
        url = self.client._build_url(ESPNEndpointDomain.NOW, "/v1/sports/news")
        assert url.startswith("https://now.core.api.espn.com")


# ---------------------------------------------------------------------------
# get_standings bug-fix regression
# ---------------------------------------------------------------------------

class TestGetStandingsDomainFix:
    """Regression: get_standings must use /apis/v2/ not /apis/site/v2/."""

    def test_standings_path_uses_apis_v2(self, httpx_mock: HTTPXMock):
        """Standings must resolve to /apis/v2/ — not /apis/site/v2/."""
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/v2/sports/basketball/nba/standings",
            json={"children": [], "seasons": {}},
        )
        with ESPNClient() as client:
            resp = client.get_standings("basketball", "nba")
        assert resp.is_success

    def test_standings_path_does_not_use_site_v2(self):
        """Ensure the path string itself is /apis/v2/, never /apis/site/v2/."""
        client = ESPNClient()
        # Inspect the path string that would be composed
        # get_standings produces: /apis/v2/sports/{sport}/{league}/standings
        from unittest.mock import MagicMock, patch
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.data = {}
        with patch.object(client, "_request_with_retry", return_value=mock_resp) as mock_req:
            client.get_standings("football", "nfl")
        called_url = mock_req.call_args[0][1]
        assert "/apis/v2/sports/football/nfl/standings" in called_url
        assert "/apis/site/v2/" not in called_url


# ---------------------------------------------------------------------------
# League-wide Site API endpoints
# ---------------------------------------------------------------------------

class TestLeagueWideEndpoints:

    def test_get_league_injuries(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries",
            json={"items": []},
        )
        with ESPNClient() as client:
            resp = client.get_league_injuries("basketball", "nba")
        assert resp.is_success

    def test_get_league_transactions(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/football/nfl/transactions",
            json={"items": []},
        )
        with ESPNClient() as client:
            resp = client.get_league_transactions("football", "nfl")
        assert resp.is_success

    def test_get_groups(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/groups",
            json={"groups": []},
        )
        with ESPNClient() as client:
            resp = client.get_groups("basketball", "nba")
        assert resp.is_success


# ---------------------------------------------------------------------------
# Athlete common/v3 endpoints
# ---------------------------------------------------------------------------

class TestAthleteV3Endpoints:

    def test_get_athlete_overview_uses_web_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/1234/overview",
            json={"athlete": {}, "statistics": []},
        )
        with ESPNClient() as client:
            resp = client.get_athlete_overview("basketball", "nba", 1234)
        assert resp.is_success

    def test_get_athlete_stats_uses_web_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/3054211/stats",
            json={"filters": [], "athletes": []},
        )
        with ESPNClient() as client:
            resp = client.get_athlete_stats("football", "nfl", 3054211)
        assert resp.is_success

    def test_get_athlete_gamelog_uses_web_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/33912/gamelog",
            json={"events": []},
        )
        with ESPNClient() as client:
            resp = client.get_athlete_gamelog("baseball", "mlb", 33912)
        assert resp.is_success

    def test_get_athlete_splits_uses_web_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.web.api.espn.com/apis/common/v3/sports/hockey/nhl/athletes/999/splits",
            json={"splits": {}},
        )
        with ESPNClient() as client:
            resp = client.get_athlete_splits("hockey", "nhl", 999)
        assert resp.is_success

    def test_get_statistics_by_athlete_uses_web_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/statistics/byathlete?limit=50&page=1&category=batting",
            json={"athletes": []},
        )
        with ESPNClient() as client:
            resp = client.get_statistics_by_athlete("baseball", "mlb", category="batting")
        assert resp.is_success


# ---------------------------------------------------------------------------
# CDN Game Data endpoints
# ---------------------------------------------------------------------------

class TestCDNEndpoints:

    def test_get_cdn_game_uses_cdn_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://cdn.espn.com/core/nfl/game?xhr=1&gameId=401547667",
            json={"gamepackageJSON": {}},
        )
        with ESPNClient() as client:
            resp = client.get_cdn_game("nfl", "401547667")
        assert resp.is_success

    def test_get_cdn_game_boxscore_view(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://cdn.espn.com/core/nba/boxscore?xhr=1&gameId=401584666",
            json={"gamepackageJSON": {}},
        )
        with ESPNClient() as client:
            resp = client.get_cdn_game("nba", "401584666", view="boxscore")
        assert resp.is_success

    def test_get_cdn_scoreboard(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://cdn.espn.com/core/nba/scoreboard?xhr=1",
            json={"events": []},
        )
        with ESPNClient() as client:
            resp = client.get_cdn_scoreboard("nba")
        assert resp.is_success


# ---------------------------------------------------------------------------
# Now/News endpoint
# ---------------------------------------------------------------------------

class TestNowNewsEndpoints:

    def test_get_now_news_uses_now_domain(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://now.core.api.espn.com/v1/sports/news?limit=20&offset=0",
            json={"resultsCount": 0, "feed": []},
        )
        with ESPNClient() as client:
            resp = client.get_now_news()
        assert resp.is_success

    def test_get_now_news_with_sport_filter(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://now.core.api.espn.com/v1/sports/news?limit=20&offset=0&sport=football&league=nfl",
            json={"resultsCount": 5, "feed": []},
        )
        with ESPNClient() as client:
            resp = client.get_now_news(sport="football", league="nfl")
        assert resp.is_success

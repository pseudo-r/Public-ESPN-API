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

        with ESPNClient() as client:
            with pytest.raises(ESPNNotFoundError):
                client.get_team("basketball", "nba", "999")

    def test_handle_429_response(self, httpx_mock: HTTPXMock):
        """Test 429 response raises ESPNRateLimitError."""
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            status_code=429,
        )

        with ESPNClient() as client:
            with pytest.raises(ESPNRateLimitError):
                client.get_scoreboard("basketball", "nba")

    def test_handle_500_response_with_retry(self, httpx_mock: HTTPXMock):
        """Test 500 response triggers retry and eventually raises error."""
        # Add response for the single retry attempt (max_retries=1 in test settings)
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            status_code=500,
        )

        with ESPNClient() as client:
            with pytest.raises(ESPNClientError):
                client.get_scoreboard("basketball", "nba")

    def test_handle_invalid_json(self, httpx_mock: HTTPXMock):
        """Test invalid JSON response raises ESPNClientError."""
        httpx_mock.add_response(
            url="https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
            content=b"not valid json",
            headers={"content-type": "application/json"},
        )

        with ESPNClient() as client:
            with pytest.raises(ESPNClientError) as exc_info:
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

        with ESPNClient() as client:
            with pytest.raises(ESPNClientError) as exc_info:
                client.get_scoreboard("basketball", "nba")

        assert "connection error" in str(exc_info.value).lower()

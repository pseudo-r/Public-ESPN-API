"""Tests for REST API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.espn.models import Competitor, Event, League, Season, Sport, Team
from clients.espn_client import ESPNResponse


@pytest.mark.django_db
class TestHealthCheckEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_success(self, api_client: APIClient):
        """Test health check returns healthy status."""
        response = api_client.get("/healthz")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        assert response.json()["database"] == "connected"


@pytest.mark.django_db
class TestTeamEndpoints:
    """Tests for team API endpoints."""

    def test_list_teams_empty(self, api_client: APIClient, league: League):
        """Test listing teams when none exist."""
        response = api_client.get("/api/v1/teams/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 0
        assert response.json()["results"] == []

    def test_list_teams(self, api_client: APIClient, team: Team):
        """Test listing teams."""
        response = api_client.get("/api/v1/teams/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1
        result = response.json()["results"][0]
        assert result["espn_id"] == "1"
        assert result["abbreviation"] == "TST"
        assert result["display_name"] == "Test Team"

    def test_list_teams_filter_by_league(
        self, api_client: APIClient, team: Team, league: League
    ):
        """Test filtering teams by league."""
        response = api_client.get("/api/v1/teams/", {"league": "nba"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/teams/", {"league": "nfl"})
        assert response.json()["count"] == 0

    def test_list_teams_filter_by_sport(
        self, api_client: APIClient, team: Team, sport: Sport
    ):
        """Test filtering teams by sport."""
        response = api_client.get("/api/v1/teams/", {"sport": "basketball"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/teams/", {"sport": "football"})
        assert response.json()["count"] == 0

    def test_list_teams_search(self, api_client: APIClient, team: Team):
        """Test searching teams."""
        response = api_client.get("/api/v1/teams/", {"search": "Test"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/teams/", {"search": "NonExistent"})
        assert response.json()["count"] == 0

    def test_get_team_detail(self, api_client: APIClient, team: Team):
        """Test getting team details."""
        response = api_client.get(f"/api/v1/teams/{team.id}/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["espn_id"] == "1"
        assert data["abbreviation"] == "TST"
        assert data["display_name"] == "Test Team"
        assert data["league"]["slug"] == "nba"
        assert data["primary_logo"] == "https://example.com/logo.png"

    def test_get_team_by_espn_id(self, api_client: APIClient, team: Team):
        """Test getting team by ESPN ID."""
        response = api_client.get("/api/v1/teams/espn/1/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["espn_id"] == "1"

    def test_get_team_by_espn_id_not_found(self, api_client: APIClient, league: League):
        """Test getting non-existent team by ESPN ID."""
        response = api_client.get("/api/v1/teams/espn/999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_team_not_found(self, api_client: APIClient, league: League):
        """Test getting non-existent team."""
        response = api_client.get("/api/v1/teams/999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestEventEndpoints:
    """Tests for event API endpoints."""

    def test_list_events_empty(self, api_client: APIClient, league: League):
        """Test listing events when none exist."""
        response = api_client.get("/api/v1/events/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 0

    def test_list_events(
        self,
        api_client: APIClient,
        event: Event,
        competitor_home: Competitor,
        competitor_away: Competitor,
    ):
        """Test listing events."""
        response = api_client.get("/api/v1/events/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1
        result = response.json()["results"][0]
        assert result["espn_id"] == "401584666"
        assert result["short_name"] == "TST @ OPP"
        assert len(result["competitors"]) == 2

    def test_list_events_filter_by_league(
        self, api_client: APIClient, event: Event, league: League
    ):
        """Test filtering events by league."""
        response = api_client.get("/api/v1/events/", {"league": "nba"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/events/", {"league": "nfl"})
        assert response.json()["count"] == 0

    def test_list_events_filter_by_date(self, api_client: APIClient, event: Event):
        """Test filtering events by date."""
        response = api_client.get("/api/v1/events/", {"date": "2024-12-15"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/events/", {"date": "2024-12-16"})
        assert response.json()["count"] == 0

    def test_list_events_filter_by_date_range(self, api_client: APIClient, event: Event):
        """Test filtering events by date range."""
        response = api_client.get(
            "/api/v1/events/",
            {"date_from": "2024-12-14", "date_to": "2024-12-16"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

    def test_list_events_filter_by_status(self, api_client: APIClient, event: Event):
        """Test filtering events by status."""
        response = api_client.get("/api/v1/events/", {"status": "final"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/events/", {"status": "scheduled"})
        assert response.json()["count"] == 0

    def test_list_events_filter_by_team(
        self,
        api_client: APIClient,
        event: Event,
        competitor_home: Competitor,
        team: Team,
    ):
        """Test filtering events by team."""
        response = api_client.get("/api/v1/events/", {"team": "TST"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/events/", {"team": "XYZ"})
        assert response.json()["count"] == 0

    def test_get_event_detail(
        self,
        api_client: APIClient,
        event: Event,
        competitor_home: Competitor,
        competitor_away: Competitor,
    ):
        """Test getting event details."""
        response = api_client.get(f"/api/v1/events/{event.id}/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["espn_id"] == "401584666"
        assert data["name"] == "Test Team at Opponent Team"
        assert data["status"] == "final"
        assert data["league"]["slug"] == "nba"
        assert data["venue"]["name"] == "Test Arena"
        assert len(data["competitors"]) == 2

    def test_get_event_by_espn_id(self, api_client: APIClient, event: Event):
        """Test getting event by ESPN ID."""
        response = api_client.get("/api/v1/events/espn/401584666/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["espn_id"] == "401584666"

    def test_get_event_by_espn_id_not_found(self, api_client: APIClient, league: League):
        """Test getting non-existent event by ESPN ID."""
        response = api_client.get("/api/v1/events/espn/999999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestIngestEndpoints:
    """Tests for ingestion API endpoints."""

    def test_ingest_teams_success(
        self, api_client: APIClient, mock_teams_response: dict
    ):
        """Test successful teams ingestion."""
        with patch("apps.ingest.services.get_espn_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_teams.return_value = ESPNResponse(
                data=mock_teams_response,
                status_code=200,
                url="test",
            )
            mock_get_client.return_value = mock_client

            response = api_client.post(
                "/api/v1/ingest/teams/",
                {"sport": "basketball", "league": "nba"},
                format="json",
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["created"] == 2
        assert data["total_processed"] == 2

    def test_ingest_teams_validation_error(self, api_client: APIClient):
        """Test teams ingestion with invalid data."""
        response = api_client.post(
            "/api/v1/ingest/teams/",
            {"league": "nba"},  # Missing sport
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_ingest_scoreboard_success(
        self, api_client: APIClient, mock_scoreboard_response: dict
    ):
        """Test successful scoreboard ingestion."""
        with patch("apps.ingest.services.get_espn_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_scoreboard.return_value = ESPNResponse(
                data=mock_scoreboard_response,
                status_code=200,
                url="test",
            )
            mock_get_client.return_value = mock_client

            response = api_client.post(
                "/api/v1/ingest/scoreboard/",
                {"sport": "basketball", "league": "nba", "date": "20241215"},
                format="json",
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["created"] == 1

    def test_ingest_scoreboard_invalid_date(self, api_client: APIClient):
        """Test scoreboard ingestion with invalid date format."""
        response = api_client.post(
            "/api/v1/ingest/scoreboard/",
            {"sport": "basketball", "league": "nba", "date": "2024-12-15"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_ingest_scoreboard_without_date(
        self, api_client: APIClient, mock_scoreboard_response: dict
    ):
        """Test scoreboard ingestion without date (defaults to today)."""
        with patch("apps.ingest.services.get_espn_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_scoreboard.return_value = ESPNResponse(
                data=mock_scoreboard_response,
                status_code=200,
                url="test",
            )
            mock_get_client.return_value = mock_client

            response = api_client.post(
                "/api/v1/ingest/scoreboard/",
                {"sport": "basketball", "league": "nba"},
                format="json",
            )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPagination:
    """Tests for API pagination."""

    def test_teams_pagination(self, api_client: APIClient, league: League):
        """Test teams endpoint pagination."""
        # Create multiple teams
        for i in range(30):
            Team.objects.create(
                league=league,
                espn_id=str(i),
                abbreviation=f"T{i:02d}",
                display_name=f"Team {i}",
            )

        response = api_client.get("/api/v1/teams/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 30
        assert len(data["results"]) == 25  # Default page size
        assert data["next"] is not None
        assert data["previous"] is None

        # Get second page
        response = api_client.get("/api/v1/teams/", {"page": 2})
        data = response.json()
        assert len(data["results"]) == 5
        assert data["next"] is None
        assert data["previous"] is not None


@pytest.mark.django_db
class TestSportEndpoints:
    """Tests for sport discovery endpoints."""

    def test_list_sports_empty(self, api_client: APIClient):
        """Test listing sports when none exist."""
        response = api_client.get("/api/v1/sports/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 0

    def test_list_sports(self, api_client: APIClient, sport: Sport):
        """Test listing sports returns ingested sports."""
        response = api_client.get("/api/v1/sports/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1
        result = response.json()["results"][0]
        assert result["slug"] == "basketball"
        assert result["name"] == "Basketball"

    def test_get_sport_by_slug(self, api_client: APIClient, sport: Sport):
        """Test retrieving a sport by its slug."""
        response = api_client.get("/api/v1/sports/basketball/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["slug"] == "basketball"
        assert data["name"] == "Basketball"

    def test_get_sport_not_found(self, api_client: APIClient):
        """Test retrieving a non-existent sport returns 404."""
        response = api_client.get("/api/v1/sports/nonexistent/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestLeagueEndpoints:
    """Tests for league discovery endpoints."""

    def test_list_leagues_empty(self, api_client: APIClient):
        """Test listing leagues when none exist."""
        response = api_client.get("/api/v1/leagues/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 0

    def test_list_leagues(self, api_client: APIClient, league: League):
        """Test listing leagues returns ingested leagues."""
        response = api_client.get("/api/v1/leagues/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1
        result = response.json()["results"][0]
        assert result["slug"] == "nba"
        assert result["abbreviation"] == "NBA"
        assert result["sport"]["slug"] == "basketball"

    def test_list_leagues_filter_by_sport(
        self, api_client: APIClient, league: League
    ):
        """Test filtering leagues by sport slug."""
        response = api_client.get("/api/v1/leagues/", {"sport": "basketball"})

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 1

        response = api_client.get("/api/v1/leagues/", {"sport": "football"})
        assert response.json()["count"] == 0

    def test_get_league_detail(self, api_client: APIClient, league: League):
        """Test retrieving a league by ID."""
        response = api_client.get(f"/api/v1/leagues/{league.id}/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["slug"] == "nba"
        assert data["sport"]["slug"] == "basketball"

    def test_get_league_not_found(self, api_client: APIClient):
        """Test retrieving a non-existent league returns 404."""
        response = api_client.get("/api/v1/leagues/999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSeasonAPI:
    """Tests for Season API endpoints."""

    def test_list_seasons(self, api_client: APIClient, season: Season):
        response = api_client.get("/api/v1/seasons/")
        assert response.status_code == 200
        assert response.data["count"] == 1
        result = response.data["results"][0]
        assert result["year"] == 2024
        assert result["season_type"] == 2

    def test_filter_season_by_league(self, api_client: APIClient, season: Season):
        response = api_client.get("/api/v1/seasons/?league=nba")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_season_by_year(self, api_client: APIClient, season: Season):
        response = api_client.get("/api/v1/seasons/?year=2024")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_retrieve_season(self, api_client: APIClient, season: Season):
        response = api_client.get(f"/api/v1/seasons/{season.pk}/")
        assert response.status_code == 200
        assert response.data["year"] == 2024

"""Tests for ingestion services."""

from unittest.mock import MagicMock, patch

import pytest

from apps.espn.models import Competitor, Event, League, Sport, Team, Venue
from apps.ingest.services import (
    IngestionResult,
    ScoreboardIngestionService,
    TeamIngestionService,
    get_or_create_sport_and_league,
)
from clients.espn_client import ESPNResponse


@pytest.mark.django_db
class TestGetOrCreateSportAndLeague:
    """Tests for get_or_create_sport_and_league helper."""

    def test_creates_new_sport_and_league(self):
        """Test creating new sport and league."""
        sport, league = get_or_create_sport_and_league("basketball", "nba")

        assert sport.slug == "basketball"
        assert sport.name == "Basketball"
        assert league.slug == "nba"
        assert league.name == "NBA"
        assert league.abbreviation == "NBA"
        assert league.sport == sport

    def test_reuses_existing_sport_and_league(self):
        """Test reusing existing sport and league."""
        sport1, league1 = get_or_create_sport_and_league("basketball", "nba")
        sport2, league2 = get_or_create_sport_and_league("basketball", "nba")

        assert sport1.id == sport2.id
        assert league1.id == league2.id

    def test_creates_different_leagues_for_same_sport(self):
        """Test creating different leagues for same sport."""
        _, nba = get_or_create_sport_and_league("basketball", "nba")
        _, wnba = get_or_create_sport_and_league("basketball", "wnba")

        assert nba.sport == wnba.sport
        assert nba.id != wnba.id


@pytest.mark.django_db
class TestTeamIngestionService:
    """Tests for TeamIngestionService."""

    def test_ingest_teams_success(self, mock_teams_response):
        """Test successful team ingestion."""
        mock_client = MagicMock()
        mock_client.get_teams.return_value = ESPNResponse(
            data=mock_teams_response,
            status_code=200,
            url="test",
        )

        service = TeamIngestionService(client=mock_client)
        result = service.ingest_teams("basketball", "nba")

        assert result.created == 2
        assert result.updated == 0
        assert result.errors == 0

        # Verify teams were created
        assert Team.objects.count() == 2
        atl = Team.objects.get(espn_id="1")
        assert atl.abbreviation == "ATL"
        assert atl.display_name == "Atlanta Hawks"

    def test_ingest_teams_updates_existing(self, mock_teams_response):
        """Test team ingestion updates existing records."""
        # Create sport and league first
        sport = Sport.objects.create(slug="basketball", name="Basketball")
        league = League.objects.create(
            sport=sport, slug="nba", name="NBA", abbreviation="NBA"
        )

        # Create existing team
        Team.objects.create(
            league=league,
            espn_id="1",
            abbreviation="OLD",
            display_name="Old Name",
        )

        mock_client = MagicMock()
        mock_client.get_teams.return_value = ESPNResponse(
            data=mock_teams_response,
            status_code=200,
            url="test",
        )

        service = TeamIngestionService(client=mock_client)
        result = service.ingest_teams("basketball", "nba")

        assert result.created == 1  # BOS is new
        assert result.updated == 1  # ATL is updated

        # Verify team was updated
        atl = Team.objects.get(espn_id="1")
        assert atl.abbreviation == "ATL"
        assert atl.display_name == "Atlanta Hawks"

    def test_ingest_teams_handles_empty_response(self):
        """Test handling empty teams response."""
        mock_client = MagicMock()
        mock_client.get_teams.return_value = ESPNResponse(
            data={"sports": [{"leagues": [{"teams": []}]}]},
            status_code=200,
            url="test",
        )

        service = TeamIngestionService(client=mock_client)
        result = service.ingest_teams("basketball", "nba")

        assert result.created == 0
        assert result.updated == 0


@pytest.mark.django_db
class TestScoreboardIngestionService:
    """Tests for ScoreboardIngestionService."""

    def test_ingest_scoreboard_success(self, mock_scoreboard_response):
        """Test successful scoreboard ingestion."""
        # Pre-create teams
        sport = Sport.objects.create(slug="basketball", name="Basketball")
        league = League.objects.create(
            sport=sport, slug="nba", name="NBA", abbreviation="NBA"
        )
        Team.objects.create(
            league=league, espn_id="1", abbreviation="ATL", display_name="Atlanta Hawks"
        )
        Team.objects.create(
            league=league, espn_id="2", abbreviation="BOS", display_name="Boston Celtics"
        )

        mock_client = MagicMock()
        mock_client.get_scoreboard.return_value = ESPNResponse(
            data=mock_scoreboard_response,
            status_code=200,
            url="test",
        )

        service = ScoreboardIngestionService(client=mock_client)
        result = service.ingest_scoreboard("basketball", "nba", "20241215")

        assert result.created == 1
        assert result.errors == 0

        # Verify event was created
        event = Event.objects.get(espn_id="401584666")
        assert event.name == "Atlanta Hawks at Boston Celtics"
        assert event.short_name == "ATL @ BOS"
        assert event.status == Event.STATUS_FINAL

        # Verify venue was created
        assert event.venue is not None
        assert event.venue.name == "TD Garden"
        assert event.venue.city == "Boston"

        # Verify competitors were created
        assert event.competitors.count() == 2
        home_comp = event.competitors.get(home_away=Competitor.HOME)
        assert home_comp.team.abbreviation == "BOS"
        assert home_comp.score == "115"
        assert home_comp.winner is True

    def test_ingest_scoreboard_creates_missing_teams(self, mock_scoreboard_response):
        """Test scoreboard ingestion creates missing teams."""
        mock_client = MagicMock()
        mock_client.get_scoreboard.return_value = ESPNResponse(
            data=mock_scoreboard_response,
            status_code=200,
            url="test",
        )

        service = ScoreboardIngestionService(client=mock_client)
        result = service.ingest_scoreboard("basketball", "nba", "20241215")

        assert result.created == 1

        # Verify teams were created as side effect
        assert Team.objects.count() == 2

    def test_ingest_scoreboard_updates_existing_event(self, mock_scoreboard_response):
        """Test scoreboard ingestion updates existing events."""
        # Create existing data
        sport = Sport.objects.create(slug="basketball", name="Basketball")
        league = League.objects.create(
            sport=sport, slug="nba", name="NBA", abbreviation="NBA"
        )
        Team.objects.create(
            league=league, espn_id="1", abbreviation="ATL", display_name="Atlanta Hawks"
        )
        Team.objects.create(
            league=league, espn_id="2", abbreviation="BOS", display_name="Boston Celtics"
        )

        from datetime import datetime, timezone

        Event.objects.create(
            league=league,
            espn_id="401584666",
            date=datetime(2024, 12, 15, tzinfo=timezone.utc),
            name="Old Name",
            status=Event.STATUS_SCHEDULED,
            season_year=2024,
            season_type=2,
        )

        mock_client = MagicMock()
        mock_client.get_scoreboard.return_value = ESPNResponse(
            data=mock_scoreboard_response,
            status_code=200,
            url="test",
        )

        service = ScoreboardIngestionService(client=mock_client)
        result = service.ingest_scoreboard("basketball", "nba", "20241215")

        assert result.created == 0
        assert result.updated == 1

        # Verify event was updated
        event = Event.objects.get(espn_id="401584666")
        assert event.name == "Atlanta Hawks at Boston Celtics"
        assert event.status == Event.STATUS_FINAL

    def test_ingest_scoreboard_handles_empty_response(self):
        """Test handling empty scoreboard response."""
        mock_client = MagicMock()
        mock_client.get_scoreboard.return_value = ESPNResponse(
            data={"events": []},
            status_code=200,
            url="test",
        )

        service = ScoreboardIngestionService(client=mock_client)
        result = service.ingest_scoreboard("basketball", "nba", "20241215")

        assert result.created == 0
        assert result.updated == 0


class TestIngestionResult:
    """Tests for IngestionResult dataclass."""

    def test_total_processed(self):
        """Test total_processed calculation."""
        result = IngestionResult(created=5, updated=3)
        assert result.total_processed == 8

    def test_to_dict(self):
        """Test to_dict conversion."""
        result = IngestionResult(created=5, updated=3, errors=1, details=["test"])
        d = result.to_dict()

        assert d["created"] == 5
        assert d["updated"] == 3
        assert d["errors"] == 1
        assert d["total_processed"] == 8
        assert d["details"] == ["test"]

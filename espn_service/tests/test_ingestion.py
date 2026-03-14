"""Tests for ingestion services."""

from datetime import UTC
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from apps.espn.models import Competitor, Event, League, Odds, Sport, Team
from apps.ingest.services import (
    IngestionResult,
    ScoreboardIngestionService,
    TeamIngestionService,
    fraction_to_decimal,
    get_or_create_sport_and_league,
    parse_bet365_odds,
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
        # league.name stores the full official name from LEAGUE_INFO
        assert league.name == "National Basketball Association"
        # league.abbreviation stores the short form
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

        from datetime import datetime

        Event.objects.create(
            league=league,
            espn_id="401584666",
            date=datetime(2024, 12, 15, tzinfo=UTC),
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


class TestFractionToDecimal:
    def test_standard_fraction(self):
        assert fraction_to_decimal("7/8") == Decimal("1.875")

    def test_whole_number_fraction(self):
        assert fraction_to_decimal("9/1") == Decimal("10")

    def test_small_fraction(self):
        result = fraction_to_decimal("27/100")
        assert result == Decimal("1.27")

    def test_even_odds(self):
        assert fraction_to_decimal("1/1") == Decimal("2")

    def test_invalid_input_returns_none(self):
        assert fraction_to_decimal("invalid") is None

    def test_empty_string_returns_none(self):
        assert fraction_to_decimal("") is None

    def test_zero_denominator_returns_none(self):
        assert fraction_to_decimal("1/0") is None


class TestParseBet365Odds:
    def test_parse_complete_odds(self):
        raw = {
            "bettingOdds": {
                "teamOdds": {
                    "preMatchFullTimeResultHome": {"value": "27/100"},
                    "preMatchFullTimeResultDraw": {"value": "19/4"},
                    "preMatchFullTimeResultAway": {"value": "9/1"},
                    "preMatchGoalLineOver": {"value": "7/8"},
                    "preMatchGoalLineUnder": {"value": "39/40"},
                    "preMatchOverUnderHandicap": {"value": "3.25"},
                }
            }
        }
        result = parse_bet365_odds(raw)
        assert result["odds_home"] == Decimal("1.27")
        assert result["odds_draw"] == Decimal("5.75")
        assert result["odds_away"] == Decimal("10")
        assert result["odds_over"] == Decimal("1.875")
        assert result["odds_under"] == Decimal("1.975")
        assert result["over_under_line"] == Decimal("3.25")

    def test_parse_no_betting_odds(self):
        result = parse_bet365_odds({})
        assert result is None

    def test_parse_no_team_odds(self):
        result = parse_bet365_odds({"bettingOdds": {}})
        assert result is None

    def test_parse_missing_market(self):
        raw = {
            "bettingOdds": {
                "teamOdds": {
                    "preMatchFullTimeResultHome": {"value": "27/100"},
                }
            }
        }
        result = parse_bet365_odds(raw)
        assert result["odds_home"] == Decimal("1.27")
        assert result["odds_draw"] is None
        assert result["odds_away"] is None

    def test_parse_missing_value_key(self):
        raw = {
            "bettingOdds": {
                "teamOdds": {
                    "preMatchFullTimeResultHome": {"oddId": "123"},
                }
            }
        }
        result = parse_bet365_odds(raw)
        assert result["odds_home"] is None


@pytest.mark.django_db
class TestScoreboardIngestionWithOdds:
    def test_ingest_scoreboard_creates_odds(self, mock_scoreboard_response):
        """Scoreboard ingestion should also fetch and create odds."""
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
        mock_client.get_event_odds.return_value = ESPNResponse(
            data={
                "bettingOdds": {
                    "teamOdds": {
                        "preMatchFullTimeResultHome": {"value": "1/2"},
                        "preMatchFullTimeResultDraw": {"value": "3/1"},
                        "preMatchFullTimeResultAway": {"value": "5/1"},
                        "preMatchGoalLineOver": {"value": "1/1"},
                        "preMatchGoalLineUnder": {"value": "4/5"},
                        "preMatchOverUnderHandicap": {"value": "2.5"},
                    }
                }
            },
            status_code=200,
            url="test",
        )

        service = ScoreboardIngestionService(client=mock_client)
        result = service.ingest_scoreboard("basketball", "nba")

        assert result.created == 1
        event = Event.objects.get(espn_id="401584666")
        odds = event.odds.first()
        assert odds is not None
        assert odds.provider == "bet365"
        assert odds.odds_home == Decimal("1.5")

    def test_ingest_scoreboard_no_odds_available(self, mock_scoreboard_response):
        """Scoreboard ingestion should work even if odds endpoint returns no data."""
        mock_client = MagicMock()
        mock_client.get_scoreboard.return_value = ESPNResponse(
            data=mock_scoreboard_response,
            status_code=200,
            url="test",
        )
        mock_client.get_event_odds.return_value = ESPNResponse(
            data={},
            status_code=200,
            url="test",
        )

        service = ScoreboardIngestionService(client=mock_client)
        result = service.ingest_scoreboard("basketball", "nba")

        assert result.created == 1
        event = Event.objects.get(espn_id="401584666")
        assert event.odds.count() == 0


@pytest.mark.django_db
class TestBackfillCommand:
    def test_backfill_fetches_and_creates_events(self, db, mock_scoreboard_response):
        """Backfill should list events, fetch each, and create records."""
        from io import StringIO

        from django.core.management import call_command

        mock_client = MagicMock()
        # Mock listing events
        mock_client.get.return_value = ESPNResponse(
            data={
                "count": 1,
                "pageIndex": 1,
                "pageSize": 100,
                "pageCount": 1,
                "items": [
                    {
                        "$ref": "http://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/events/401584666"
                    }
                ],
            },
            status_code=200,
            url="test",
        )
        # Mock get_event (summary)
        mock_client.get_event.return_value = ESPNResponse(
            data={"events": [mock_scoreboard_response["events"][0]]},
            status_code=200,
            url="test",
        )
        # Mock get_event_odds
        mock_client.get_event_odds.return_value = ESPNResponse(
            data={},
            status_code=200,
            url="test",
        )

        from unittest.mock import patch

        with patch("apps.ingest.management.commands.backfill.get_espn_client", return_value=mock_client):
            out = StringIO()
            call_command("backfill", "basketball", "nba", "--season", "2024", "--delay", "0", stdout=out)

        output = out.getvalue()
        assert "401584666" in output
        assert Event.objects.filter(espn_id="401584666").exists()

    def test_backfill_resumes_existing_events(self, db, event, mock_scoreboard_response):
        """Backfill should update events that already exist (idempotent)."""
        from io import StringIO

        from django.core.management import call_command

        mock_client = MagicMock()
        mock_client.get.return_value = ESPNResponse(
            data={
                "count": 1,
                "pageIndex": 1,
                "pageSize": 100,
                "pageCount": 1,
                "items": [
                    {
                        "$ref": "http://sports.core.api.espn.com/v2/events/401584666"
                    }
                ],
            },
            status_code=200,
            url="test",
        )
        mock_client.get_event.return_value = ESPNResponse(
            data={"events": [mock_scoreboard_response["events"][0]]},
            status_code=200,
            url="test",
        )
        mock_client.get_event_odds.return_value = ESPNResponse(
            data={},
            status_code=200,
            url="test",
        )

        from unittest.mock import patch

        with patch("apps.ingest.management.commands.backfill.get_espn_client", return_value=mock_client):
            out = StringIO()
            call_command("backfill", "basketball", "nba", "--season", "2024", "--delay", "0", stdout=out)

        # Should not crash, event count unchanged
        assert Event.objects.filter(espn_id="401584666").count() == 1


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

"""Tests for ESPN models."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from apps.espn.models import Athlete, Competitor, Event, League, Odds, Season, Sport, Team, Venue


@pytest.mark.django_db
class TestSportModel:
    """Tests for Sport model."""

    def test_sport_str(self, sport: Sport):
        """Test Sport string representation."""
        assert str(sport) == "Basketball"

    def test_sport_ordering(self, db):
        """Test Sport ordering by name."""
        Sport.objects.create(slug="football", name="Football")
        Sport.objects.create(slug="baseball", name="Baseball")

        sports = list(Sport.objects.all())
        assert sports[0].name == "Baseball"
        assert sports[1].name == "Football"


@pytest.mark.django_db
class TestLeagueModel:
    """Tests for League model."""

    def test_league_str(self, league: League):
        """Test League string representation."""
        assert str(league) == "NBA (Basketball)"

    def test_league_unique_constraint(self, sport: Sport, league: League):
        """Test League unique constraint on sport+slug."""
        with pytest.raises(Exception):  # IntegrityError
            League.objects.create(
                sport=sport,
                slug="nba",
                name="Duplicate NBA",
            )


@pytest.mark.django_db
class TestTeamModel:
    """Tests for Team model."""

    def test_team_str(self, team: Team):
        """Test Team string representation."""
        assert str(team) == "Test Team (NBA)"

    def test_team_primary_logo(self, team: Team):
        """Test Team primary_logo property."""
        assert team.primary_logo == "https://example.com/logo.png"

    def test_team_primary_logo_no_default(self, league: League):
        """Test Team primary_logo when no default logo."""
        team = Team.objects.create(
            league=league,
            espn_id="99",
            abbreviation="XYZ",
            display_name="No Logo Team",
            logos=[{"href": "https://example.com/alt.png", "rel": ["full"]}],
        )
        assert team.primary_logo == "https://example.com/alt.png"

    def test_team_primary_logo_empty(self, league: League):
        """Test Team primary_logo when no logos."""
        team = Team.objects.create(
            league=league,
            espn_id="99",
            abbreviation="XYZ",
            display_name="No Logo Team",
        )
        assert team.primary_logo is None

    def test_team_unique_constraint(self, team: Team, league: League):
        """Test Team unique constraint on league+espn_id."""
        with pytest.raises(Exception):  # IntegrityError
            Team.objects.create(
                league=league,
                espn_id="1",  # Same as team fixture
                abbreviation="DUP",
                display_name="Duplicate Team",
            )


@pytest.mark.django_db
class TestVenueModel:
    """Tests for Venue model."""

    def test_venue_str_with_location(self, venue: Venue):
        """Test Venue string representation with location."""
        assert str(venue) == "Test Arena (Test City, TS)"

    def test_venue_str_no_location(self, db):
        """Test Venue string representation without location."""
        venue = Venue.objects.create(
            espn_id="5678",
            name="Arena Only",
        )
        assert str(venue) == "Arena Only"


@pytest.mark.django_db
class TestEventModel:
    """Tests for Event model."""

    def test_event_str(self, event: Event):
        """Test Event string representation."""
        assert "TST @ OPP" in str(event)
        assert "2024-12-15" in str(event)

    def test_event_status_choices(self, league: League):
        """Test Event status choices."""
        event = Event.objects.create(
            league=league,
            espn_id="123",
            date=datetime.now(UTC),
            name="Test Event",
            season_year=2024,
            season_type=2,
            status=Event.STATUS_IN_PROGRESS,
        )
        assert event.status == "in_progress"

    def test_event_unique_constraint(self, event: Event, league: League):
        """Test Event unique constraint on league+espn_id."""
        with pytest.raises(Exception):  # IntegrityError
            Event.objects.create(
                league=league,
                espn_id="401584666",  # Same as event fixture
                date=datetime.now(UTC),
                name="Duplicate Event",
                season_year=2024,
                season_type=2,
            )


@pytest.mark.django_db
class TestCompetitorModel:
    """Tests for Competitor model."""

    def test_competitor_str(self, competitor_home: Competitor):
        """Test Competitor string representation."""
        assert "TST" in str(competitor_home)
        assert "home" in str(competitor_home)

    def test_competitor_score_int(self, competitor_home: Competitor):
        """Test Competitor score_int property."""
        assert competitor_home.score_int == 110

    def test_competitor_score_int_empty(self, event: Event, team: Team):
        """Test Competitor score_int when empty."""
        competitor = Competitor.objects.create(
            event=event,
            team=team,
            home_away=Competitor.HOME,
            order=0,
        )
        assert competitor.score_int is None

    def test_competitor_score_int_invalid(self, event: Event, team: Team):
        """Test Competitor score_int when invalid."""
        competitor = Competitor.objects.create(
            event=event,
            team=team,
            home_away=Competitor.HOME,
            score="N/A",
            order=0,
        )
        assert competitor.score_int is None


@pytest.mark.django_db
class TestAthleteModel:
    """Tests for Athlete model."""

    def test_athlete_str_with_team(self, team: Team):
        """Test Athlete string representation with team."""
        athlete = Athlete.objects.create(
            espn_id="12345",
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            display_name="T. Player",
            team=team,
        )
        assert str(athlete) == "T. Player (TST)"

    def test_athlete_str_free_agent(self, db):
        """Test Athlete string representation as free agent."""
        athlete = Athlete.objects.create(
            espn_id="12345",
            first_name="Test",
            last_name="Player",
            full_name="Test Player",
            display_name="T. Player",
        )
        assert str(athlete) == "T. Player (FA)"


@pytest.mark.django_db
class TestSeason:
    """Tests for Season model."""

    def test_create_season(self, db, league):
        from datetime import date

        season = Season.objects.create(
            league=league,
            year=2024,
            season_type=2,
            start_date=date(2024, 10, 22),
            end_date=date(2025, 4, 13),
            display_name="2024-25 Regular Season",
            slug="regular-season",
        )
        assert season.year == 2024
        assert season.season_type == 2
        assert str(season) == "NBA 2024 Regular (2)"

    def test_season_unique_constraint(self, db, league):
        from datetime import date

        Season.objects.create(
            league=league,
            year=2024,
            season_type=2,
            start_date=date(2024, 10, 22),
            end_date=date(2025, 4, 13),
        )
        with pytest.raises(Exception):
            Season.objects.create(
                league=league,
                year=2024,
                season_type=2,
                start_date=date(2024, 10, 22),
                end_date=date(2025, 4, 13),
            )

    def test_event_season_fk(self, db, event, league):
        from datetime import date

        season = Season.objects.create(
            league=league,
            year=2024,
            season_type=2,
            start_date=date(2024, 10, 22),
            end_date=date(2025, 4, 13),
        )
        event.season = season
        event.save()
        event.refresh_from_db()
        assert event.season == season


@pytest.mark.django_db
class TestOddsModel:
    """Tests for Odds model."""

    def test_create_odds(self, event: Event):
        odds = Odds.objects.create(
            event=event,
            provider="bet365",
            odds_home=Decimal("1.27"),
            odds_draw=Decimal("5.75"),
            odds_away=Decimal("10.0"),
            odds_over=Decimal("1.875"),
            odds_under=Decimal("1.975"),
            over_under_line=Decimal("3.25"),
        )
        assert odds.provider == "bet365"
        assert odds.odds_home == Decimal("1.27")
        assert odds.over_under_line == Decimal("3.25")

    def test_odds_str(self, event: Event):
        odds = Odds.objects.create(event=event, provider="bet365")
        assert "bet365" in str(odds)

    def test_odds_unique_together(self, event: Event):
        Odds.objects.create(event=event, provider="bet365")
        with pytest.raises(Exception):
            Odds.objects.create(event=event, provider="bet365")

    def test_odds_allows_different_providers(self, event: Event):
        Odds.objects.create(event=event, provider="bet365")
        Odds.objects.create(event=event, provider="draftkings")
        assert event.odds.count() == 2

    def test_odds_nullable_fields(self, event: Event):
        odds = Odds.objects.create(event=event, provider="bet365")
        assert odds.odds_home is None
        assert odds.odds_draw is None
        assert odds.over_under_line is None

"""Data ingestion services for ESPN data.

This module contains services that orchestrate fetching data from ESPN
and persisting it to the database using idempotent upserts.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import structlog
from django.db import transaction

from apps.core.exceptions import IngestionError
from apps.espn.models import Competitor, Event, League, Odds, Sport, Team, Venue
from clients.espn_client import ESPNClient, get_espn_client

logger = structlog.get_logger(__name__)


@dataclass
class IngestionResult:
    """Result of an ingestion operation."""

    created: int = 0
    updated: int = 0
    errors: int = 0
    details: list[str] | None = None

    @property
    def total_processed(self) -> int:
        return self.created + self.updated

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "updated": self.updated,
            "errors": self.errors,
            "total_processed": self.total_processed,
            "details": self.details,
        }


def get_or_create_sport_and_league(sport_slug: str, league_slug: str) -> tuple[Sport, League]:
    """Get or create Sport and League records.

    Uses the comprehensive SPORT_NAMES and LEAGUE_INFO registries that cover
    all 17 sports and 139 leagues discovered from the ESPN v2/v3 WADL.

    Args:
        sport_slug: Sport slug (e.g., "basketball", "football")
        league_slug: League slug (e.g., "nba", "nfl")

    Returns:
        Tuple of (Sport, League)
    """
    from clients.espn_client import LEAGUE_INFO, SPORT_NAMES

    sport, _ = Sport.objects.get_or_create(
        slug=sport_slug,
        defaults={"name": SPORT_NAMES.get(sport_slug, sport_slug.replace("-", " ").title())},
    )

    league_name, league_abbr = LEAGUE_INFO.get(
        league_slug, (league_slug.replace("-", " ").title(), league_slug.upper()[:10])
    )
    league, _ = League.objects.get_or_create(
        sport=sport,
        slug=league_slug,
        defaults={
            "name": league_name,
            "abbreviation": league_abbr,
        },
    )

    return sport, league


def fraction_to_decimal(fraction_str: str) -> Decimal | None:
    """Convert a UK fractional odds string to decimal odds.

    Examples:
        '7/8' → Decimal('1.875')
        '9/1' → Decimal('10')

    Returns None for invalid input.
    """
    if not fraction_str or "/" not in fraction_str:
        return None
    try:
        num, den = fraction_str.split("/")
        return Decimal(num) / Decimal(den) + 1
    except (InvalidOperation, ZeroDivisionError, ValueError):
        return None


def parse_bet365_odds(raw_data: dict[str, Any]) -> dict[str, Any] | None:
    """Parse Bet365 odds from ESPN core API response.

    Extracts pre-match odds from bettingOdds.teamOdds.
    Converts fractional UK odds to decimal.

    Returns dict of odds fields, or None if no betting data.
    """
    betting_odds = raw_data.get("bettingOdds", {})
    team_odds = betting_odds.get("teamOdds")
    if not team_odds:
        return None

    mapping = {
        "odds_home": "preMatchFullTimeResultHome",
        "odds_draw": "preMatchFullTimeResultDraw",
        "odds_away": "preMatchFullTimeResultAway",
        "odds_over": "preMatchGoalLineOver",
        "odds_under": "preMatchGoalLineUnder",
    }

    result: dict[str, Any] = {}
    for field, key in mapping.items():
        market = team_odds.get(key, {})
        value = market.get("value")
        result[field] = fraction_to_decimal(value) if value else None

    # Over/under line is a decimal string, not a fraction
    handicap = team_odds.get("preMatchOverUnderHandicap", {}).get("value")
    try:
        result["over_under_line"] = Decimal(handicap) if handicap else None
    except InvalidOperation:
        result["over_under_line"] = None

    return result


class TeamIngestionService:
    """Service for ingesting team data from ESPN."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    def _parse_team_data(self, team_data: dict[str, Any]) -> dict[str, Any]:
        """Parse raw team data into model fields.

        Args:
            team_data: Raw team data from ESPN API

        Returns:
            Dict of model fields
        """
        # Extract team info - handle nested structure
        team_info = team_data.get("team", team_data)

        return {
            "espn_id": str(team_info.get("id", "")),
            "uid": team_info.get("uid", ""),
            "slug": team_info.get("slug", ""),
            "abbreviation": team_info.get("abbreviation", ""),
            "display_name": team_info.get("displayName", ""),
            "short_display_name": team_info.get("shortDisplayName", ""),
            "name": team_info.get("name", ""),
            "nickname": team_info.get("nickname", ""),
            "location": team_info.get("location", ""),
            "color": team_info.get("color", ""),
            "alternate_color": team_info.get("alternateColor", ""),
            "is_active": team_info.get("isActive", True),
            "is_all_star": team_info.get("isAllStar", False),
            "logos": team_info.get("logos", []),
            "links": team_info.get("links", []),
            "raw_data": team_info,
        }

    @transaction.atomic
    def ingest_teams(self, sport: str, league: str) -> IngestionResult:
        """Ingest all teams for a sport and league.

        Args:
            sport: Sport slug (e.g., "basketball")
            league: League slug (e.g., "nba")

        Returns:
            IngestionResult with counts
        """
        result = IngestionResult(details=[])

        try:
            # Ensure sport and league exist
            _, league_obj = get_or_create_sport_and_league(sport, league)

            # Fetch teams from ESPN
            response = self.client.get_teams(sport, league)
            teams_data = response.data.get("sports", [{}])[0].get("leagues", [{}])[0].get(
                "teams", []
            )

            if not teams_data:
                logger.warning(
                    "no_teams_found",
                    sport=sport,
                    league=league,
                )
                return result

            for team_data in teams_data:
                try:
                    parsed = self._parse_team_data(team_data)
                    espn_id = parsed.pop("espn_id")

                    if not espn_id:
                        result.errors += 1
                        continue

                    _, created = Team.objects.update_or_create(
                        league=league_obj,
                        espn_id=espn_id,
                        defaults=parsed,
                    )

                    if created:
                        result.created += 1
                    else:
                        result.updated += 1

                except Exception as e:
                    logger.error(
                        "team_ingestion_error",
                        team_data=team_data,
                        error=str(e),
                    )
                    result.errors += 1

            logger.info(
                "teams_ingested",
                sport=sport,
                league=league,
                created=result.created,
                updated=result.updated,
                errors=result.errors,
            )

        except Exception as e:
            logger.exception("team_ingestion_failed", sport=sport, league=league)
            raise IngestionError(f"Failed to ingest teams: {e}") from e

        return result


class ScoreboardIngestionService:
    """Service for ingesting scoreboard/event data from ESPN."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    def _parse_venue_data(self, venue_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse venue data from ESPN API.

        Args:
            venue_data: Raw venue data

        Returns:
            Dict of model fields or None
        """
        if not venue_data or not venue_data.get("id"):
            return None

        address = venue_data.get("address", {})

        return {
            "espn_id": str(venue_data.get("id", "")),
            "name": venue_data.get("fullName", venue_data.get("shortName", "")),
            "city": address.get("city", ""),
            "state": address.get("state", ""),
            "country": address.get("country", "USA"),
            "is_indoor": venue_data.get("indoor", True),
            "capacity": venue_data.get("capacity"),
            "raw_data": venue_data,
        }

    def _parse_event_status(self, status_data: dict[str, Any]) -> tuple[str, str]:
        """Parse event status from ESPN data.

        Args:
            status_data: Status object from ESPN

        Returns:
            Tuple of (status, status_detail)
        """
        type_data = status_data.get("type", {})
        state = type_data.get("state", "pre")
        completed = type_data.get("completed", False)

        if completed:
            return Event.STATUS_FINAL, type_data.get("detail", "Final")

        status_map = {
            "pre": Event.STATUS_SCHEDULED,
            "in": Event.STATUS_IN_PROGRESS,
            "post": Event.STATUS_FINAL,
        }

        return status_map.get(state, Event.STATUS_SCHEDULED), type_data.get("detail", "")

    def _parse_event_data(
        self, event_data: dict[str, Any], league: League  # noqa: ARG002
    ) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
        """Parse event data from ESPN API.

        Args:
            event_data: Raw event data
            league: League object

        Returns:
            Tuple of (event_fields, competitors_data, venue_data)
        """
        # Get competition data (usually only one)
        competitions = event_data.get("competitions", [])
        competition = competitions[0] if competitions else {}

        # Parse status
        status_data = event_data.get("status", {})
        status, status_detail = self._parse_event_status(status_data)

        # Parse season info
        season_data = event_data.get("season", {})

        # Parse date
        date_str = event_data.get("date", "")
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            date = datetime.now()

        event_fields = {
            "espn_id": str(event_data.get("id", "")),
            "uid": event_data.get("uid", ""),
            "date": date,
            "name": event_data.get("name", ""),
            "short_name": event_data.get("shortName", ""),
            "season_year": season_data.get("year", date.year),
            "season_type": season_data.get("type", 2),
            "season_slug": season_data.get("slug", ""),
            "week": event_data.get("week", {}).get("number"),
            "status": status,
            "status_detail": status_detail,
            "clock": status_data.get("displayClock", ""),
            "period": status_data.get("period"),
            "attendance": competition.get("attendance"),
            "broadcasts": competition.get("broadcasts", []),
            "links": event_data.get("links", []),
            "raw_data": event_data,
        }

        # Parse venue
        venue_data = self._parse_venue_data(competition.get("venue", {}))

        # Parse competitors
        competitors_data = competition.get("competitors", [])

        return event_fields, competitors_data, venue_data

    def _get_or_create_venue(self, venue_data: dict[str, Any] | None) -> Venue | None:
        """Get or create venue from parsed data."""
        if not venue_data:
            return None

        espn_id = venue_data.pop("espn_id")
        venue, _ = Venue.objects.update_or_create(
            espn_id=espn_id,
            defaults=venue_data,
        )
        return venue

    def _create_competitors(
        self,
        event: Event,
        competitors_data: list[dict[str, Any]],
        league: League,
    ) -> int:
        """Create competitor records for an event.

        Args:
            event: Event object
            competitors_data: List of competitor data from ESPN
            league: League object

        Returns:
            Number of competitors created
        """
        count = 0

        for idx, comp_data in enumerate(competitors_data):
            team_data = comp_data.get("team", {})
            team_id = str(team_data.get("id", ""))

            if not team_id:
                continue

            # Try to find the team
            try:
                team = Team.objects.get(league=league, espn_id=team_id)
            except Team.DoesNotExist:
                # Create a minimal team record
                team = Team.objects.create(
                    league=league,
                    espn_id=team_id,
                    abbreviation=team_data.get("abbreviation", ""),
                    display_name=team_data.get("displayName", team_data.get("name", "")),
                    short_display_name=team_data.get("shortDisplayName", ""),
                    name=team_data.get("name", ""),
                    location=team_data.get("location", ""),
                    logos=team_data.get("logo", []),
                )

            # Determine home/away
            home_away = comp_data.get("homeAway", "away")
            if home_away not in [Competitor.HOME, Competitor.AWAY]:
                home_away = Competitor.HOME if idx == 1 else Competitor.AWAY

            # Create competitor
            Competitor.objects.update_or_create(
                event=event,
                team=team,
                defaults={
                    "home_away": home_away,
                    "score": comp_data.get("score", ""),
                    "winner": comp_data.get("winner"),
                    "line_scores": comp_data.get("linescores", []),
                    "records": comp_data.get("records", []),
                    "statistics": comp_data.get("statistics", []),
                    "leaders": comp_data.get("leaders", []),
                    "order": idx,
                    "raw_data": comp_data,
                },
            )
            count += 1

        return count

    def _ingest_odds(self, event: Event, sport: str, league: str) -> None:
        """Fetch and store Bet365 odds for an event."""
        try:
            response = self.client.get_event_odds(sport, league, event.espn_id)
            parsed = parse_bet365_odds(response.data)
            if parsed:
                Odds.objects.update_or_create(
                    event=event,
                    provider="bet365",
                    defaults={**parsed, "raw_data": response.data},
                )
        except Exception as e:
            logger.warning(
                "odds_ingestion_skipped",
                event_id=event.espn_id,
                error=str(e),
            )

    @transaction.atomic
    def ingest_scoreboard(
        self,
        sport: str,
        league: str,
        date: str | None = None,
    ) -> IngestionResult:
        """Ingest scoreboard data for a sport, league, and date.

        Args:
            sport: Sport slug (e.g., "basketball")
            league: League slug (e.g., "nba")
            date: Date in YYYYMMDD format (optional, defaults to today)

        Returns:
            IngestionResult with counts
        """
        result = IngestionResult(details=[])

        try:
            # Ensure sport and league exist
            _, league_obj = get_or_create_sport_and_league(sport, league)

            # Fetch scoreboard from ESPN
            response = self.client.get_scoreboard(sport, league, date)
            events_data = response.data.get("events", [])

            if not events_data:
                logger.info(
                    "no_events_found",
                    sport=sport,
                    league=league,
                    date=date,
                )
                return result

            for event_data in events_data:
                try:
                    # Parse event data
                    event_fields, competitors_data, venue_data = self._parse_event_data(
                        event_data, league_obj
                    )

                    espn_id = event_fields.pop("espn_id")
                    if not espn_id:
                        result.errors += 1
                        continue

                    # Get or create venue
                    venue = self._get_or_create_venue(venue_data)

                    # Create or update event
                    event, created = Event.objects.update_or_create(
                        league=league_obj,
                        espn_id=espn_id,
                        defaults={**event_fields, "venue": venue},
                    )

                    # Clear existing competitors and recreate
                    event.competitors.all().delete()
                    self._create_competitors(event, competitors_data, league_obj)

                    # Fetch and store odds
                    self._ingest_odds(event, sport, league)

                    if created:
                        result.created += 1
                    else:
                        result.updated += 1

                except Exception as e:
                    logger.error(
                        "event_ingestion_error",
                        event_id=event_data.get("id"),
                        error=str(e),
                    )
                    result.errors += 1

            logger.info(
                "scoreboard_ingested",
                sport=sport,
                league=league,
                date=date,
                created=result.created,
                updated=result.updated,
                errors=result.errors,
            )

        except Exception as e:
            logger.exception(
                "scoreboard_ingestion_failed",
                sport=sport,
                league=league,
                date=date,
            )
            raise IngestionError(f"Failed to ingest scoreboard: {e}") from e

        return result

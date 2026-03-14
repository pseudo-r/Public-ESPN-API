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
from apps.espn.models import Competitor, Event, League, Odds, Season, Sport, Team, Venue
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


import re

# Provider priority: try Bet365 first, then Unibet
PROVIDER_PRIORITY = [
    re.compile(r"bet\s*365", re.IGNORECASE),
    re.compile(r"unibet", re.IGNORECASE),
]


def _safe_decimal(value: Any) -> Decimal | None:
    """Safely convert a value to Decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def select_provider(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Select best provider from odds items list by priority.

    Tries Bet365 first (matches 'Bet365', 'Bet 365', etc.),
    then Unibet as fallback.

    Returns the provider's odds data dict, or None.
    """
    for pattern in PROVIDER_PRIORITY:
        for item in items:
            provider = item.get("provider", {})
            name = provider.get("name", "")
            if pattern.search(name):
                return item
    return None


def _parse_format_standard(provider_data: dict[str, Any]) -> dict[str, Any]:
    """Parse odds from standard format (providers like 1001, 58).

    Uses close/current → moneyLine.decimal for 1X2,
    close/current → over/under/draw.decimal for markets.
    """
    home_odds = provider_data.get("homeTeamOdds", {})
    away_odds = provider_data.get("awayTeamOdds", {})

    home_ml = (
        home_odds.get("close", {}).get("moneyLine", {})
        or home_odds.get("current", {}).get("moneyLine", {})
    )
    away_ml = (
        away_odds.get("close", {}).get("moneyLine", {})
        or away_odds.get("current", {}).get("moneyLine", {})
    )

    close_data = provider_data.get("close", {})
    current_data = provider_data.get("current", {})

    return {
        "odds_home": _safe_decimal(home_ml.get("decimal") if isinstance(home_ml, dict) else None),
        "odds_away": _safe_decimal(away_ml.get("decimal") if isinstance(away_ml, dict) else None),
        "odds_draw": _safe_decimal(
            (close_data.get("draw", {}) or current_data.get("draw", {})).get("decimal")
        ),
        "odds_over": _safe_decimal(
            (close_data.get("over", {}) or current_data.get("over", {})).get("decimal")
        ),
        "odds_under": _safe_decimal(
            (close_data.get("under", {}) or current_data.get("under", {})).get("decimal")
        ),
        "over_under_line": _safe_decimal(provider_data.get("overUnder")),
    }


def _parse_format_2000(provider_data: dict[str, Any]) -> dict[str, Any]:
    """Parse odds from provider 2000 format ('Bet 365').

    Uses homeTeamOdds.odds.value for 1X2 (already decimal),
    and bettingOdds.teamOdds for over/under (fractional UK).
    """
    home_odds = provider_data.get("homeTeamOdds", {})
    away_odds = provider_data.get("awayTeamOdds", {})
    draw_odds = provider_data.get("drawOdds", {})

    result = {
        "odds_home": _safe_decimal(home_odds.get("odds", {}).get("value")),
        "odds_away": _safe_decimal(away_odds.get("odds", {}).get("value")),
        "odds_draw": _safe_decimal(draw_odds.get("value")),
        "odds_over": None,
        "odds_under": None,
        "over_under_line": None,
    }

    # Over/under from bettingOdds.teamOdds (fractional UK)
    team_odds = provider_data.get("bettingOdds", {}).get("teamOdds", {})
    if team_odds:
        over_val = team_odds.get("preMatchGoalLineOver", {}).get("value")
        under_val = team_odds.get("preMatchGoalLineUnder", {}).get("value")
        line_val = team_odds.get("preMatchOverUnderHandicap", {}).get("value")
        result["odds_over"] = fraction_to_decimal(over_val) if over_val else None
        result["odds_under"] = fraction_to_decimal(under_val) if under_val else None
        result["over_under_line"] = _safe_decimal(line_val)

    return result


def parse_odds_data(provider_data: dict[str, Any]) -> dict[str, Any] | None:
    """Parse odds from a single provider's data (format from /odds endpoint).

    Auto-detects format:
    - Provider 2000 ('Bet 365'): uses bettingOdds + homeTeamOdds.odds
    - Other providers: uses close/current + moneyLine.decimal

    Returns dict of odds fields, or None if insufficient data.
    """
    # Detect format by presence of bettingOdds (provider 2000)
    if "bettingOdds" in provider_data:
        result = _parse_format_2000(provider_data)
    else:
        result = _parse_format_standard(provider_data)

    if not any(v is not None for v in result.values()):
        return None

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

    def _get_or_create_season(
        self, league: League, season_data: dict[str, Any]
    ) -> Season | None:
        """Get or create a Season from event season data."""
        year = season_data.get("year")
        season_type = season_data.get("type", 2)
        if not year:
            return None

        season, _ = Season.objects.get_or_create(
            league=league,
            year=year,
            season_type=season_type,
            defaults={
                "slug": season_data.get("slug", ""),
                "display_name": season_data.get("displayName", ""),
            },
        )
        return season

    def _parse_event_data(
        self, event_data: dict[str, Any], league: League  # noqa: ARG002
    ) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None, dict[str, Any]]:
        """Parse event data from ESPN API.

        Args:
            event_data: Raw event data
            league: League object

        Returns:
            Tuple of (event_fields, competitors_data, venue_data, season_data)
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

        return event_fields, competitors_data, venue_data, season_data

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

    def _ingest_odds(self, event: Event, sport: str, league: str) -> str:
        """Fetch and store odds for an event.

        Calls /odds (all providers), selects Bet365 or Unibet by name,
        parses the decimal odds, and stores them.

        Returns status string: 'created', 'updated', 'no_provider', 'no_odds', 'error'.
        """
        try:
            response = self.client.get_odds(sport, league, event.espn_id)
            items = response.data.get("items", [])
            if not items:
                return "no_odds"

            provider_data = select_provider(items)
            if not provider_data:
                return "no_provider"

            provider_name = provider_data.get("provider", {}).get("name", "unknown")
            parsed = parse_odds_data(provider_data)
            if not parsed:
                return "no_odds"

            _, created = Odds.objects.update_or_create(
                event=event,
                provider=provider_name.lower().replace(" ", ""),
                defaults={**parsed, "raw_data": provider_data},
            )
            return "created" if created else "updated"
        except Exception as e:
            logger.warning(
                "odds_ingestion_skipped",
                event_id=event.espn_id,
                error=str(e),
            )
            return "error"

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
                    event_fields, competitors_data, venue_data, season_data = (
                        self._parse_event_data(event_data, league_obj)
                    )

                    espn_id = event_fields.pop("espn_id")
                    if not espn_id:
                        result.errors += 1
                        continue

                    # Get or create venue
                    venue = self._get_or_create_venue(venue_data)

                    # Get or create season
                    season = self._get_or_create_season(league_obj, season_data)

                    # Create or update event
                    event, created = Event.objects.update_or_create(
                        league=league_obj,
                        espn_id=espn_id,
                        defaults={**event_fields, "venue": venue, "season": season},
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

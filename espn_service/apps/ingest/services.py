"""Data ingestion services for ESPN data.

This module contains services that orchestrate fetching data from ESPN
and persisting it to the database using idempotent upserts.
"""

from dataclasses import dataclass
from datetime import date as date_cls
from datetime import datetime
from typing import Any

import structlog
from django.db import transaction

from apps.core.exceptions import IngestionError
from apps.espn.models import Competitor, Event, League, Sport, Team, Venue
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
    """Get or create Sport and League records."""
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


class TeamIngestionService:
    """Service for ingesting team data from ESPN."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    def _parse_team_data(self, team_data: dict[str, Any]) -> dict[str, Any]:
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
        """Ingest all teams for a sport and league."""
        result = IngestionResult(details=[])

        try:
            _, league_obj = get_or_create_sport_and_league(sport, league)

            response = self.client.get_teams(sport, league)
            sports = response.data.get("sports") or [{}]
            leagues = sports[0].get("leagues") or [{}]
            teams_data = leagues[0].get("teams") or []

            if not teams_data:
                logger.warning("no_teams_found", sport=sport, league=league)
                return result

            for team_data in teams_data:
                try:
                    with transaction.atomic():
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
                    logger.error("team_ingestion_error", team_data=team_data, error=str(e))
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
        competitions = event_data.get("competitions", [])
        competition = competitions[0] if competitions else {}

        status_data = event_data.get("status", {})
        status, status_detail = self._parse_event_status(status_data)

        season_data = event_data.get("season", {})

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

        venue_data = self._parse_venue_data(competition.get("venue", {}))
        competitors_data = competition.get("competitors", [])

        return event_fields, competitors_data, venue_data

    def _get_or_create_venue(self, venue_data: dict[str, Any] | None) -> Venue | None:
        if not venue_data:
            return None
        espn_id = venue_data.pop("espn_id")
        venue, _ = Venue.objects.update_or_create(espn_id=espn_id, defaults=venue_data)
        return venue

    def _create_competitors(
        self,
        event: Event,
        competitors_data: list[dict[str, Any]],
        league: League,
    ) -> int:
        count = 0
        for idx, comp_data in enumerate(competitors_data):
            team_data = comp_data.get("team", {})
            team_id = str(team_data.get("id", ""))

            if not team_id:
                continue

            try:
                team = Team.objects.get(league=league, espn_id=team_id)
            except Team.DoesNotExist:
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

            home_away = comp_data.get("homeAway", "away")
            if home_away not in [Competitor.HOME, Competitor.AWAY]:
                home_away = Competitor.HOME if idx == 1 else Competitor.AWAY

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

    @transaction.atomic
    def ingest_scoreboard(
        self,
        sport: str,
        league: str,
        date: str | None = None,
    ) -> IngestionResult:
        """Ingest scoreboard data for a sport, league, and date."""
        result = IngestionResult(details=[])

        try:
            _, league_obj = get_or_create_sport_and_league(sport, league)

            response = self.client.get_scoreboard(sport, league, date)
            events_data = response.data.get("events", [])

            if not events_data:
                logger.info("no_events_found", sport=sport, league=league, date=date)
                return result

            for event_data in events_data:
                try:
                    with transaction.atomic():
                        event_fields, competitors_data, venue_data = self._parse_event_data(
                            event_data, league_obj
                        )

                        espn_id = event_fields.pop("espn_id")
                        if not espn_id:
                            result.errors += 1
                            continue

                        venue = self._get_or_create_venue(venue_data)

                        event, created = Event.objects.update_or_create(
                            league=league_obj,
                            espn_id=espn_id,
                            defaults={**event_fields, "venue": venue},
                        )

                        event.competitors.all().delete()
                        self._create_competitors(event, competitors_data, league_obj)

                        if created:
                            result.created += 1
                        else:
                            result.updated += 1

                except Exception as e:
                    logger.error("event_ingestion_error", event_id=event_data.get("id"), error=str(e))
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
            logger.exception("scoreboard_ingestion_failed", sport=sport, league=league, date=date)
            raise IngestionError(f"Failed to ingest scoreboard: {e}") from e

        return result


# ---------------------------------------------------------------------------
# New ingestion services — added in audit expansion
# ---------------------------------------------------------------------------


class NewsIngestionService:
    """Service for ingesting news articles from ESPN site API."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    def _parse_article(self, item: dict[str, Any]) -> dict[str, Any] | None:
        espn_id = str(item.get("dataSourceIdentifier") or item.get("id") or "")
        headline = item.get("headline") or item.get("title") or ""
        if not espn_id or not headline:
            return None

        def _parse_dt(s: str) -> datetime | None:
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
            except (ValueError, AttributeError):
                return None

        return {
            "espn_id": espn_id,
            "headline": headline[:500],
            "description": item.get("description") or item.get("abstract") or "",
            "story": item.get("story") or "",
            "published": _parse_dt(item.get("published") or ""),
            "last_modified": _parse_dt(item.get("lastModified") or ""),
            "type": str(item.get("type") or ""),
            "categories": item.get("categories") or [],
            "images": item.get("images") or [],
            "links": item.get("links") or {},
            "raw_data": item,
        }

    @transaction.atomic
    def ingest_news(self, sport: str, league: str, limit: int = 50) -> IngestionResult:
        """Ingest news articles for a sport/league."""
        from apps.espn.models import NewsArticle

        result = IngestionResult(details=[])

        try:
            _, league_obj = get_or_create_sport_and_league(sport, league)

            response = self.client.get_news(sport, league, limit=limit)
            articles_data = response.data.get("articles", [])

            if not articles_data:
                logger.info("no_news_found", sport=sport, league=league)
                return result

            for raw_item in articles_data:
                try:
                    with transaction.atomic():
                        parsed = self._parse_article(raw_item)
                        if not parsed:
                            result.errors += 1
                            continue

                        espn_id = parsed.pop("espn_id")
                        _, created = NewsArticle.objects.update_or_create(
                            espn_id=espn_id,
                            defaults={**parsed, "league": league_obj},
                        )
                        if created:
                            result.created += 1
                        else:
                            result.updated += 1

                except Exception as e:
                    logger.error("news_article_error", error=str(e))
                    result.errors += 1

            logger.info(
                "news_ingested",
                sport=sport,
                league=league,
                created=result.created,
                updated=result.updated,
            )

        except Exception as e:
            logger.exception("news_ingestion_failed", sport=sport, league=league)
            raise IngestionError(f"Failed to ingest news: {e}") from e

        return result


class InjuryIngestionService:
    """Service for ingesting league injury reports from ESPN site API."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    _STATUS_MAP: dict[str, str] = {
        "out": "out",
        "doubtful": "doubtful",
        "questionable": "questionable",
        "injured reserve": "ir",
        "ir": "ir",
        "day-to-day": "day_to_day",
        "probable": "day_to_day",
    }

    def _normalize_status(self, raw: str) -> str:
        return self._STATUS_MAP.get(raw.lower().strip(), "other")

    def _parse_injury(self, item: dict[str, Any]) -> dict[str, Any] | None:
        athlete_data = item.get("athlete") or {}
        athlete_name = athlete_data.get("displayName") or athlete_data.get("fullName") or ""
        if not athlete_name:
            return None

        raw_status = item.get("status") or ""
        team_data = item.get("team") or athlete_data.get("team") or {}

        injury_type = item.get("type") or (item.get("details") or {}).get("type") or ""
        if isinstance(injury_type, dict):
            injury_type = injury_type.get("description") or injury_type.get("name") or ""

        return {
            "athlete_espn_id": str(athlete_data.get("id") or ""),
            "athlete_name": athlete_name,
            "position": (athlete_data.get("position") or {}).get("abbreviation") or "",
            "status": self._normalize_status(raw_status),
            "status_display": raw_status,
            "description": item.get("description") or item.get("shortComment") or "",
            "injury_type": injury_type,
            "team_espn_id": str(team_data.get("id") or ""),
            "raw_data": item,
        }

    @transaction.atomic
    def ingest_injuries(self, sport: str, league: str) -> IngestionResult:
        """Clear and re-ingest all league injuries (snapshot refresh)."""
        from apps.espn.models import Injury

        result = IngestionResult(details=[])

        try:
            _, league_obj = get_or_create_sport_and_league(sport, league)

            response = self.client.get_league_injuries(sport, league)
            data = response.data
            items = data.get("injuries") if "injuries" in data else data.get("items")
            if not isinstance(items, list):
                raise ValueError("Expected an injury snapshot list")

            # Validate the complete snapshot before replacing existing records.
            # The live Site API groups athlete injuries under each team's id.
            parsed_items = []
            for group in items:
                if not isinstance(group, dict):
                    raise ValueError("Invalid injury entry")
                entries = group.get("injuries", [group])
                if not isinstance(entries, list):
                    raise ValueError("Invalid team injury list")
                for item in entries:
                    if not isinstance(item, dict):
                        raise ValueError("Invalid athlete injury")
                    item = dict(item)
                    if "injuries" in group and not item.get("team"):
                        item["team"] = {"id": group.get("id", "")}
                    parsed = self._parse_injury(item)
                    if not parsed:
                        raise ValueError("Injury entry has no athlete name")
                    parsed_items.append(parsed)

            League.objects.select_for_update().get(pk=league_obj.pk)

            # Injuries are a snapshot — delete stale entries then re-insert
            deleted, _ = Injury.objects.filter(league=league_obj).delete()
            logger.debug("cleared_old_injuries", count=deleted, sport=sport, league=league)

            for parsed in parsed_items:
                team_espn_id = parsed.pop("team_espn_id", "")
                team_obj = (
                    Team.objects.filter(league=league_obj, espn_id=team_espn_id).first()
                    if team_espn_id
                    else None
                )
                Injury.objects.create(league=league_obj, team=team_obj, **parsed)
                result.created += 1

            logger.info(
                "injuries_ingested",
                sport=sport,
                league=league,
                created=result.created,
                errors=result.errors,
            )

        except Exception as e:
            logger.exception("injury_ingestion_failed", sport=sport, league=league)
            raise IngestionError(f"Failed to ingest injuries: {e}") from e

        return result


class TransactionIngestionService:
    """Service for ingesting league transactions from ESPN site API."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    def _parse_transaction(self, item: dict[str, Any]) -> dict[str, Any] | None:
        description = item.get("description") or item.get("text") or ""
        if not description:
            return None

        raw_date = item.get("date") or ""
        txn_date: date_cls | None = None
        try:
            if raw_date:
                txn_date = date_cls.fromisoformat(raw_date[:10])
        except (ValueError, TypeError):
            pass

        athlete_data = item.get("athlete") or {}
        team_data = item.get("team") or {}

        return {
            "espn_id": str(item.get("id") or ""),
            "date": txn_date,
            "description": description,
            "type": item.get("type") or "",
            "athlete_name": athlete_data.get("displayName") or "",
            "athlete_espn_id": str(athlete_data.get("id") or ""),
            "team_espn_id": str(team_data.get("id") or ""),
            "raw_data": item,
        }

    @transaction.atomic
    def ingest_transactions(self, sport: str, league: str) -> IngestionResult:
        """Ingest recent transactions for a sport/league."""
        from apps.espn.models import Transaction

        result = IngestionResult(details=[])

        try:
            _, league_obj = get_or_create_sport_and_league(sport, league)

            response = self.client.get_league_transactions(sport, league)
            items = response.data.get("items") or response.data.get("transactions") or []

            if not items:
                logger.info("no_transactions_found", sport=sport, league=league)
                return result

            for raw_item in items:
                try:
                    with transaction.atomic():
                        parsed = self._parse_transaction(raw_item)
                        if not parsed:
                            result.errors += 1
                            continue

                        team_espn_id = parsed.pop("team_espn_id", "")
                        team_obj = (
                            Team.objects.filter(league=league_obj, espn_id=team_espn_id).first()
                            if team_espn_id
                            else None
                        )

                        from apps.espn.identity import transaction_identity

                        identity_key = transaction_identity(
                            parsed["espn_id"], parsed["date"], parsed["description"],
                            team_espn_id, parsed["athlete_espn_id"],
                        )
                        _, created = Transaction.objects.update_or_create(
                            league=league_obj,
                            identity_key=identity_key,
                            defaults={**parsed, "team": team_obj},
                        )

                        if created:
                            result.created += 1
                        else:
                            result.updated += 1

                except Exception as e:
                    logger.error("transaction_ingestion_error", error=str(e))
                    result.errors += 1

            logger.info(
                "transactions_ingested",
                sport=sport,
                league=league,
                created=result.created,
                updated=result.updated,
                errors=result.errors,
            )

        except Exception as e:
            logger.exception("transactions_ingestion_failed", sport=sport, league=league)
            raise IngestionError(f"Failed to ingest transactions: {e}") from e

        return result


class AthleteStatsIngestionService:
    """Service for ingesting athlete season stats from common/v3 endpoint."""

    def __init__(self, client: ESPNClient | None = None):
        self.client = client or get_espn_client()

    @transaction.atomic
    def ingest_athlete_stats(
        self,
        sport: str,
        league: str,
        athlete_espn_id: str | int,
        season: int | None = None,
        season_type: int = 2,
    ) -> IngestionResult:
        """Ingest season stats for a single athlete."""
        from apps.espn.models import Athlete, AthleteSeasonStats

        result = IngestionResult(details=[])

        try:
            _, league_obj = get_or_create_sport_and_league(sport, league)

            response = self.client.get_athlete_stats(
                sport, league, int(athlete_espn_id), season=season, season_type=season_type
            )
            data = response.data

            athlete_obj = Athlete.objects.filter(espn_id=str(athlete_espn_id)).first()
            athlete_name = athlete_obj.display_name if athlete_obj else str(athlete_espn_id)
            season_val = season or (data.get("season") or {}).get("year")
            if not season_val:
                raise ValueError("Specify season when the athlete response has no season year")

            stats = data.get("stats") or data.get("splits") or {}
            if data.get("categories"):
                stats = []
                for category in data["categories"]:
                    selected = dict(category)
                    if "statistics" in category:
                        selected["statistics"] = [
                            row for row in category["statistics"]
                            if (row.get("season") or {}).get("year") == season_val
                        ]
                        # Upstream totals span the athlete's career, not this season.
                        selected.pop("totals", None)
                    stats.append(selected)

            _, created = AthleteSeasonStats.objects.update_or_create(
                league=league_obj,
                athlete_espn_id=str(athlete_espn_id),
                season_year=season_val,
                season_type=season_type,
                defaults={
                    "athlete": athlete_obj,
                    "athlete_name": athlete_name,
                    "stats": stats,
                    "raw_data": data,
                },
            )

            if created:
                result.created += 1
            else:
                result.updated += 1

            logger.info(
                "athlete_stats_ingested",
                sport=sport,
                league=league,
                athlete_espn_id=athlete_espn_id,
                season=season_val,
            )

        except Exception as e:
            logger.exception(
                "athlete_stats_ingestion_failed",
                sport=sport,
                league=league,
                athlete_espn_id=athlete_espn_id,
            )
            raise IngestionError(f"Failed to ingest athlete stats: {e}") from e

        return result

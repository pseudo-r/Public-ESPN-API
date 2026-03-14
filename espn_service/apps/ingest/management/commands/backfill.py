"""Management command to backfill historical event data from ESPN."""

import time

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import (
    ScoreboardIngestionService,
    get_or_create_sport_and_league,
)
from clients.espn_client import ESPNEndpointDomain, get_espn_client


class Command(BaseCommand):
    """Backfill historical events and odds for a sport/league/season."""

    help = "Backfill historical events and odds for a sport/league/season"

    def add_arguments(self, parser):
        parser.add_argument("sport", type=str, help="Sport slug (e.g., soccer)")
        parser.add_argument("league", type=str, help="League slug (e.g., fra.1)")
        parser.add_argument(
            "--season", type=int, required=True, help="Season year (e.g., 2024)"
        )
        parser.add_argument(
            "--dates",
            type=str,
            default=None,
            help="Date range YYYYMMDD-YYYYMMDD (overrides --season auto-detection)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.5,
            help="Delay between API calls in seconds (default: 0.5)",
        )

    def handle(self, *args, **options):
        sport = options["sport"].lower()
        league = options["league"].lower()
        season = options["season"]
        dates = options["dates"]
        delay = options["delay"]

        self.stdout.write(f"Backfilling {sport}/{league} season {season} (delay: {delay}s)...")

        try:
            client = get_espn_client()
            service = ScoreboardIngestionService(client=client)
            _, league_obj = get_or_create_sport_and_league(sport, league)

            # Get date range from season metadata or --dates override
            if not dates:
                dates = self._get_season_dates(client, sport, league, season)
            self.stdout.write(f"Date range: {dates}")

            # List all events for the season via core API
            event_ids = self._list_season_events(client, sport, league, dates, delay)
            total = len(event_ids)
            self.stdout.write(f"Found {total} events")

            created = 0
            updated = 0
            errors = 0
            odds_stats = {"created": 0, "updated": 0, "no_odds": 0, "no_provider": 0, "error": 0}

            for idx, event_id in enumerate(event_ids, 1):
                try:
                    # Fetch event summary
                    response = client.get_event(sport, league, event_id)
                    events_data = response.data.get("events", [])
                    if not events_data:
                        header = response.data.get("header", {})
                        if header:
                            events_data = [self._header_to_event(header, response.data)]

                    for event_data in events_data:
                        event_fields, competitors_data, venue_data, season_data = (
                            service._parse_event_data(event_data, league_obj)
                        )
                        espn_id = event_fields.pop("espn_id")
                        if not espn_id:
                            continue

                        venue = service._get_or_create_venue(venue_data)
                        season = service._get_or_create_season(league_obj, season_data)
                        from apps.espn.models import Event

                        event, was_created = Event.objects.update_or_create(
                            league=league_obj,
                            espn_id=espn_id,
                            defaults={**event_fields, "venue": venue, "season": season},
                        )
                        event.competitors.all().delete()
                        service._create_competitors(event, competitors_data, league_obj)
                        odds_status = service._ingest_odds(event, sport, league)
                        odds_stats[odds_status] = odds_stats.get(odds_status, 0) + 1

                        if was_created:
                            created += 1
                        else:
                            updated += 1

                    odds_icon = "🎲" if odds_status in ("created", "updated") else "⊘"
                    self.stdout.write(f"[{idx}/{total}] Event {event_id} ✓ {odds_icon}")

                except Exception as e:
                    self.stderr.write(f"[{idx}/{total}] Event {event_id} ✗ {e}")
                    errors += 1

                if delay > 0:
                    time.sleep(delay)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\nBackfill complete:"
                    f"\n  Events: created={created}, updated={updated}, errors={errors}"
                    f"\n  Odds:   created={odds_stats['created']}, updated={odds_stats['updated']}, "
                    f"no_odds={odds_stats['no_odds']}, no_provider={odds_stats['no_provider']}, "
                    f"errors={odds_stats['error']}"
                )
            )

        except Exception as e:
            raise CommandError(f"Backfill failed: {e}") from e

    def _header_to_event(self, header: dict, full_data: dict) -> dict:
        """Convert summary header format to scoreboard event format."""
        competitions = header.get("competitions", [])
        competition = competitions[0] if competitions else {}

        return {
            "id": header.get("id", ""),
            "uid": header.get("uid", full_data.get("uid", "")),
            "date": competition.get("date", ""),
            "name": full_data.get("gameInfo", {}).get("name", ""),
            "shortName": header.get("shortName", ""),
            "season": header.get("season", full_data.get("season", {})),
            "status": competition.get("status", {}),
            "competitions": competitions,
        }

    def _get_season_dates(self, client, sport: str, league: str, season: int) -> str:
        """Fetch season start/end dates from ESPN API and cache in Season model."""
        from datetime import date

        from apps.espn.models import Season

        response = client.get(
            f"/v2/sports/{sport}/leagues/{league}/seasons/{season}",
            domain=ESPNEndpointDomain.CORE,
        )
        data = response.data
        start = data.get("startDate", "")[:10]
        end = data.get("endDate", "")[:10]
        if not start or not end:
            raise CommandError(
                f"Could not determine dates for season {season}. "
                f"Use --dates YYYYMMDD-YYYYMMDD manually."
            )

        # Cache season metadata
        _, league_obj = get_or_create_sport_and_league(sport, league)
        season_type_val = data.get("type", 2)
        if isinstance(season_type_val, dict):
            season_type_val = season_type_val.get("type", 2)
        Season.objects.update_or_create(
            league=league_obj,
            year=season,
            season_type=season_type_val,
            defaults={
                "start_date": date.fromisoformat(start),
                "end_date": date.fromisoformat(end),
                "display_name": data.get("displayName", ""),
                "slug": data.get("slug", ""),
                "raw_data": data,
            },
        )

        return f"{start.replace('-', '')}-{end.replace('-', '')}"

    def _list_season_events(
        self, client, sport: str, league: str, dates: str, delay: float
    ) -> list[str]:
        """List all event IDs for a season using core API pagination."""
        event_ids = []
        page = 1

        while True:
            response = client.get(
                f"/v2/sports/{sport}/leagues/{league}/events",
                domain=ESPNEndpointDomain.CORE,
                params={"dates": dates, "limit": 100, "page": page},
            )
            data = response.data
            items = data.get("items", [])

            for item in items:
                ref = item.get("$ref", "")
                parts = ref.split("/events/")
                if len(parts) > 1:
                    eid = parts[1].split("?")[0].split("/")[0]
                    event_ids.append(eid)

            page_count = data.get("pageCount", 1)
            if page >= page_count:
                break
            page += 1

            if delay > 0:
                time.sleep(delay)

        return event_ids

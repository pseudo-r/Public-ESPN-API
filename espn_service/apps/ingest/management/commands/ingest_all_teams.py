"""Management command to ingest teams for all configured leagues."""

from argparse import BooleanOptionalAction

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import TeamIngestionService
from clients.leagues import ALL_LEAGUES


class Command(BaseCommand):
    """Django management command to ingest teams for all supported leagues."""

    help = (
        "Ingest team data from ESPN for all configured leagues. "
        "Use --sport to filter by sport or --dry-run to preview without ingesting."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--sport",
            type=str,
            default=None,
            help="Optional: filter to a single sport slug (e.g., basketball)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print leagues that would be ingested without actually ingesting",
        )
        parser.add_argument(
            "--continue-on-error",
            action=BooleanOptionalAction,
            default=True,
            help="Continue processing remaining leagues if one fails (default: True)",
        )

    def handle(self, *args, **options):
        sport_filter = options.get("sport")
        dry_run = options["dry_run"]
        continue_on_error = options["continue_on_error"]

        leagues = ALL_LEAGUES
        if sport_filter:
            leagues = [(s, league_slug) for s, league_slug in ALL_LEAGUES if s == sport_filter.lower()]
            if not leagues:
                raise CommandError(
                    f"No leagues configured for sport: {sport_filter}. "
                    f"Available sports: {sorted({s for s, _ in ALL_LEAGUES})}"
                )

        self.stdout.write(
            f"{'[DRY RUN] ' if dry_run else ''}Ingesting teams for "
            f"{len(leagues)} league(s)"
            + (f" (sport: {sport_filter})" if sport_filter else "")
        )

        if dry_run:
            for sport, league in leagues:
                self.stdout.write(f"  • {sport}/{league}")
            return

        total_created = 0
        total_updated = 0
        total_errors = 0
        failures = []

        for sport, league in leagues:
            self.stdout.write(f"  Ingesting {sport}/{league}...", ending="")

            try:
                service = TeamIngestionService()
                result = service.ingest_teams(sport, league)
                total_created += result.created
                total_updated += result.updated
                total_errors += result.errors

                status_str = (
                    self.style.SUCCESS(
                        f" ✓ created={result.created} updated={result.updated}"
                        + (f" errors={result.errors}" if result.errors else "")
                    )
                )
                self.stdout.write(status_str)

            except Exception as e:
                failure_msg = f" ✗ {e}"
                self.stdout.write(self.style.ERROR(failure_msg))
                failures.append(f"{sport}/{league}: {e}")
                if not continue_on_error:
                    raise CommandError(f"Stopped at {sport}/{league}: {e}") from e

        # Summary
        self.stdout.write("\n" + "─" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Total: created={total_created} updated={total_updated} "
                f"errors={total_errors} failed_leagues={len(failures)}"
            )
        )
        if failures:
            self.stdout.write(self.style.WARNING("Failed leagues:"))
            for f in failures:
                self.stdout.write(self.style.WARNING(f"  • {f}"))

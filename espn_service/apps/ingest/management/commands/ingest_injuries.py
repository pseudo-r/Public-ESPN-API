"""Management command to ingest ESPN injury reports."""

import argparse

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import InjuryIngestionService
from apps.ingest.tasks import ALL_LEAGUES_CONFIG


class Command(BaseCommand):
    help = "Refresh ESPN injury reports for one or all configured leagues."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--sport", type=str, help="Sport slug (e.g., football)")
        parser.add_argument("--league", type=str, help="League slug (e.g., nfl)")

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        sport = options.get("sport")
        league = options.get("league")

        if sport and league:
            leagues = [(sport.lower(), league.lower())]
        elif sport or league:
            raise CommandError("Provide both --sport and --league, or neither to run all leagues.")
        else:
            leagues = ALL_LEAGUES_CONFIG

        service = InjuryIngestionService()
        total_created = total_errors = 0

        for s, league_slug in leagues:
            try:
                result = service.ingest_injuries(s, league_slug)
                total_created += result.created
                total_errors += result.errors
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [{s}/{league_slug}] created={result.created} errors={result.errors}"
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [{s}/{league_slug}] FAILED: {e}"))
                total_errors += 1

        self.stdout.write(
            self.style.SUCCESS(f"\nDone — created={total_created} errors={total_errors}")
        )

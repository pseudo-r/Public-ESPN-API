"""Management command to ingest ESPN transactions."""

import argparse

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import TransactionIngestionService
from apps.ingest.tasks import ALL_LEAGUES_CONFIG


class Command(BaseCommand):
    help = "Ingest ESPN transaction records for one or all configured leagues."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--sport", type=str, help="Sport slug (e.g., basketball)")
        parser.add_argument("--league", type=str, help="League slug (e.g., nba)")

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        sport = options.get("sport")
        league = options.get("league")

        if sport and league:
            leagues = [(sport.lower(), league.lower())]
        elif sport or league:
            raise CommandError("Provide both --sport and --league, or neither to run all leagues.")
        else:
            leagues = ALL_LEAGUES_CONFIG

        service = TransactionIngestionService()
        total_created = total_updated = total_errors = 0

        for s, league_slug in leagues:
            try:
                result = service.ingest_transactions(s, league_slug)
                total_created += result.created
                total_updated += result.updated
                total_errors += result.errors
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [{s}/{league_slug}] created={result.created} updated={result.updated} errors={result.errors}"
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [{s}/{league_slug}] FAILED: {e}"))
                total_errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone — created={total_created} updated={total_updated} errors={total_errors}"
            )
        )

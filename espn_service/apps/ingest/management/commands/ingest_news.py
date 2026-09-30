"""Management command to ingest ESPN news articles."""

import argparse

import structlog
from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import NewsIngestionService
from apps.ingest.tasks import ALL_LEAGUES_CONFIG

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Ingest ESPN news articles for one or all configured leagues."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--sport", type=str, help="Sport slug (e.g., basketball)")
        parser.add_argument("--league", type=str, help="League slug (e.g., nba)")
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Number of articles to fetch per league (default: 50)",
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        sport = options.get("sport")
        league = options.get("league")
        limit: int = options["limit"]

        if sport and league:
            leagues = [(sport.lower(), league.lower())]
        elif sport or league:
            raise CommandError("Provide both --sport and --league, or neither to run all leagues.")
        else:
            leagues = ALL_LEAGUES_CONFIG

        service = NewsIngestionService()
        total_created = total_updated = total_errors = 0

        for s, league_slug in leagues:
            try:
                result = service.ingest_news(s, league_slug, limit=limit)
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

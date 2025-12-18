"""Management command to ingest scoreboard data from ESPN."""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import ScoreboardIngestionService


class Command(BaseCommand):
    """Django management command to ingest scoreboard data from ESPN."""

    help = "Ingest scoreboard/event data from ESPN for a given sport, league, and date"

    def add_arguments(self, parser):
        parser.add_argument(
            "sport",
            type=str,
            help="Sport slug (e.g., basketball, football)",
        )
        parser.add_argument(
            "league",
            type=str,
            help="League slug (e.g., nba, nfl)",
        )
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help="Date in YYYYMMDD format (default: today)",
        )

    def handle(self, *args, **options):
        sport = options["sport"].lower()
        league = options["league"].lower()
        date = options["date"]

        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        self.stdout.write(f"Ingesting scoreboard for {sport}/{league} on {date}...")

        try:
            service = ScoreboardIngestionService()
            result = service.ingest_scoreboard(sport, league, date)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully ingested scoreboard:\n"
                    f"  Created: {result.created}\n"
                    f"  Updated: {result.updated}\n"
                    f"  Errors: {result.errors}\n"
                    f"  Total processed: {result.total_processed}"
                )
            )

        except Exception as e:
            raise CommandError(f"Failed to ingest scoreboard: {e}") from e

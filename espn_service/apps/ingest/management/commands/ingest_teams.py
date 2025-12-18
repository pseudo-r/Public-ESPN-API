"""Management command to ingest teams from ESPN."""

from django.core.management.base import BaseCommand, CommandError

from apps.ingest.services import TeamIngestionService


class Command(BaseCommand):
    """Django management command to ingest teams from ESPN."""

    help = "Ingest team data from ESPN for a given sport and league"

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

    def handle(self, *args, **options):
        sport = options["sport"].lower()
        league = options["league"].lower()

        self.stdout.write(f"Ingesting teams for {sport}/{league}...")

        try:
            service = TeamIngestionService()
            result = service.ingest_teams(sport, league)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully ingested teams:\n"
                    f"  Created: {result.created}\n"
                    f"  Updated: {result.updated}\n"
                    f"  Errors: {result.errors}\n"
                    f"  Total processed: {result.total_processed}"
                )
            )

        except Exception as e:
            raise CommandError(f"Failed to ingest teams: {e}") from e

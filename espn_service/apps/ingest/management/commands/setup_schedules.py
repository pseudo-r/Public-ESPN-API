"""Create default Django-Q2 schedules if they don't exist."""

from django.core.management.base import BaseCommand
from django_q.models import Schedule

DEFAULT_SCHEDULES = [
    {
        "name": "NBA scoreboard (hourly)",
        "func": "apps.ingest.tasks.refresh_scoreboard",
        "args": '["basketball", "nba"]',
        "schedule_type": Schedule.CRON,
        "cron": "0 * * * *",
    },
    {
        "name": "NFL scoreboard (hourly)",
        "func": "apps.ingest.tasks.refresh_scoreboard",
        "args": '["football", "nfl"]',
        "schedule_type": Schedule.CRON,
        "cron": "0 * * * *",
    },
    {
        "name": "All teams (weekly)",
        "func": "apps.ingest.tasks.refresh_all_teams",
        "schedule_type": Schedule.CRON,
        "cron": "0 3 * * 1",
    },
    {
        "name": "Purge old results (daily)",
        "func": "apps.ingest.tasks.purge_old_results",
        "schedule_type": Schedule.CRON,
        "cron": "0 4 * * *",
    },
]


class Command(BaseCommand):
    help = "Create default Django-Q2 schedules if they don't exist"

    def handle(self, *args, **options):
        for sched in DEFAULT_SCHEDULES:
            obj, created = Schedule.objects.get_or_create(
                name=sched["name"],
                defaults=sched,
            )
            status = "created" if created else "already exists"
            self.stdout.write(f"  {sched['name']}: {status}")

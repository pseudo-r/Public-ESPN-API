from django.db import migrations


def populate_seasons(apps, schema_editor):
    """Create Season records from distinct Event season_year/season_type combos."""
    Event = apps.get_model("espn", "Event")
    Season = apps.get_model("espn", "Season")

    distinct_seasons = (
        Event.objects.values("league_id", "season_year", "season_type", "season_slug").distinct()
    )

    for row in distinct_seasons:
        season, _ = Season.objects.get_or_create(
            league_id=row["league_id"],
            year=row["season_year"],
            season_type=row["season_type"],
            defaults={
                "slug": row["season_slug"] or "",
            },
        )
        # Link events to this season
        Event.objects.filter(
            league_id=row["league_id"],
            season_year=row["season_year"],
            season_type=row["season_type"],
        ).update(season_id=season.pk)


def reverse_populate(apps, schema_editor):
    """Clear season FK on events (scalar fields still exist)."""
    Event = apps.get_model("espn", "Event")
    Event.objects.all().update(season_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ("espn", "0002_season"),
    ]

    operations = [
        migrations.RunPython(populate_seasons, reverse_populate),
    ]

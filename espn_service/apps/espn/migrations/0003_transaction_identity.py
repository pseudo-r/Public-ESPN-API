"""Consolidate duplicate transactions before enforcing refresh idempotency.

Keeps the most recently updated row for each league/identity. Duplicate rows
cannot be restored by reversing this migration; back up the database first.
"""

import hashlib
import json

from django.db import migrations, models


def backfill(apps, schema_editor):
    transaction = apps.get_model("espn", "Transaction")
    alias = schema_editor.connection.alias
    seen = set()
    for row in transaction.objects.using(alias).select_related("team").order_by("-updated_at", "-pk").iterator():
        team_id = (row.raw_data.get("team") or {}).get("id")
        if not team_id and row.team_id:
            team_id = row.team.espn_id
        fields = ["espn", str(row.espn_id)] if row.espn_id else [
            "natural", str(row.date or ""), row.description,
            str(team_id or ""), str(row.athlete_espn_id or ""),
        ]
        key = hashlib.sha256(json.dumps(fields, ensure_ascii=False).encode()).hexdigest()
        identity = (row.league_id, key)
        if identity in seen:
            transaction.objects.using(alias).filter(pk=row.pk).delete()
        else:
            seen.add(identity)
            transaction.objects.using(alias).filter(pk=row.pk).update(identity_key=key)


class Migration(migrations.Migration):
    dependencies = [("espn", "0002_injury_newsarticle_transaction_athleteseasonstats")]
    operations = [
        migrations.AddField("transaction", "identity_key", models.CharField(default="", editable=False, max_length=64)),
        migrations.RunPython(backfill, migrations.RunPython.noop),
        migrations.AddConstraint("transaction", models.UniqueConstraint(fields=("league", "identity_key"), name="unique_transaction_identity")),
    ]

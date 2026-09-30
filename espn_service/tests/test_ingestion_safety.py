"""Real database failures, migration upgrades, and concurrent refresh regression tests."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import MagicMock, patch

import pytest
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.db.migrations.executor import MigrationExecutor

from apps.espn.models import Competitor, Event, Team, Transaction
from apps.ingest.services import (
    ScoreboardIngestionService,
    TeamIngestionService,
    TransactionIngestionService,
    get_or_create_sport_and_league,
)
from clients.espn_client import ESPNResponse


@pytest.mark.django_db
def test_bad_team_database_write_does_not_poison_next_record():
    client = MagicMock()
    client.get_teams.return_value = ESPNResponse(
        {
            "sports": [
                {
                    "leagues": [
                        {
                            "teams": [
                                {"team": {"id": "bad", "displayName": None}},
                                {"team": {"id": "good", "displayName": "Good team"}},
                            ]
                        }
                    ]
                }
            ]
        },
        200,
        "test",
    )
    result = TeamIngestionService(client).ingest_teams("football", "nfl")
    assert (result.created, result.errors) == (1, 1)
    assert list(Team.objects.values_list("espn_id", flat=True)) == ["good"]


@pytest.mark.django_db
def test_event_competitor_failure_rolls_back_event_replacement(mock_scoreboard_response):
    client = MagicMock()
    client.get_scoreboard.return_value = ESPNResponse(mock_scoreboard_response, 200, "test")
    service = ScoreboardIngestionService(client)
    service.ingest_scoreboard("basketball", "nba")
    before = list(Competitor.objects.values_list("pk", "event_id", "team_id"))
    with patch.object(
        service, "_create_competitors", side_effect=IntegrityError("failed competitor")
    ):
        result = service.ingest_scoreboard("basketball", "nba")
    assert result.errors == len(mock_scoreboard_response["events"])
    assert list(Competitor.objects.values_list("pk", "event_id", "team_id")) == before
    assert Event.objects.count() == len(mock_scoreboard_response["events"])


@pytest.mark.django_db
def test_database_rejects_duplicate_transaction_identity():
    _, league = get_or_create_sport_and_league("football", "nfl")
    Transaction.objects.create(league=league, description="Signed player")
    with pytest.raises(IntegrityError), transaction.atomic():
        Transaction.objects.create(league=league, description="Signed player")
    assert Transaction.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_duplicate_transaction_migration_retains_newest():
    old = [("espn", "0002_injury_newsarticle_transaction_athleteseasonstats")]
    new = [("espn", "0003_transaction_identity")]
    executor = MigrationExecutor(connection)
    executor.migrate(old)
    try:
        apps = executor.loader.project_state(old).apps
        sport = apps.get_model("espn", "Sport").objects.create(slug="football", name="Football")
        league = apps.get_model("espn", "League").objects.create(
            sport=sport, slug="nfl", name="NFL"
        )
        model = apps.get_model("espn", "Transaction")
        model.objects.create(league=league, espn_id="", description="Signed player")
        newest = model.objects.create(league=league, espn_id="", description="Signed player")
        executor = MigrationExecutor(connection)
        executor.migrate(new)
        assert Transaction.objects.get().pk == newest.pk
        assert len(Transaction.objects.get().identity_key) == 64
    finally:
        MigrationExecutor(connection).migrate(new)


@pytest.mark.django_db(transaction=True)
def test_simultaneous_transaction_refreshes_are_unique():
    if connection.vendor != "postgresql":
        pytest.skip("Concurrency test requires PostgreSQL; exercised in CI/Compose")
    get_or_create_sport_and_league("football", "nfl")
    barrier = Barrier(2)

    def refresh():
        close_old_connections()
        try:
            client = MagicMock()
            client.get_league_transactions.return_value = ESPNResponse(
                {
                    "transactions": [
                        {"date": "2026-09-30", "description": "Signed player", "team": {"id": "4"}},
                    ]
                },
                200,
                "test",
            )
            barrier.wait(timeout=10)
            return TransactionIngestionService(client).ingest_transactions("football", "nfl")
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: refresh(), range(2)))
    assert sum(r.errors for r in results) == 0
    assert sum(r.created for r in results) == 1
    assert sum(r.updated for r in results) == 1
    assert Transaction.objects.count() == 1

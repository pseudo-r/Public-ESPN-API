"""Regressions found by comparing live ESPN responses with ingestion assumptions."""

from unittest.mock import MagicMock

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.core.exceptions import (
    ESPNClientError,
    ESPNNotFoundError,
    ESPNRateLimitError,
    IngestionError,
)
from apps.espn.models import AthleteSeasonStats, Injury, Transaction
from apps.ingest.services import (
    AthleteStatsIngestionService,
    InjuryIngestionService,
    TransactionIngestionService,
    get_or_create_sport_and_league,
)
from clients.espn_client import ESPNClient, ESPNResponse


@pytest.mark.parametrize("status,error", [(400, ESPNClientError), (403, ESPNClientError), (404, ESPNNotFoundError), (429, ESPNRateLimitError)])
def test_terminal_errors_are_not_retried(httpx_mock, status, error):
    httpx_mock.add_response(status_code=status)
    with ESPNClient(max_retries=3) as client, pytest.raises(error):
        client.get_scoreboard("football", "nfl")
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.django_db
def test_grouped_injury_snapshot_and_empty_refresh():
    client = MagicMock()
    client.get_league_injuries.return_value = ESPNResponse({"injuries": [{
        "id": "12", "injuries": [{"athlete": {"id": "1", "displayName": "Player"},
                                   "status": "Out", "type": {"description": "Ankle"}}],
    }]}, 200, "test")
    service = InjuryIngestionService(client)
    assert service.ingest_injuries("football", "nfl").created == 1
    assert Injury.objects.get().injury_type == "Ankle"
    client.get_league_injuries.return_value = ESPNResponse({"injuries": []}, 200, "test")
    service.ingest_injuries("football", "nfl")
    assert not Injury.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("data", [{}, {"injuries": [{}]}, {"injuries": "invalid"}])
def test_malformed_snapshot_preserves_existing_injuries(data):
    _, league = get_or_create_sport_and_league("football", "nfl")
    Injury.objects.create(league=league, athlete_name="Existing", status="out")
    client = MagicMock()
    client.get_league_injuries.return_value = ESPNResponse(data, 200, "test")
    with pytest.raises(IngestionError):
        InjuryIngestionService(client).ingest_injuries("football", "nfl")
    assert Injury.objects.get().athlete_name == "Existing"


@pytest.mark.django_db
def test_transactions_without_ids_are_idempotent():
    client = MagicMock()
    client.get_league_transactions.return_value = ESPNResponse({"transactions": [
        {"date": "2026-09-29T07:00Z", "description": "Signed a player", "team": {"id": "4"}},
    ]}, 200, "test")
    service = TransactionIngestionService(client)
    assert service.ingest_transactions("football", "nfl").created == 1
    assert service.ingest_transactions("football", "nfl").updated == 1
    assert Transaction.objects.count() == 1


@pytest.mark.django_db
def test_common_v3_stats_preserve_categories_and_require_season():
    client = MagicMock()
    current = {"season": {"year": 2026}, "stats": ["10"]}
    categories = [{"name": "passing", "statistics": [{"season": {"year": 2025}}, current], "totals": ["99"]}]
    client.get_athlete_stats.return_value = ESPNResponse({"categories": categories}, 200, "test")
    service = AthleteStatsIngestionService(client)
    with pytest.raises(IngestionError):
        service.ingest_athlete_stats("football", "nfl", "3139477")
    assert not AthleteSeasonStats.objects.exists()
    service.ingest_athlete_stats("football", "nfl", "3139477", season=2026)
    saved = AthleteSeasonStats.objects.get()
    assert saved.stats == [{"name": "passing", "statistics": [current]}]
    assert saved.raw_data["categories"] == categories


def test_new_client_routes(httpx_mock):
    httpx_mock.add_response(url="https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/12/schedule?season=2026", json={"events": []})
    httpx_mock.add_response(url="https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/3139477/bio", json={"awards": []})
    with ESPNClient() as client:
        assert client.get_team_schedule("football", "nfl", "12", 2026).data == {"events": []}
        assert client.get_athlete_bio("football", "nfl", 3139477).data == {"awards": []}


@pytest.mark.django_db
@override_settings(INGEST_PERMISSION_CLASSES=["rest_framework.permissions.IsAdminUser"])
@pytest.mark.parametrize("resource", ["teams", "scoreboard", "news", "injuries", "transactions"])
def test_production_ingestion_rejects_anonymous_writes(resource):
    response = APIClient().post(f"/api/v1/ingest/{resource}/", {"sport": "football", "league": "nfl"})
    assert response.status_code in (401, 403)

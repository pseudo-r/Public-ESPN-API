"""Tests for new ingestion services and REST API endpoints.

Covers: NewsIngestionService, InjuryIngestionService, TransactionIngestionService,
Celery tasks, and REST GET endpoints for news/injuries/transactions/athlete-stats.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.espn.models import Injury, League, NewsArticle, Sport, Team, Transaction
from apps.ingest.services import (
    IngestionResult,
    InjuryIngestionService,
    NewsIngestionService,
    TransactionIngestionService,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_league(sport_slug: str = "basketball", league_slug: str = "nba") -> tuple[Sport, League]:
    sport, _ = Sport.objects.get_or_create(slug=sport_slug, defaults={"name": sport_slug.title()})
    league, _ = League.objects.get_or_create(
        sport=sport,
        slug=league_slug,
        defaults={"name": league_slug.upper(), "abbreviation": league_slug.upper()[:5]},
    )
    return sport, league


def _make_espn_response(data: dict) -> MagicMock:
    resp = MagicMock()
    resp.data = data
    return resp


# ---------------------------------------------------------------------------
# NewsIngestionService
# ---------------------------------------------------------------------------


class TestNewsIngestionService(TestCase):
    """Tests for NewsIngestionService.ingest_news()."""

    def setUp(self) -> None:
        self.client_mock = MagicMock()
        self.service = NewsIngestionService(client=self.client_mock)
        _, self.league = _make_league("basketball", "nba")

    def test_ingest_creates_new_articles(self) -> None:
        """Two new articles should be created."""
        self.client_mock.get_news.return_value = _make_espn_response({
            "articles": [
                {
                    "dataSourceIdentifier": "art-001",
                    "headline": "LeBron scores 50",
                    "published": "2024-01-15T20:00:00Z",
                    "type": "Story",
                },
                {
                    "dataSourceIdentifier": "art-002",
                    "headline": "NBA All-Star rosters announced",
                    "published": "2024-01-16T18:00:00Z",
                    "type": "Story",
                },
            ]
        })

        result = self.service.ingest_news("basketball", "nba")

        assert isinstance(result, IngestionResult)
        assert result.created == 2
        assert result.updated == 0
        assert result.errors == 0
        assert NewsArticle.objects.count() == 2

    def test_ingest_updates_existing_article(self) -> None:
        """Ingesting the same espn_id twice should update, not create."""
        self.client_mock.get_news.return_value = _make_espn_response({
            "articles": [
                {
                    "dataSourceIdentifier": "art-001",
                    "headline": "Updated headline",
                    "published": "2024-01-15T20:00:00Z",
                    "type": "Story",
                }
            ]
        })

        NewsArticle.objects.create(espn_id="art-001", headline="Old headline")

        result = self.service.ingest_news("basketball", "nba")

        assert result.created == 0
        assert result.updated == 1
        assert NewsArticle.objects.get(espn_id="art-001").headline == "Updated headline"

    def test_ingest_empty_response_returns_zero(self) -> None:
        self.client_mock.get_news.return_value = _make_espn_response({"articles": []})
        result = self.service.ingest_news("basketball", "nba")
        assert result.created == 0
        assert result.updated == 0
        assert result.errors == 0

    def test_ingest_skips_items_without_espn_id(self) -> None:
        self.client_mock.get_news.return_value = _make_espn_response({
            "articles": [{"headline": "No ID article"}]
        })
        result = self.service.ingest_news("basketball", "nba")
        assert result.errors == 1
        assert NewsArticle.objects.count() == 0


# ---------------------------------------------------------------------------
# InjuryIngestionService
# ---------------------------------------------------------------------------


class TestInjuryIngestionService(TestCase):
    """Tests for InjuryIngestionService.ingest_injuries()."""

    def setUp(self) -> None:
        self.client_mock = MagicMock()
        self.service = InjuryIngestionService(client=self.client_mock)
        sport, self.league = _make_league("football", "nfl")
        self.team = Team.objects.create(
            league=self.league,
            espn_id="18",
            abbreviation="KC",
            display_name="Kansas City Chiefs",
        )

    def test_ingest_creates_injury_records(self) -> None:
        self.client_mock.get_league_injuries.return_value = _make_espn_response({
            "items": [
                {
                    "athlete": {"id": "3139477", "displayName": "Patrick Mahomes", "position": {"abbreviation": "QB"}},
                    "status": "Questionable",
                    "description": "Ankle",
                    "type": "Ankle",
                    "team": {"id": "18"},
                },
            ]
        })

        result = self.service.ingest_injuries("football", "nfl")

        assert result.created == 1
        assert result.errors == 0
        injury = Injury.objects.get(league=self.league)
        assert injury.athlete_name == "Patrick Mahomes"
        assert injury.status == "questionable"
        assert injury.team == self.team

    def test_ingest_clears_stale_records(self) -> None:
        """Re-ingesting should wipe old records and insert fresh ones."""
        Injury.objects.create(league=self.league, athlete_name="Old Player", status="out")

        self.client_mock.get_league_injuries.return_value = _make_espn_response({
            "items": [
                {
                    "athlete": {"id": "999", "displayName": "New Player"},
                    "status": "Out",
                    "team": {},
                }
            ]
        })

        self.service.ingest_injuries("football", "nfl")

        assert Injury.objects.filter(league=self.league).count() == 1
        assert Injury.objects.filter(league=self.league).first().athlete_name == "New Player"

    def test_ingest_empty_response(self) -> None:
        self.client_mock.get_league_injuries.return_value = _make_espn_response({"items": []})
        result = self.service.ingest_injuries("football", "nfl")
        assert result.created == 0

    def test_status_normalisation(self) -> None:
        service = InjuryIngestionService.__new__(InjuryIngestionService)
        assert service._normalize_status("Out") == "out"
        assert service._normalize_status("QUESTIONABLE") == "questionable"
        assert service._normalize_status("Injured Reserve") == "ir"
        assert service._normalize_status("Day-to-Day") == "day_to_day"
        assert service._normalize_status("Unknown") == "other"


# ---------------------------------------------------------------------------
# TransactionIngestionService
# ---------------------------------------------------------------------------


class TestTransactionIngestionService(TestCase):
    """Tests for TransactionIngestionService.ingest_transactions()."""

    def setUp(self) -> None:
        self.client_mock = MagicMock()
        self.service = TransactionIngestionService(client=self.client_mock)
        _, self.league = _make_league("basketball", "nba")

    def test_ingest_creates_transactions(self) -> None:
        self.client_mock.get_league_transactions.return_value = _make_espn_response({
            "items": [
                {
                    "id": "txn-101",
                    "description": "Lakers signed X to a 1-year deal",
                    "type": "Signing",
                    "date": "2024-07-15",
                    "athlete": {"id": "555", "displayName": "Player X"},
                    "team": {},
                }
            ]
        })

        result = self.service.ingest_transactions("basketball", "nba")

        assert result.created == 1
        txn = Transaction.objects.get(espn_id="txn-101")
        assert txn.type == "Signing"
        assert txn.date == date(2024, 7, 15)

    def test_ingest_updates_existing_transaction(self) -> None:
        Transaction.objects.create(league=self.league, espn_id="txn-101", description="Old")

        self.client_mock.get_league_transactions.return_value = _make_espn_response({
            "items": [
                {
                    "id": "txn-101",
                    "description": "Updated description",
                    "type": "Trade",
                    "date": "2024-07-20",
                    "athlete": {},
                    "team": {},
                }
            ]
        })

        result = self.service.ingest_transactions("basketball", "nba")

        assert result.updated == 1
        assert Transaction.objects.get(espn_id="txn-101").description == "Updated description"


# ---------------------------------------------------------------------------
# Celery tasks
# ---------------------------------------------------------------------------


class TestNewCeleryTasks(TestCase):
    """Verify new Celery task functions dispatch services correctly."""

    @patch("apps.ingest.services.NewsIngestionService")
    def test_refresh_news_task_calls_service(self, MockService: MagicMock) -> None:
        from apps.ingest.tasks import refresh_news_task

        mock_instance = MockService.return_value
        mock_instance.ingest_news.return_value = IngestionResult(created=5, updated=0, errors=0)

        # bind=True tasks must be tested via .run() to skip the self/broker machinery
        result = refresh_news_task.run("basketball", "nba")

        mock_instance.ingest_news.assert_called_once_with("basketball", "nba", limit=50)
        assert result["created"] == 5

    @patch("apps.ingest.services.InjuryIngestionService")
    def test_refresh_injuries_task_calls_service(self, MockService: MagicMock) -> None:
        from apps.ingest.tasks import refresh_injuries_task

        mock_instance = MockService.return_value
        mock_instance.ingest_injuries.return_value = IngestionResult(created=30, updated=0, errors=0)

        result = refresh_injuries_task.run("football", "nfl")

        mock_instance.ingest_injuries.assert_called_once_with("football", "nfl")
        assert result["created"] == 30

    @patch("apps.ingest.services.TransactionIngestionService")
    def test_refresh_transactions_task_calls_service(self, MockService: MagicMock) -> None:
        from apps.ingest.tasks import refresh_transactions_task

        mock_instance = MockService.return_value
        mock_instance.ingest_transactions.return_value = IngestionResult(created=8, updated=2, errors=0)

        result = refresh_transactions_task.run("basketball", "nba")

        mock_instance.ingest_transactions.assert_called_once_with("basketball", "nba")
        assert result["created"] == 8


# ---------------------------------------------------------------------------
# REST API endpoints
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestNewsArticleAPI:
    """Tests for GET /api/v1/news/"""

    def test_list_news_empty(self) -> None:
        client = APIClient()
        response = client.get("/api/v1/news/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_list_news_filter_by_league(self) -> None:
        sport, league = _make_league("basketball", "nba")
        sport2, league2 = _make_league("football", "nfl")
        NewsArticle.objects.create(espn_id="a1", headline="NBA news", league=league)
        NewsArticle.objects.create(espn_id="a2", headline="NFL news", league=league2)

        client = APIClient()
        response = client.get("/api/v1/news/?league=nba")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["headline"] == "NBA news"


@pytest.mark.django_db
class TestInjuryAPI:
    """Tests for GET /api/v1/injuries/"""

    def test_list_injuries_empty(self) -> None:
        client = APIClient()
        response = client.get("/api/v1/injuries/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_list_injuries_filter_by_status(self) -> None:
        _, league = _make_league("football", "nfl")
        Injury.objects.create(league=league, athlete_name="Player A", status="out")
        Injury.objects.create(league=league, athlete_name="Player B", status="questionable")

        client = APIClient()
        response = client.get("/api/v1/injuries/?status=out")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["athlete_name"] == "Player A"


@pytest.mark.django_db
class TestIngestNewsEndpoint:
    """Tests for POST /api/v1/ingest/news/"""

    def test_invalid_request_returns_400(self) -> None:
        client = APIClient()
        response = client.post("/api/v1/ingest/news/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.ingest.views.NewsIngestionService")
    def test_valid_request_calls_service(self, MockService: MagicMock) -> None:
        mock_instance = MockService.return_value
        mock_instance.ingest_news.return_value = IngestionResult(created=3, updated=0, errors=0)

        client = APIClient()
        response = client.post(
            "/api/v1/ingest/news/",
            {"sport": "basketball", "league": "nba"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] == 3
        mock_instance.ingest_news.assert_called_once_with("basketball", "nba", limit=50)


@pytest.mark.django_db
class TestIngestInjuriesEndpoint:
    """Tests for POST /api/v1/ingest/injuries/"""

    def test_invalid_request_returns_400(self) -> None:
        client = APIClient()
        response = client.post("/api/v1/ingest/injuries/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.ingest.views.InjuryIngestionService")
    def test_valid_request_calls_service(self, MockService: MagicMock) -> None:
        mock_instance = MockService.return_value
        mock_instance.ingest_injuries.return_value = IngestionResult(created=22, updated=0, errors=0)

        client = APIClient()
        response = client.post(
            "/api/v1/ingest/injuries/",
            {"sport": "football", "league": "nfl"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] == 22

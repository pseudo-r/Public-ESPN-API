"""Tests for Django-Q2 task functions."""

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.ingest.tasks import purge_old_results


@pytest.mark.django_db
class TestPurgeOldResults:
    def test_purges_results_older_than_90_days(self):
        from django_q.models import Failure, Success

        now = timezone.now()
        old_date = now - timedelta(days=91)
        recent_date = now - timedelta(days=10)

        # Create old and recent results (id, started, and success flag are required)
        Success.objects.create(id=uuid.uuid4().hex, name="old_task", func="test", started=old_date, stopped=old_date, success=True)
        Success.objects.create(id=uuid.uuid4().hex, name="recent_task", func="test", started=recent_date, stopped=recent_date, success=True)
        Failure.objects.create(id=uuid.uuid4().hex, name="old_failure", func="test", started=old_date, stopped=old_date, success=False)
        Failure.objects.create(id=uuid.uuid4().hex, name="recent_failure", func="test", started=recent_date, stopped=recent_date, success=False)

        result = purge_old_results()

        assert result["purged_success"] == 1
        assert result["purged_failure"] == 1
        assert Success.objects.count() == 1
        assert Failure.objects.count() == 1

    def test_no_old_results_returns_zero(self):
        result = purge_old_results()
        assert result["purged_success"] == 0
        assert result["purged_failure"] == 0

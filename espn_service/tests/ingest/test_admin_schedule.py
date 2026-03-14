"""Tests for Schedule admin 'Run now' action."""

from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django_q.models import Schedule

from apps.ingest.admin import ScheduleRunNowAdmin


@pytest.mark.django_db
class TestScheduleRunNowAction:
    def test_run_now_enqueues_task(self):
        schedule = Schedule.objects.create(
            name="Test schedule",
            func="apps.ingest.tasks.refresh_scoreboard",
            args='["basketball", "nba"]',
            schedule_type=Schedule.CRON,
            cron="0 * * * *",
        )

        admin_instance = ScheduleRunNowAdmin(Schedule, AdminSite())
        factory = RequestFactory()
        request = factory.post("/admin/")
        request.session = "session"
        request._messages = FallbackStorage(request)

        with patch("apps.ingest.admin.async_task") as mock_async:
            admin_instance.run_now(request, Schedule.objects.filter(pk=schedule.pk))
            mock_async.assert_called_once_with(
                "apps.ingest.tasks.refresh_scoreboard",
                "basketball",
                "nba",
            )

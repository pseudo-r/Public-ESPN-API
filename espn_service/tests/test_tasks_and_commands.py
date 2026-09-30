"""Exercise worker retries, fan-out failures, and management entry points."""

from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.ingest import tasks
from apps.ingest.services import IngestionResult

CASES = [
    ("teams", "TeamIngestionService", "ingest_teams"),
    ("scoreboard", "ScoreboardIngestionService", "ingest_scoreboard"),
    ("news", "NewsIngestionService", "ingest_news"),
    ("injuries", "InjuryIngestionService", "ingest_injuries"),
    ("transactions", "TransactionIngestionService", "ingest_transactions"),
]


@pytest.mark.parametrize("name,service,method", CASES)
def test_worker_success_and_retry(name, service, method):
    task = getattr(tasks, f"refresh_{name}_task")
    with patch(f"apps.ingest.services.{service}") as cls:
        function = getattr(cls.return_value, method)
        function.return_value = IngestionResult(created=2, updated=1)
        assert task.run("football", "nfl")["created"] == 2
        function.side_effect = RuntimeError("upstream unavailable")
        with patch.object(task, "retry", side_effect=RuntimeError("retry requested")) as retry:
            with pytest.raises(RuntimeError, match="retry requested"):
                task.run("football", "nfl")
            assert isinstance(retry.call_args.kwargs["exc"], RuntimeError)


@pytest.mark.parametrize(
    "plural,singular",
    [
        ("scoreboards", "scoreboard"),
        ("teams", "teams"),
        ("news", "news"),
        ("injuries", "injuries"),
        ("transactions", "transactions"),
    ],
)
def test_fanout_continues_after_broker_failure(plural, singular):
    with (
        patch.object(tasks, "ALL_LEAGUES_CONFIG", [("football", "nfl"), ("basketball", "nba")]),
        patch.object(getattr(tasks, f"refresh_{singular}_task"), "delay") as delay,
    ):
        delay.side_effect = [RuntimeError("broker down"), None]
        result = getattr(tasks, f"refresh_all_{plural}_task").run()
        assert delay.call_count == 2
        assert result["errors"] == 1


@pytest.mark.parametrize("name,service,method", CASES)
def test_command_invokes_service_and_reports_failures(name, service, method):
    command = f"ingest_{name}"
    args = (
        ["FOOTBALL", "NFL"]
        if name in ("teams", "scoreboard")
        else ["--sport", "FOOTBALL", "--league", "NFL"]
    )
    with patch(f"apps.ingest.management.commands.{command}.{service}") as cls:
        function = getattr(cls.return_value, method)
        function.return_value = IngestionResult(created=2, updated=1)
        out = StringIO()
        call_command(command, *args, stdout=out)
        assert function.call_args.args[:2] == ("football", "nfl")
        assert "2" in out.getvalue()
        function.side_effect = RuntimeError("failed upstream")
        if name in ("teams", "scoreboard"):
            with pytest.raises(CommandError, match="failed upstream"):
                call_command(command, *args, stdout=StringIO())
        else:
            out = StringIO()
            call_command(command, *args, stdout=out)
            assert "FAILED" in out.getvalue()


@pytest.mark.parametrize("name", ["news", "injuries", "transactions"])
def test_bulk_commands_require_paired_filters(name):
    with pytest.raises(CommandError):
        call_command(f"ingest_{name}", "--sport", "football", stdout=StringIO())

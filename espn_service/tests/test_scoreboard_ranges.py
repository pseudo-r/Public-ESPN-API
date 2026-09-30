"""Regression coverage for issue #23."""
from unittest.mock import patch

import pytest

from apps.core.exceptions import ESPNClientError
from apps.ingest.serializers import IngestScoreboardRequestSerializer
from clients.dates import scoreboard_dates
from clients.espn_client import ESPNClient, ESPNResponse


@pytest.mark.parametrize("value", ["20260230", "20260925-20260919", "20260101-20260201", "2026011"])
def test_invalid_dates(value):
    with pytest.raises(ValueError):
        scoreboard_dates(value)
    serializer = IngestScoreboardRequestSerializer(
        data={"sport": "baseball", "league": "mlb", "date": value}
    )
    assert not serializer.is_valid()


def test_leap_day_and_same_day():
    assert scoreboard_dates("20240228-20240301") == ["20240228", "20240229", "20240301"]
    assert scoreboard_dates("20260919-20260919") == ["20260919"]


def test_aggregate_and_metadata():
    responses = [
        ESPNResponse(data={"events": [{"id": "2", "name": "old"}], "week": 1},
                     status_code=200, url="day1"),
        ESPNResponse(data={"events": [{"id": "1"}, {"id": "2", "name": "new"}], "week": 2},
                     status_code=200, url="day2"),
    ]
    with ESPNClient() as client, patch.object(client, "get", side_effect=responses) as get:
        result = client.get_scoreboard("baseball", "mlb", "20260919-20260920", limit=1000)
    assert [event["id"] for event in result.data["events"]] == ["1", "2"]
    assert result.data["events"][1]["name"] == "new"
    assert "week" not in result.data
    assert [item["metadata"]["week"] for item in result.data["dailyMetadata"]] == [1, 2]
    assert [call.kwargs["params"]["dates"] for call in get.call_args_list] == ["20260919", "20260920"]
    assert all(call.kwargs["params"]["limit"] == 1000 for call in get.call_args_list)
    serializer = IngestScoreboardRequestSerializer(
        data={"sport": "baseball", "league": "mlb", "date": "20260919-20260920"}
    )
    assert serializer.is_valid(), serializer.errors


@pytest.mark.parametrize("failure", [
    ESPNClientError("failed day"),
    ESPNResponse(data={}, status_code=200, url="bad"),
    ESPNResponse(data={"events": [{}]}, status_code=200, url="bad"),
])
def test_no_partial_results(failure):
    first = ESPNResponse(data={"events": [{"id": "1"}]}, status_code=200, url="ok")
    with (
        ESPNClient() as client,
        patch.object(client, "get", side_effect=[first, failure]),
        pytest.raises(ESPNClientError),
    ):
        client.get_scoreboard("baseball", "mlb", "20260919-20260920")

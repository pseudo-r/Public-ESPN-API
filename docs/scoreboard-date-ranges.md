# Scoreboard date-range workaround

The Python client works around the ESPN regression reported in [#23](https://github.com/pseudo-r/Public-ESPN-API/issues/23):

```python
from clients.espn_client import ESPNClient

with ESPNClient() as client:
    result = client.get_scoreboard("baseball", "mlb", "20260919-20260925", limit=1000)
    events = result.data["events"]
```

Ranges are inclusive and limited to 31 days per call. Each date is requested separately. Event IDs are deduplicated (the later daily response wins) and events sorted by date and ID. The limit applies to each daily request; upstream truncation can still limit completeness. Any failed or malformed daily response fails the whole call without returning partial results.

The synthesized response contains `events`, `dateRange`, and `dailyMetadata`. Season/week and other upstream metadata remain attached to their individual dates. Its URL describes the logical query, not a successful upstream range request. Single-day queries retain their upstream response format.

The scoreboard ingestion API's `date` field and `ingest_scoreboard --date` command also accept this format. Invalid calendar dates and reversed or oversized ranges are rejected. Direct ESPN range requests may still fail: this fixes the repository's client, not ESPN's server.

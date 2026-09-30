"""Serializers for ingest API endpoints."""

from rest_framework import serializers

from clients.dates import scoreboard_dates


class IngestScoreboardRequestSerializer(serializers.Serializer):
    """Request serializer for scoreboard ingestion."""

    sport = serializers.CharField(max_length=50, help_text="Sport slug (e.g., 'basketball')")
    league = serializers.CharField(max_length=50, help_text="League slug (e.g., 'nba')")
    date = serializers.CharField(
        max_length=17,
        required=False,
        allow_blank=True,
        help_text="YYYYMMDD or inclusive YYYYMMDD-YYYYMMDD, up to 31 days (optional)",
    )

    def validate_sport(self, value: str) -> str:
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        return value.lower().strip()

    def validate_date(self, value: str) -> str | None:
        if not value:
            return None
        value = value.strip()
        try:
            scoreboard_dates(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value


class IngestTeamsRequestSerializer(serializers.Serializer):
    """Request serializer for teams ingestion."""

    sport = serializers.CharField(max_length=50, help_text="Sport slug (e.g., 'basketball')")
    league = serializers.CharField(max_length=50, help_text="League slug (e.g., 'nba')")

    def validate_sport(self, value: str) -> str:
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        return value.lower().strip()


class IngestNewsRequestSerializer(serializers.Serializer):
    """Request serializer for news ingestion."""

    sport = serializers.CharField(max_length=50, help_text="Sport slug (e.g., 'basketball')")
    league = serializers.CharField(max_length=50, help_text="League slug (e.g., 'nba')")
    limit = serializers.IntegerField(
        default=50, min_value=1, max_value=200, help_text="Number of articles to fetch (default 50)"
    )

    def validate_sport(self, value: str) -> str:
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        return value.lower().strip()


class IngestInjuriesRequestSerializer(serializers.Serializer):
    """Request serializer for injury ingestion."""

    sport = serializers.CharField(max_length=50, help_text="Sport slug (e.g., 'football')")
    league = serializers.CharField(max_length=50, help_text="League slug (e.g., 'nfl')")

    def validate_sport(self, value: str) -> str:
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        return value.lower().strip()


class IngestTransactionsRequestSerializer(serializers.Serializer):
    """Request serializer for transaction ingestion."""

    sport = serializers.CharField(max_length=50, help_text="Sport slug (e.g., 'basketball')")
    league = serializers.CharField(max_length=50, help_text="League slug (e.g., 'nba')")

    def validate_sport(self, value: str) -> str:
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        return value.lower().strip()


class IngestionResultSerializer(serializers.Serializer):
    """Serializer for ingestion results."""

    created = serializers.IntegerField(help_text="Number of new records created")
    updated = serializers.IntegerField(help_text="Number of existing records updated")
    errors = serializers.IntegerField(help_text="Number of records that failed to process")
    total_processed = serializers.IntegerField(help_text="Total records processed (created + updated)")
    details = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="Optional details about the ingestion",
    )

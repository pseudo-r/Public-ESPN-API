"""Serializers for ingestion API endpoints."""

from rest_framework import serializers


class IngestScoreboardRequestSerializer(serializers.Serializer):
    """Request serializer for scoreboard ingestion."""

    sport = serializers.CharField(
        max_length=50,
        help_text="Sport slug (e.g., 'basketball', 'football')",
    )
    league = serializers.CharField(
        max_length=50,
        help_text="League slug (e.g., 'nba', 'nfl')",
    )
    date = serializers.CharField(
        max_length=8,
        required=False,
        allow_blank=True,
        help_text="Date in YYYYMMDD format (optional, defaults to today)",
    )

    def validate_sport(self, value: str) -> str:
        """Validate and normalize sport slug."""
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        """Validate and normalize league slug."""
        return value.lower().strip()

    def validate_date(self, value: str) -> str | None:
        """Validate date format."""
        if not value:
            return None

        value = value.strip()
        if len(value) != 8 or not value.isdigit():
            raise serializers.ValidationError(
                "Date must be in YYYYMMDD format (e.g., '20241215')"
            )
        return value


class IngestTeamsRequestSerializer(serializers.Serializer):
    """Request serializer for teams ingestion."""

    sport = serializers.CharField(
        max_length=50,
        help_text="Sport slug (e.g., 'basketball', 'football')",
    )
    league = serializers.CharField(
        max_length=50,
        help_text="League slug (e.g., 'nba', 'nfl')",
    )

    def validate_sport(self, value: str) -> str:
        """Validate and normalize sport slug."""
        return value.lower().strip()

    def validate_league(self, value: str) -> str:
        """Validate and normalize league slug."""
        return value.lower().strip()


class IngestionResultSerializer(serializers.Serializer):
    """Serializer for ingestion results."""

    created = serializers.IntegerField(
        help_text="Number of new records created",
    )
    updated = serializers.IntegerField(
        help_text="Number of existing records updated",
    )
    errors = serializers.IntegerField(
        help_text="Number of records that failed to process",
    )
    total_processed = serializers.IntegerField(
        help_text="Total records processed (created + updated)",
    )
    details = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="Optional details about the ingestion",
    )

"""Views for ingestion API endpoints."""

import structlog
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ingest.serializers import (
    IngestionResultSerializer,
    IngestScoreboardRequestSerializer,
    IngestTeamsRequestSerializer,
)
from apps.ingest.services import ScoreboardIngestionService, TeamIngestionService

logger = structlog.get_logger(__name__)


class IngestScoreboardView(APIView):
    """Endpoint for ingesting scoreboard data from ESPN."""

    @extend_schema(
        tags=["Ingest"],
        summary="Ingest scoreboard data",
        description=(
            "Fetch scoreboard data from ESPN for a specific sport, league, and date, "
            "then upsert the events and competitors into the database."
        ),
        request=IngestScoreboardRequestSerializer,
        responses={
            200: IngestionResultSerializer,
            400: {"description": "Invalid request data"},
            502: {"description": "ESPN API error"},
        },
    )
    def post(self, request: Request) -> Response:
        """Ingest scoreboard data from ESPN."""
        serializer = IngestScoreboardRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sport = serializer.validated_data["sport"]
        league = serializer.validated_data["league"]
        date = serializer.validated_data.get("date")

        logger.info(
            "scoreboard_ingestion_requested",
            sport=sport,
            league=league,
            date=date,
        )

        service = ScoreboardIngestionService()
        result = service.ingest_scoreboard(sport, league, date)

        return Response(
            IngestionResultSerializer(result.to_dict()).data,
            status=status.HTTP_200_OK,
        )


class IngestTeamsView(APIView):
    """Endpoint for ingesting team data from ESPN."""

    @extend_schema(
        tags=["Ingest"],
        summary="Ingest teams data",
        description=(
            "Fetch all teams from ESPN for a specific sport and league, "
            "then upsert them into the database."
        ),
        request=IngestTeamsRequestSerializer,
        responses={
            200: IngestionResultSerializer,
            400: {"description": "Invalid request data"},
            502: {"description": "ESPN API error"},
        },
    )
    def post(self, request: Request) -> Response:
        """Ingest teams data from ESPN."""
        serializer = IngestTeamsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sport = serializer.validated_data["sport"]
        league = serializer.validated_data["league"]

        logger.info(
            "teams_ingestion_requested",
            sport=sport,
            league=league,
        )

        service = TeamIngestionService()
        result = service.ingest_teams(sport, league)

        return Response(
            IngestionResultSerializer(result.to_dict()).data,
            status=status.HTTP_200_OK,
        )

"""Views for ESPN data API endpoints."""

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.espn.filters import EventFilter, TeamFilter
from apps.espn.models import Event, Team
from apps.espn.serializers import (
    EventListSerializer,
    EventSerializer,
    TeamListSerializer,
    TeamSerializer,
)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Team data.

    Provides list and retrieve actions for teams.
    """

    filterset_class = TeamFilter
    search_fields = ["display_name", "abbreviation", "location", "name"]
    ordering_fields = ["display_name", "abbreviation", "created_at"]
    ordering = ["display_name"]

    def get_queryset(self) -> QuerySet[Team]:
        """Get the team queryset with optimized prefetching."""
        return Team.objects.select_related("league", "league__sport").filter(is_active=True)

    def get_serializer_class(self) -> type:
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return TeamListSerializer
        return TeamSerializer

    @extend_schema(
        tags=["Teams"],
        summary="List teams",
        description="Get a paginated list of teams with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="sport",
                description="Filter by sport slug (e.g., 'basketball')",
                type=str,
            ),
            OpenApiParameter(
                name="league",
                description="Filter by league slug (e.g., 'nba')",
                type=str,
            ),
            OpenApiParameter(
                name="search",
                description="Search in display_name, abbreviation, or location",
                type=str,
            ),
        ],
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List teams with filtering and pagination."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Teams"],
        summary="Get team details",
        description="Retrieve detailed information about a specific team.",
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get team details."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Teams"],
        summary="Get team by ESPN ID",
        description="Retrieve a team by its ESPN ID.",
        parameters=[
            OpenApiParameter(
                name="espn_id",
                description="ESPN team ID",
                type=str,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="espn/(?P<espn_id>[^/.]+)")
    def by_espn_id(self, request: Request, espn_id: str) -> Response:
        """Get team by ESPN ID."""
        queryset = self.get_queryset()
        team = queryset.filter(espn_id=espn_id).first()
        if not team:
            return Response({"error": "Team not found"}, status=404)
        serializer = TeamSerializer(team)
        return Response(serializer.data)


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Event/Game data.

    Provides list and retrieve actions for events.
    """

    filterset_class = EventFilter
    search_fields = ["name", "short_name"]
    ordering_fields = ["date", "created_at"]
    ordering = ["-date"]

    def get_queryset(self) -> QuerySet[Event]:
        """Get the event queryset with optimized prefetching."""
        return Event.objects.select_related(
            "league",
            "league__sport",
            "venue",
        ).prefetch_related(
            "competitors",
            "competitors__team",
        )

    def get_serializer_class(self) -> type:
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return EventListSerializer
        return EventSerializer

    @extend_schema(
        tags=["Events"],
        summary="List events",
        description="Get a paginated list of events/games with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="sport",
                description="Filter by sport slug (e.g., 'basketball')",
                type=str,
            ),
            OpenApiParameter(
                name="league",
                description="Filter by league slug (e.g., 'nba')",
                type=str,
            ),
            OpenApiParameter(
                name="date",
                description="Filter by exact date (YYYY-MM-DD)",
                type=str,
            ),
            OpenApiParameter(
                name="date_from",
                description="Filter by date >= (YYYY-MM-DD)",
                type=str,
            ),
            OpenApiParameter(
                name="date_to",
                description="Filter by date <= (YYYY-MM-DD)",
                type=str,
            ),
            OpenApiParameter(
                name="status",
                description="Filter by status (scheduled, in_progress, final)",
                type=str,
            ),
            OpenApiParameter(
                name="team",
                description="Filter by team ESPN ID or abbreviation",
                type=str,
            ),
        ],
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List events with filtering and pagination."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Events"],
        summary="Get event details",
        description="Retrieve detailed information about a specific event/game.",
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get event details."""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Events"],
        summary="Get event by ESPN ID",
        description="Retrieve an event by its ESPN ID.",
        parameters=[
            OpenApiParameter(
                name="espn_id",
                description="ESPN event ID",
                type=str,
                location=OpenApiParameter.PATH,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="espn/(?P<espn_id>[^/.]+)")
    def by_espn_id(self, request: Request, espn_id: str) -> Response:
        """Get event by ESPN ID."""
        queryset = self.get_queryset()
        event = queryset.filter(espn_id=espn_id).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        serializer = EventSerializer(event)
        return Response(serializer.data)

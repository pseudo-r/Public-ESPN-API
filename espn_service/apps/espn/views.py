"""Views for ESPN data API endpoints."""

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.espn.filters import EventFilter, SeasonFilter, TeamFilter
from apps.espn.models import Event, League, Season, Sport, Team
from apps.espn.serializers import (
    EventListSerializer,
    EventSerializer,
    LeagueSerializer,
    SeasonSerializer,
    SportSerializer,
    TeamListSerializer,
    TeamSerializer,
)


class SportViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Sport discovery.

    Provides list and retrieve actions for sports.
    """

    serializer_class = SportSerializer
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Sport]:
        """Get all sports."""
        return Sport.objects.prefetch_related("leagues").order_by("name")

    @extend_schema(
        tags=["Discovery"],
        summary="List sports",
        description="Get all sports that have ingested data in the database.",
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all sports."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Discovery"],
        summary="Get sport details",
        description="Retrieve a sport by slug (e.g., 'basketball', 'football').",
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get sport details."""
        return super().retrieve(request, *args, **kwargs)


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for League discovery.

    Provides list and retrieve actions for leagues.
    """

    serializer_class = LeagueSerializer

    def get_queryset(self) -> QuerySet[League]:
        """Get league queryset with optional sport filter."""
        qs = League.objects.select_related("sport").order_by("sport__name", "name")
        sport = self.request.query_params.get("sport")
        if sport:
            qs = qs.filter(sport__slug__iexact=sport)
        return qs

    @extend_schema(
        tags=["Discovery"],
        summary="List leagues",
        description="Get all leagues that have ingested data in the database.",
        parameters=[
            OpenApiParameter(
                name="sport",
                description="Filter by sport slug (e.g., 'basketball')",
                type=str,
            ),
        ],
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all leagues."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Discovery"],
        summary="Get league details",
        description="Retrieve a specific league by ID.",
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get league details."""
        return super().retrieve(request, *args, **kwargs)


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
    def by_espn_id(self, request: Request, espn_id: str) -> Response:  # noqa: ARG002

        queryset = self.get_queryset()
        team = queryset.filter(espn_id=espn_id).first()
        if not team:
            return Response({"error": "Team not found"}, status=404)
        serializer = TeamSerializer(team)
        return Response(serializer.data)


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Season data."""

    serializer_class = SeasonSerializer
    filterset_class = SeasonFilter
    ordering_fields = ["year", "season_type"]
    ordering = ["-year", "season_type"]

    def get_queryset(self) -> QuerySet[Season]:
        return Season.objects.select_related("league", "league__sport")

    @extend_schema(
        tags=["Seasons"],
        summary="List seasons",
        description="Get all seasons with optional filtering by league, year, type.",
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Seasons"],
        summary="Get season details",
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        return super().retrieve(request, *args, **kwargs)


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
    def by_espn_id(self, request: Request, espn_id: str) -> Response:  # noqa: ARG002

        queryset = self.get_queryset()
        event = queryset.filter(espn_id=espn_id).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        serializer = EventSerializer(event)
        return Response(serializer.data)

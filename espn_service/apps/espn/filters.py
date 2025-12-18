"""Filters for ESPN data API endpoints."""

import django_filters
from django.db.models import Q, QuerySet

from apps.espn.models import Event, Team


class TeamFilter(django_filters.FilterSet):
    """Filter for Team queryset."""

    sport = django_filters.CharFilter(
        field_name="league__sport__slug",
        lookup_expr="iexact",
        help_text="Filter by sport slug (e.g., 'basketball')",
    )
    league = django_filters.CharFilter(
        field_name="league__slug",
        lookup_expr="iexact",
        help_text="Filter by league slug (e.g., 'nba')",
    )
    is_active = django_filters.BooleanFilter(
        help_text="Filter by active status",
    )
    abbreviation = django_filters.CharFilter(
        lookup_expr="iexact",
        help_text="Filter by team abbreviation",
    )
    search = django_filters.CharFilter(
        method="search_filter",
        help_text="Search in display_name, abbreviation, or location",
    )

    class Meta:
        model = Team
        fields = ["sport", "league", "is_active", "abbreviation"]

    def search_filter(
        self, queryset: QuerySet, name: str, value: str
    ) -> QuerySet:
        """Custom search filter across multiple fields."""
        if not value:
            return queryset
        return queryset.filter(
            Q(display_name__icontains=value)
            | Q(abbreviation__icontains=value)
            | Q(location__icontains=value)
            | Q(name__icontains=value)
        )


class EventFilter(django_filters.FilterSet):
    """Filter for Event queryset."""

    sport = django_filters.CharFilter(
        field_name="league__sport__slug",
        lookup_expr="iexact",
        help_text="Filter by sport slug (e.g., 'basketball')",
    )
    league = django_filters.CharFilter(
        field_name="league__slug",
        lookup_expr="iexact",
        help_text="Filter by league slug (e.g., 'nba')",
    )
    date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date",
        help_text="Filter by exact date (YYYY-MM-DD)",
    )
    date_from = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date__gte",
        help_text="Filter by date >= (YYYY-MM-DD)",
    )
    date_to = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date__lte",
        help_text="Filter by date <= (YYYY-MM-DD)",
    )
    status = django_filters.ChoiceFilter(
        choices=Event.STATUS_CHOICES,
        help_text="Filter by event status",
    )
    season_year = django_filters.NumberFilter(
        help_text="Filter by season year",
    )
    season_type = django_filters.NumberFilter(
        help_text="Filter by season type (1=preseason, 2=regular, 3=postseason)",
    )
    team = django_filters.CharFilter(
        method="team_filter",
        help_text="Filter by team ESPN ID or abbreviation",
    )

    class Meta:
        model = Event
        fields = [
            "sport",
            "league",
            "date",
            "date_from",
            "date_to",
            "status",
            "season_year",
            "season_type",
        ]

    def team_filter(
        self, queryset: QuerySet, name: str, value: str
    ) -> QuerySet:
        """Filter events by team (ESPN ID or abbreviation)."""
        if not value:
            return queryset
        return queryset.filter(
            Q(competitors__team__espn_id=value)
            | Q(competitors__team__abbreviation__iexact=value)
        ).distinct()

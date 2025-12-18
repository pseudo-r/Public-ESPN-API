"""Django admin configuration for ESPN models."""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from apps.espn.models import Athlete, Competitor, Event, League, Sport, Team, Venue


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    """Admin for Sport model."""

    list_display = ["name", "slug", "league_count", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created_at", "updated_at"]

    def league_count(self, obj: Sport) -> int:
        return obj.leagues.count()

    league_count.short_description = "Leagues"  # type: ignore[attr-defined]


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin for League model."""

    list_display = ["name", "abbreviation", "sport", "team_count", "created_at"]
    list_filter = ["sport"]
    search_fields = ["name", "slug", "abbreviation"]
    readonly_fields = ["created_at", "updated_at"]

    def team_count(self, obj: League) -> int:
        return obj.teams.count()

    team_count.short_description = "Teams"  # type: ignore[attr-defined]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin for Team model."""

    list_display = [
        "display_name",
        "abbreviation",
        "league",
        "espn_id",
        "is_active",
        "color_preview",
    ]
    list_filter = ["league", "is_active", "is_all_star"]
    search_fields = ["display_name", "abbreviation", "espn_id", "slug"]
    readonly_fields = ["created_at", "updated_at", "logo_preview"]

    def color_preview(self, obj: Team) -> str:
        if obj.color:
            return format_html(
                '<span style="background-color: #{0}; padding: 2px 10px; '
                'border-radius: 3px; color: white;">{0}</span>',
                obj.color,
            )
        return "-"

    color_preview.short_description = "Color"  # type: ignore[attr-defined]

    def logo_preview(self, obj: Team) -> str:
        logo_url = obj.primary_logo
        if logo_url:
            return format_html(
                '<img src="{0}" style="max-height: 100px; max-width: 100px;" />',
                logo_url,
            )
        return "-"

    logo_preview.short_description = "Logo"  # type: ignore[attr-defined]


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Admin for Venue model."""

    list_display = ["name", "city", "state", "is_indoor", "capacity", "espn_id"]
    list_filter = ["is_indoor", "state", "country"]
    search_fields = ["name", "city", "espn_id"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin for Event model."""

    list_display = [
        "short_name",
        "league",
        "date",
        "status",
        "venue",
        "espn_id",
    ]
    list_filter = ["league", "status", "season_year", "season_type"]
    search_fields = ["name", "short_name", "espn_id"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "date"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("league", "venue")


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    """Admin for Competitor model."""

    list_display = [
        "team",
        "event",
        "home_away",
        "score",
        "winner",
    ]
    list_filter = ["home_away", "winner", "event__league"]
    search_fields = ["team__display_name", "event__name"]
    readonly_fields = ["created_at", "updated_at"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("team", "event")


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    """Admin for Athlete model."""

    list_display = [
        "display_name",
        "team",
        "position",
        "jersey",
        "is_active",
        "espn_id",
    ]
    list_filter = ["is_active", "team__league", "position"]
    search_fields = ["full_name", "display_name", "espn_id"]
    readonly_fields = ["created_at", "updated_at", "headshot_preview"]

    def headshot_preview(self, obj: Athlete) -> str:
        if obj.headshot:
            return format_html(
                '<img src="{0}" style="max-height: 100px; max-width: 100px;" />',
                obj.headshot,
            )
        return "-"

    headshot_preview.short_description = "Headshot"  # type: ignore[attr-defined]

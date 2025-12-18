"""Serializers for ESPN data models."""

from rest_framework import serializers

from apps.espn.models import Athlete, Competitor, Event, League, Sport, Team, Venue


class SportSerializer(serializers.ModelSerializer):
    """Serializer for Sport model."""

    class Meta:
        model = Sport
        fields = ["id", "slug", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for League model."""

    sport = SportSerializer(read_only=True)
    sport_slug = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = League
        fields = [
            "id",
            "slug",
            "name",
            "abbreviation",
            "sport",
            "sport_slug",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LeagueMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for League (used in nested contexts)."""

    sport_slug = serializers.CharField(source="sport.slug", read_only=True)

    class Meta:
        model = League
        fields = ["id", "slug", "name", "abbreviation", "sport_slug"]


class VenueSerializer(serializers.ModelSerializer):
    """Serializer for Venue model."""

    class Meta:
        model = Venue
        fields = [
            "id",
            "espn_id",
            "name",
            "city",
            "state",
            "country",
            "is_indoor",
            "capacity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model."""

    league = LeagueMinimalSerializer(read_only=True)
    primary_logo = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "espn_id",
            "uid",
            "slug",
            "abbreviation",
            "display_name",
            "short_display_name",
            "name",
            "nickname",
            "location",
            "color",
            "alternate_color",
            "is_active",
            "is_all_star",
            "logos",
            "primary_logo",
            "league",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Team lists."""

    league_slug = serializers.CharField(source="league.slug", read_only=True)
    sport_slug = serializers.CharField(source="league.sport.slug", read_only=True)
    primary_logo = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "espn_id",
            "abbreviation",
            "display_name",
            "short_display_name",
            "location",
            "color",
            "primary_logo",
            "league_slug",
            "sport_slug",
            "is_active",
        ]


class TeamMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Team (used in competitor context)."""

    primary_logo = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "espn_id",
            "abbreviation",
            "display_name",
            "short_display_name",
            "location",
            "color",
            "primary_logo",
        ]


class CompetitorSerializer(serializers.ModelSerializer):
    """Serializer for Competitor model."""

    team = TeamMinimalSerializer(read_only=True)
    score_int = serializers.IntegerField(read_only=True)

    class Meta:
        model = Competitor
        fields = [
            "id",
            "team",
            "home_away",
            "score",
            "score_int",
            "winner",
            "line_scores",
            "records",
            "statistics",
            "leaders",
            "order",
        ]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""

    league = LeagueMinimalSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    competitors = CompetitorSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "espn_id",
            "uid",
            "date",
            "name",
            "short_name",
            "season_year",
            "season_type",
            "season_slug",
            "week",
            "status",
            "status_detail",
            "clock",
            "period",
            "attendance",
            "broadcasts",
            "links",
            "league",
            "venue",
            "competitors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Event lists."""

    league_slug = serializers.CharField(source="league.slug", read_only=True)
    sport_slug = serializers.CharField(source="league.sport.slug", read_only=True)
    venue_name = serializers.CharField(source="venue.name", read_only=True, allow_null=True)
    competitors = CompetitorSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "espn_id",
            "date",
            "name",
            "short_name",
            "status",
            "status_detail",
            "league_slug",
            "sport_slug",
            "venue_name",
            "competitors",
        ]


class AthleteSerializer(serializers.ModelSerializer):
    """Serializer for Athlete model."""

    team = TeamMinimalSerializer(read_only=True)

    class Meta:
        model = Athlete
        fields = [
            "id",
            "espn_id",
            "uid",
            "first_name",
            "last_name",
            "full_name",
            "display_name",
            "short_name",
            "position",
            "position_abbreviation",
            "jersey",
            "is_active",
            "height",
            "weight",
            "age",
            "birth_date",
            "birth_place",
            "headshot",
            "team",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

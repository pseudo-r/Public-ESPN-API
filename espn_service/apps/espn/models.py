"""Database models for ESPN sports data."""

from django.db import models


class TimestampMixin(models.Model):
    """Mixin providing created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Sport(TimestampMixin):
    """Sport entity (e.g., basketball, football)."""

    slug = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class League(TimestampMixin):
    """League entity (e.g., NBA, NFL)."""

    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name="leagues",
    )
    slug = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [["sport", "slug"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.sport.name})"


class Venue(TimestampMixin):
    """Venue/stadium entity."""

    espn_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default="USA")
    is_indoor = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    # Raw data for extensibility
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        location = ", ".join(filter(None, [self.city, self.state]))
        return f"{self.name} ({location})" if location else self.name


class Team(TimestampMixin):
    """Team entity."""

    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    espn_id = models.CharField(max_length=50, db_index=True)
    uid = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=100, blank=True)
    abbreviation = models.CharField(max_length=10)
    display_name = models.CharField(max_length=100)
    short_display_name = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=50, blank=True)  # Team name only (e.g., "Lakers")
    nickname = models.CharField(max_length=50, blank=True)  # City/location
    location = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=10, blank=True)
    alternate_color = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    is_all_star = models.BooleanField(default=False)

    # Store logo URLs and other semi-structured data
    logos = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=list, blank=True)

    # Raw data for extensibility
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["display_name"]
        unique_together = [["league", "espn_id"]]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.league.slug.upper()})"

    @property
    def primary_logo(self) -> str | None:
        """Get the primary logo URL."""
        if not self.logos:
            return None
        # Look for default logo first
        for logo in self.logos:
            if isinstance(logo, dict) and "default" in logo.get("rel", []):
                return logo.get("href")
        # Fallback to first logo
        if self.logos and isinstance(self.logos[0], dict):
            return self.logos[0].get("href")
        return None


class Event(TimestampMixin):
    """Event/game entity."""

    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="events",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    espn_id = models.CharField(max_length=50, db_index=True)
    uid = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)

    # Season information
    season_year = models.PositiveIntegerField()
    season_type = models.PositiveSmallIntegerField(default=2)  # 1=preseason, 2=regular, 3=postseason
    season_slug = models.CharField(max_length=50, blank=True)
    week = models.PositiveSmallIntegerField(null=True, blank=True)

    # Status
    STATUS_SCHEDULED = "scheduled"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_FINAL = "final"
    STATUS_POSTPONED = "postponed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_FINAL, "Final"),
        (STATUS_POSTPONED, "Postponed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
    )
    status_detail = models.CharField(max_length=100, blank=True)
    clock = models.CharField(max_length=20, blank=True)
    period = models.PositiveSmallIntegerField(null=True, blank=True)

    # Attendance
    attendance = models.PositiveIntegerField(null=True, blank=True)

    # Broadcasts
    broadcasts = models.JSONField(default=list, blank=True)

    # Links
    links = models.JSONField(default=list, blank=True)

    # Raw data for extensibility
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = [["league", "espn_id"]]

    def __str__(self) -> str:
        return f"{self.short_name or self.name} ({self.date.strftime('%Y-%m-%d')})"


class Competitor(TimestampMixin):
    """Competitor in an event (links team to event with game-specific data)."""

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="competitors",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="competitions",
    )

    # Home/away designation
    HOME = "home"
    AWAY = "away"
    HOME_AWAY_CHOICES = [
        (HOME, "Home"),
        (AWAY, "Away"),
    ]
    home_away = models.CharField(
        max_length=4,
        choices=HOME_AWAY_CHOICES,
    )

    # Score and result
    score = models.CharField(max_length=10, blank=True)
    winner = models.BooleanField(null=True, blank=True)

    # Line scores (quarter/period scores)
    line_scores = models.JSONField(default=list, blank=True)

    # Records (overall, home, away)
    records = models.JSONField(default=list, blank=True)

    # Statistics
    statistics = models.JSONField(default=list, blank=True)

    # Leaders (points, rebounds, assists leaders)
    leaders = models.JSONField(default=list, blank=True)

    # Order (usually 0 for away, 1 for home)
    order = models.PositiveSmallIntegerField(default=0)

    # Raw data for extensibility
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["order"]
        unique_together = [["event", "team"]]

    def __str__(self) -> str:
        return f"{self.team.abbreviation} ({self.home_away}) - {self.event.short_name}"

    @property
    def score_int(self) -> int | None:
        """Get score as integer."""
        try:
            return int(self.score) if self.score else None
        except ValueError:
            return None


class Athlete(TimestampMixin):
    """Athlete entity (optional - for detailed stats)."""

    espn_id = models.CharField(max_length=50, unique=True, db_index=True)
    uid = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True)

    # Current team (nullable - athletes can be free agents)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="athletes",
    )

    # Position
    position = models.CharField(max_length=50, blank=True)
    position_abbreviation = models.CharField(max_length=10, blank=True)

    # Jersey
    jersey = models.CharField(max_length=10, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Physical attributes
    height = models.CharField(max_length=20, blank=True)  # e.g., "6'8"
    weight = models.PositiveIntegerField(null=True, blank=True)  # in pounds
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=100, blank=True)

    # Media
    headshot = models.URLField(max_length=500, blank=True)

    # Links
    links = models.JSONField(default=list, blank=True)

    # Raw data for extensibility
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        team_abbr = self.team.abbreviation if self.team else "FA"
        return f"{self.display_name} ({team_abbr})"


# ---------------------------------------------------------------------------
# New models — added in audit expansion
# ---------------------------------------------------------------------------


class NewsArticle(TimestampMixin):
    """News article from ESPN news or Now API."""

    espn_id = models.CharField(max_length=100, unique=True, db_index=True)
    headline = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    story = models.TextField(blank=True)
    published = models.DateTimeField(null=True, blank=True, db_index=True)
    last_modified = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=50, blank=True)

    # Optional league association (nullable — some articles span multiple leagues)
    league = models.ForeignKey(
        League,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="news_articles",
    )

    categories = models.JSONField(default=list, blank=True)
    images = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=dict, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-published"]
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def __str__(self) -> str:
        return self.headline[:80]

    @property
    def thumbnail(self) -> str | None:
        """Return thumbnail URL from first image entry."""
        for img in self.images:
            if isinstance(img, dict):
                return img.get("url") or img.get("href")
        return None


class Injury(TimestampMixin):
    """Player injury record from the league injuries endpoint."""

    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="injuries")
    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="injuries"
    )
    espn_id = models.CharField(max_length=100, blank=True, db_index=True)
    athlete_espn_id = models.CharField(max_length=50, blank=True, db_index=True)
    athlete_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, blank=True)

    STATUS_OUT = "out"
    STATUS_QUESTIONABLE = "questionable"
    STATUS_DOUBTFUL = "doubtful"
    STATUS_IR = "ir"
    STATUS_DAY_TO_DAY = "day_to_day"
    STATUS_OTHER = "other"
    STATUS_CHOICES = [
        ("out", "Out"),
        ("questionable", "Questionable"),
        ("doubtful", "Doubtful"),
        ("ir", "IR"),
        ("day_to_day", "Day-to-Day"),
        ("other", "Other"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="other", db_index=True)
    status_display = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=500, blank=True)
    injury_type = models.CharField(max_length=100, blank=True)
    injury_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Injury"
        verbose_name_plural = "Injuries"

    def __str__(self) -> str:
        return f"{self.athlete_name} ({self.status_display or self.status})"


class Transaction(TimestampMixin):
    """Transaction record (signing, trade, waiver, release, etc.)."""

    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="transactions")
    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions"
    )
    espn_id = models.CharField(max_length=100, blank=True, db_index=True)
    identity_key = models.CharField(max_length=64, editable=False, default="")
    date = models.DateField(null=True, blank=True, db_index=True)
    description = models.TextField()
    type = models.CharField(max_length=100, blank=True)
    athlete_name = models.CharField(max_length=100, blank=True)
    athlete_espn_id = models.CharField(max_length=50, blank=True, db_index=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-date", "-updated_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        constraints = [
            models.UniqueConstraint(fields=["league", "identity_key"], name="unique_transaction_identity"),
        ]

    def save(self, *args, **kwargs):
        from .identity import transaction_identity

        team_id = (self.raw_data.get("team") or {}).get("id")
        if not team_id and self.team_id:
            team_id = self.team.espn_id
        self.identity_key = transaction_identity(
            self.espn_id, self.date, self.description, team_id, self.athlete_espn_id,
        )
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"identity_key"}
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.description[:80]


class AthleteSeasonStats(TimestampMixin):
    """Athlete season statistics from common/v3 stats endpoint."""

    athlete = models.ForeignKey(
        Athlete, on_delete=models.CASCADE, related_name="season_stats", null=True, blank=True
    )
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="athlete_season_stats"
    )
    athlete_espn_id = models.CharField(max_length=50, db_index=True)
    athlete_name = models.CharField(max_length=100, blank=True)
    season_year = models.PositiveIntegerField(db_index=True)
    season_type = models.PositiveSmallIntegerField(default=2)  # 2=regular, 3=postseason
    # Flexible stats JSON — structure varies by sport
    stats = models.JSONField(default=dict, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-season_year"]
        unique_together = [["league", "athlete_espn_id", "season_year", "season_type"]]
        verbose_name = "Athlete Season Stats"
        verbose_name_plural = "Athlete Season Stats"

    def __str__(self) -> str:
        return f"{self.athlete_name} — {self.league.slug.upper()} {self.season_year}"

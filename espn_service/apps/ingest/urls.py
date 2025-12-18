"""URL configuration for ingest app."""

from django.urls import path

from apps.ingest.views import IngestScoreboardView, IngestTeamsView

app_name = "ingest"

urlpatterns = [
    path("scoreboard/", IngestScoreboardView.as_view(), name="ingest-scoreboard"),
    path("teams/", IngestTeamsView.as_view(), name="ingest-teams"),
]

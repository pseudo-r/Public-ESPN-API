"""URL configuration for ESPN app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.espn.views import EventViewSet, LeagueViewSet, SeasonViewSet, SportViewSet, TeamViewSet

app_name = "espn"

router = DefaultRouter()
router.register(r"sports", SportViewSet, basename="sport")
router.register(r"leagues", LeagueViewSet, basename="league")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"seasons", SeasonViewSet, basename="season")
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]

"""URL configuration for ESPN app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.espn.views import EventViewSet, TeamViewSet

app_name = "espn"

router = DefaultRouter()
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]

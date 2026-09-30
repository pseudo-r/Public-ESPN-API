"""Tests for NHL models."""

import pytest

from apps.nhl.models import Team

pytestmark = pytest.mark.django_db


class TestTeamModel:
    def test_team_creation(self) -> None:
        """Test creating a Team model instance."""
        team = Team.objects.create(
            team_id="10",
            abbreviation="TOR",
            name="Maple Leafs",
            full_name="Toronto Maple Leafs",
            franchise_id="5"
        )
        assert team.team_id == "10"
        assert str(team) == "Toronto Maple Leafs (TOR)"
        assert team.is_active is True

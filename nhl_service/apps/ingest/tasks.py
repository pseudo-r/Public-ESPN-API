"""Celery ingestion tasks for NHL data."""

import logging
from datetime import datetime
from typing import Any

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.nhl.models import (
    Player,
    Standing,
    Team,
)
from clients.nhl_client import NHLStatsClient, NHLWebClient

logger = logging.getLogger(__name__)


@shared_task
def sync_teams() -> str:
    """Sync all NHL teams from the Stats REST API."""
    with NHLStatsClient() as stats_client:
        response = stats_client.get_teams()
        teams_data: list[dict[str, Any]] = response.get("data", [])
        if not teams_data:
            raise ValueError("Refusing to replace teams with an empty snapshot")

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            # Set all to inactive first, then mark active if they appear in the feed
            Team.objects.update(is_active=False)

            for t_data in teams_data:
                # Stats API team IDs are ints in the feed
                if not t_data.get("id"):
                    raise ValueError("Team is missing its upstream ID")
                team_id = str(t_data["id"])

                # Some fields
                name = t_data.get("fullName", "")
                abbrev = t_data.get("triCode", "")
                if not abbrev:
                    abbrev = t_data.get("rawTricode", "")

                franchise_id = str(t_data.get("franchiseId", ""))

                team, created = Team.objects.update_or_create(
                    team_id=team_id,
                    defaults={
                        "abbreviation": abbrev,
                        "name": name.split()[-1] if name else "",
                        "full_name": name,
                        "franchise_id": franchise_id,
                        "is_active": True,
                        "raw_data": t_data,
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        return f"Teams sync complete. Created: {created_count}, Updated: {updated_count}"


@shared_task
def sync_team_rosters() -> str:
    """Sync current active players from all active teams."""
    with NHLWebClient() as web_client:
        active_teams = Team.objects.filter(is_active=True)

        total_created = 0
        total_updated = 0

        # We do not mark all inactive here, as we loop team by team.
        # A full player sync would need to handle trades and demotions strictly.
        # This is a simplified active roster ingestion.

        for team in active_teams:
            try:
                roster_data = web_client.get_roster(team.abbreviation)

                # Roster has 'forwards', 'defensemen', 'goalies'
                players_in_roster = []
                players_in_roster.extend(roster_data.get("forwards", []))
                players_in_roster.extend(roster_data.get("defensemen", []))
                players_in_roster.extend(roster_data.get("goalies", []))

                with transaction.atomic():
                    # For basic sync, just ensure they exist
                    for p_data in players_in_roster:
                        if not p_data.get("id"):
                            raise ValueError("Player is missing its upstream ID")
                        player_id = str(p_data["id"])
                        first_name = p_data.get("firstName", {}).get("default", "")
                        last_name = p_data.get("lastName", {}).get("default", "")
                        full_name = f"{first_name} {last_name}".strip()

                        sweater = str(p_data.get("sweaterNumber", ""))
                        position = p_data.get("positionCode", "")
                        headshot = p_data.get("headshot", "")

                        player, created = Player.objects.update_or_create(
                            player_id=player_id,
                            defaults={
                                "first_name": first_name,
                                "last_name": last_name,
                                "full_name": full_name,
                                "sweater_number": sweater,
                                "position": position,
                                "current_team": team,
                                "is_active": True,
                                "headshot_url": headshot,
                                "raw_data": p_data,
                            },
                        )

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1

            except Exception as e:
                logger.error("Failed to sync roster for %s: %s", team.abbreviation, e)

        return f"Roster sync complete. Created: {total_created}, Updated: {total_updated}"


@shared_task
def sync_standings() -> str:
    """Sync current league standings."""
    with NHLWebClient() as web_client:
        response = web_client.get_standings()

        standings_data = response.get("standings", [])
        if not standings_data:
            return "No standings data found."

        date_str = response.get("standingsDate", timezone.now().strftime("%Y-%m-%d"))
        # The API might give the 'now' datetime, slice to YYYY-MM-DD
        sync_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for st_data in standings_data:
                team_abbrev = st_data.get("teamAbbrev", "")
                if isinstance(team_abbrev, dict):
                    team_abbrev = team_abbrev.get("default", "")

                # If team missing, try finding by name or just skip
                try:
                    team = Team.objects.get(abbreviation=team_abbrev)
                except Team.DoesNotExist:
                    logger.warning("Team %s not found in DB. Run sync_teams first.", team_abbrev)
                    continue

                games_played = st_data.get("gamesPlayed", 0)
                wins = st_data.get("wins", 0)
                losses = st_data.get("losses", 0)
                ot_losses = st_data.get("otLosses", 0)
                points = st_data.get("points", 0)
                point_pct = st_data.get("pointPctg", 0.0)

                div_name = st_data.get("divisionName", "")
                conf_name = st_data.get("conferenceName", "")

                standing, created = Standing.objects.update_or_create(
                    team=team,
                    date=datetime.strptime(st_data.get("date", str(sync_date))[:10], "%Y-%m-%d").date(),
                    defaults={
                        "games_played": games_played,
                        "wins": wins,
                        "losses": losses,
                        "ot_losses": ot_losses,
                        "points": points,
                        "point_pct": point_pct,
                        "division_name": div_name,
                        "conference_name": conf_name,
                        "raw_data": st_data,
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        return f"Standings sync complete for {sync_date}. Created: {created_count}, Updated: {updated_count}"

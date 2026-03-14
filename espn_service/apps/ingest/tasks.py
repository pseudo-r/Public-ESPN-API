"""Task functions for Django-Q2.

These functions are referenced by name in Django-Q2 schedules
and can be triggered manually via the admin.
"""

from datetime import timedelta

import structlog
from django.utils import timezone

from apps.ingest.services import ScoreboardIngestionService, TeamIngestionService

logger = structlog.get_logger(__name__)

# All major leagues to refresh in scheduled tasks.
ALL_LEAGUES_CONFIG: list[tuple[str, str]] = [
    # Football
    ("football", "nfl"),
    ("football", "college-football"),
    ("football", "cfl"),
    ("football", "ufl"),
    # Basketball
    ("basketball", "nba"),
    ("basketball", "wnba"),
    ("basketball", "mens-college-basketball"),
    ("basketball", "womens-college-basketball"),
    ("basketball", "nba-development"),
    # Baseball
    ("baseball", "mlb"),
    ("baseball", "college-baseball"),
    # Hockey
    ("hockey", "nhl"),
    ("hockey", "mens-college-hockey"),
    # Soccer (major leagues)
    ("soccer", "eng.1"),
    ("soccer", "usa.1"),
    ("soccer", "esp.1"),
    ("soccer", "ger.1"),
    ("soccer", "ita.1"),
    ("soccer", "fra.1"),
    ("soccer", "mex.1"),
    ("soccer", "uefa.champions"),
    ("soccer", "uefa.europa"),
    ("soccer", "usa.nwsl"),
    # MMA
    ("mma", "ufc"),
    # Golf
    ("golf", "pga"),
    ("golf", "lpga"),
    ("golf", "liv"),
    # Tennis
    ("tennis", "atp"),
    ("tennis", "wta"),
    # Racing
    ("racing", "f1"),
    ("racing", "irl"),
    ("racing", "nascar-premier"),
    # Rugby (numeric slugs)
    ("rugby", "164205"),   # Rugby World Cup
    ("rugby", "180659"),   # Six Nations
    ("rugby", "267979"),   # Gallagher Premiership
    ("rugby", "242041"),   # Super Rugby Pacific
    # Rugby League
    ("rugby-league", "3"),
    # Lacrosse
    ("lacrosse", "pll"),
    ("lacrosse", "nll"),
    # Australian Football
    ("australian-football", "afl"),
    # Cricket
    ("cricket", "icc.t20"),
    ("cricket", "ipl"),
    # Volleyball
    ("volleyball", "fivb.w"),
    ("volleyball", "fivb.m"),
]


def refresh_scoreboard(sport: str, league: str, date: str | None = None) -> dict:
    """Refresh scoreboard data for a sport/league."""
    logger.info("starting_scoreboard_refresh", sport=sport, league=league, date=date)
    service = ScoreboardIngestionService()
    result = service.ingest_scoreboard(sport, league, date)
    logger.info(
        "completed_scoreboard_refresh",
        sport=sport,
        league=league,
        created=result.created,
        updated=result.updated,
        errors=result.errors,
    )
    return result.to_dict()


def refresh_teams(sport: str, league: str) -> dict:
    """Refresh team data for a sport/league."""
    logger.info("starting_teams_refresh", sport=sport, league=league)
    service = TeamIngestionService()
    result = service.ingest_teams(sport, league)
    logger.info(
        "completed_teams_refresh",
        sport=sport,
        league=league,
        created=result.created,
        updated=result.updated,
        errors=result.errors,
    )
    return result.to_dict()


def refresh_all_teams() -> dict:
    """Refresh team data for all configured leagues."""
    results = {}
    for sport, league in ALL_LEAGUES_CONFIG:
        try:
            service = TeamIngestionService()
            result = service.ingest_teams(sport, league)
            results[f"{sport}/{league}"] = result.to_dict()
        except Exception as e:
            logger.error(
                "league_teams_refresh_failed", sport=sport, league=league, error=str(e)
            )
            results[f"{sport}/{league}"] = {"error": str(e)}
    return results


def refresh_daily_scoreboards() -> dict:
    """Refresh today's scoreboards for all configured leagues."""
    today = timezone.now().strftime("%Y%m%d")
    results = {}
    for sport, league in ALL_LEAGUES_CONFIG:
        try:
            service = ScoreboardIngestionService()
            result = service.ingest_scoreboard(sport, league, today)
            results[f"{sport}/{league}"] = result.to_dict()
        except Exception as e:
            logger.error(
                "league_scoreboard_refresh_failed",
                sport=sport,
                league=league,
                date=today,
                error=str(e),
            )
            results[f"{sport}/{league}"] = {"error": str(e)}
    return results


def purge_old_results() -> dict:
    """Delete task results older than 90 days."""
    from django_q.models import Failure, Success

    cutoff = timezone.now() - timedelta(days=90)
    s_count, _ = Success.objects.filter(stopped__lt=cutoff).delete()
    f_count, _ = Failure.objects.filter(stopped__lt=cutoff).delete()
    return {"purged_success": s_count, "purged_failure": f_count}

"""Celery tasks for data ingestion.

These tasks can be scheduled via Celery Beat or triggered manually.
"""

from datetime import datetime

import structlog
from celery import shared_task

from apps.ingest.services import ScoreboardIngestionService, TeamIngestionService

logger = structlog.get_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    acks_late=True,
)
def refresh_scoreboard_task(
    self,
    sport: str,
    league: str,
    date: str | None = None,
) -> dict:
    """Celery task to refresh scoreboard data.

    Args:
        sport: Sport slug (e.g., "basketball")
        league: League slug (e.g., "nba")
        date: Optional date in YYYYMMDD format

    Returns:
        Dict with ingestion results
    """
    logger.info(
        "starting_scoreboard_refresh_task",
        sport=sport,
        league=league,
        date=date,
        task_id=self.request.id,
    )

    service = ScoreboardIngestionService()
    result = service.ingest_scoreboard(sport, league, date)

    logger.info(
        "completed_scoreboard_refresh_task",
        sport=sport,
        league=league,
        date=date,
        created=result.created,
        updated=result.updated,
        errors=result.errors,
        task_id=self.request.id,
    )

    return result.to_dict()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    acks_late=True,
)
def refresh_teams_task(
    self,
    sport: str,
    league: str,
) -> dict:
    """Celery task to refresh team data.

    Args:
        sport: Sport slug (e.g., "basketball")
        league: League slug (e.g., "nba")

    Returns:
        Dict with ingestion results
    """
    logger.info(
        "starting_teams_refresh_task",
        sport=sport,
        league=league,
        task_id=self.request.id,
    )

    service = TeamIngestionService()
    result = service.ingest_teams(sport, league)

    logger.info(
        "completed_teams_refresh_task",
        sport=sport,
        league=league,
        created=result.created,
        updated=result.updated,
        errors=result.errors,
        task_id=self.request.id,
    )

    return result.to_dict()


@shared_task(bind=True)
def refresh_all_teams_task(self) -> dict:
    """Celery task to refresh team data for all configured leagues.

    Returns:
        Dict with aggregated results by league
    """
    # Default leagues to refresh
    leagues_config = [
        ("basketball", "nba"),
        ("basketball", "wnba"),
        ("football", "nfl"),
        ("baseball", "mlb"),
        ("hockey", "nhl"),
    ]

    results = {}

    for sport, league in leagues_config:
        try:
            service = TeamIngestionService()
            result = service.ingest_teams(sport, league)
            results[f"{sport}/{league}"] = result.to_dict()
        except Exception as e:
            logger.error(
                "league_teams_refresh_failed",
                sport=sport,
                league=league,
                error=str(e),
            )
            results[f"{sport}/{league}"] = {"error": str(e)}

    return results


@shared_task(bind=True)
def refresh_daily_scoreboards_task(self) -> dict:
    """Celery task to refresh today's scoreboards for all leagues.

    Returns:
        Dict with aggregated results by league
    """
    today = datetime.now().strftime("%Y%m%d")

    # Default leagues to refresh
    leagues_config = [
        ("basketball", "nba"),
        ("basketball", "wnba"),
        ("football", "nfl"),
        ("baseball", "mlb"),
        ("hockey", "nhl"),
    ]

    results = {}

    for sport, league in leagues_config:
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

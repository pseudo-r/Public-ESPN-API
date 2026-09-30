"""HTTP clients for communicating with external NHL APIs."""

import logging
from typing import Any

import httpx
from django.conf import settings
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


def _is_transient(exc):
    return isinstance(exc, httpx.TransportError) or (
        isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code >= 500
    )


class ManagedClient:
    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class NHLWebClient(ManagedClient):
    """Client for modern api-web.nhle.com endpoints."""

    def __init__(self) -> None:
        self.base_url = settings.NHL_API_WEB_BASE_URL
        self.client = httpx.Client(timeout=settings.NHL_API_TIMEOUT)

    @retry(retry=retry_if_exception(_is_transient), stop=stop_after_attempt(settings.NHL_API_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.debug("NHLWebClient GET %s", url)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_standings(self) -> dict[str, Any]:
        """Get current standings."""
        return self._get("v1/standings/now")

    def get_roster(self, team_abbrev: str) -> dict[str, Any]:
        """Get current roster for a team."""
        return self._get(f"v1/roster/{team_abbrev}/current")

    def get_player_landing(self, player_id: int | str) -> dict[str, Any]:
        """Get full player profile."""
        return self._get(f"v1/player/{player_id}/landing")

    def get_schedule(self, date: str | None = None) -> dict[str, Any]:
        """Get schedule (now or specific YYYY-MM-DD date)."""
        endpoint = f"v1/schedule/{date}" if date else "v1/schedule/now"
        return self._get(endpoint)

    def get_boxscore(self, game_id: int | str) -> dict[str, Any]:
        """Get game boxscore."""
        return self._get(f"v1/gamecenter/{game_id}/boxscore")


class NHLStatsClient(ManagedClient):
    """Client for api.nhle.com/stats/rest endpoints."""

    def __init__(self) -> None:
        self.base_url = settings.NHL_API_STATS_BASE_URL
        self.client = httpx.Client(timeout=settings.NHL_API_TIMEOUT)

    @retry(retry=retry_if_exception(_is_transient), stop=stop_after_attempt(settings.NHL_API_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.debug("NHLStatsClient GET %s", url)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_teams(self) -> dict[str, Any]:
        """Get all teams."""
        return self._get("en/team")

    def get_skater_summary(self, season_id: str, limit: int = -1) -> dict[str, Any]:
        """Get skater scoring summary for a season."""
        params = {"cayenneExp": f"seasonId={season_id}", "limit": limit}
        return self._get("en/skater/summary", params=params)

    def get_goalie_summary(self, season_id: str, limit: int = -1) -> dict[str, Any]:
        """Get goalie summary for a season."""
        params = {"cayenneExp": f"seasonId={season_id}", "limit": limit}
        return self._get("en/goalie/summary", params=params)

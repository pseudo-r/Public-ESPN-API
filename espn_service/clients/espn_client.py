"""ESPN API client with retry logic, timeouts, and error handling.

This module provides a centralized client for all ESPN API interactions.
All ESPN API calls should go through this client to ensure consistent
error handling, retries, and rate limiting.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import httpx
import structlog
from django.conf import settings
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from apps.core.exceptions import (
    ESPNClientError,
    ESPNNotFoundError,
    ESPNRateLimitError,
)

logger = structlog.get_logger(__name__)


class ESPNEndpointDomain(str, Enum):
    """ESPN API domain types."""

    SITE = "site"  # site.api.espn.com
    CORE = "core"  # sports.core.api.espn.com


@dataclass
class ESPNResponse:
    """Wrapper for ESPN API responses."""

    data: dict[str, Any]
    status_code: int
    url: str

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300


class ESPNClient:
    """Client for ESPN API interactions.

    This client handles:
    - Multiple ESPN API domains (site, core)
    - Automatic retries with exponential backoff
    - Request timeouts
    - Rate limiting guidance
    - Defensive JSON parsing
    - Structured error responses

    Usage:
        client = ESPNClient()
        response = client.get_scoreboard("basketball", "nba", "20241215")
        teams = client.get_teams("basketball", "nba")
    """

    def __init__(
        self,
        site_api_url: str | None = None,
        core_api_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        user_agent: str | None = None,
    ):
        """Initialize ESPN client.

        Args:
            site_api_url: Base URL for site.api.espn.com
            core_api_url: Base URL for sports.core.api.espn.com
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            user_agent: User-Agent header value
        """
        config = getattr(settings, "ESPN_CLIENT", {})

        self.site_api_url = (
            site_api_url or config.get("SITE_API_BASE_URL", "https://site.api.espn.com")
        ).rstrip("/")
        self.core_api_url = (
            core_api_url or config.get("CORE_API_BASE_URL", "https://sports.core.api.espn.com")
        ).rstrip("/")
        self.timeout = timeout or config.get("TIMEOUT", 30.0)
        self.max_retries = max_retries or config.get("MAX_RETRIES", 3)
        self.retry_backoff = config.get("RETRY_BACKOFF", 1.0)
        self.user_agent = user_agent or config.get(
            "USER_AGENT", "ESPN-Service/1.0"
        )

        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client (lazy initialization)."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "application/json",
                },
                follow_redirects=True,
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None

    def __enter__(self) -> "ESPNClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _get_base_url(self, domain: ESPNEndpointDomain) -> str:
        """Get base URL for the given domain."""
        if domain == ESPNEndpointDomain.SITE:
            return self.site_api_url
        return self.core_api_url

    def _build_url(self, domain: ESPNEndpointDomain, path: str) -> str:
        """Build full URL from domain and path."""
        base_url = self._get_base_url(domain)
        path = path.lstrip("/")
        return f"{base_url}/{path}"

    def _handle_response(self, response: httpx.Response, url: str) -> ESPNResponse:
        """Handle HTTP response and convert to ESPNResponse.

        Args:
            response: HTTP response object
            url: Request URL (for logging)

        Returns:
            ESPNResponse with parsed data

        Raises:
            ESPNNotFoundError: If resource not found (404)
            ESPNRateLimitError: If rate limited (429)
            ESPNClientError: For other HTTP errors
        """
        if response.status_code == 404:
            logger.warning("espn_resource_not_found", url=url)
            raise ESPNNotFoundError(f"ESPN resource not found: {url}")

        if response.status_code == 429:
            logger.warning("espn_rate_limited", url=url)
            raise ESPNRateLimitError("ESPN API rate limit exceeded")

        if response.status_code >= 500:
            logger.error(
                "espn_server_error",
                url=url,
                status_code=response.status_code,
            )
            # Raise for retry
            raise ESPNClientError(f"ESPN server error: {response.status_code}")

        if response.status_code >= 400:
            logger.error(
                "espn_client_error",
                url=url,
                status_code=response.status_code,
            )
            raise ESPNClientError(f"ESPN API error: {response.status_code}")

        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            logger.error("espn_json_parse_error", url=url, error=str(e))
            raise ESPNClientError(f"Failed to parse ESPN response: {e}") from e

        return ESPNResponse(data=data, status_code=response.status_code, url=url)

    def _request_with_retry(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> ESPNResponse:
        """Make HTTP request with retry logic.

        This method implements exponential backoff retry for transient failures.
        """

        @retry(
            retry=retry_if_exception_type((httpx.TransportError, ESPNClientError)),
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.retry_backoff, min=1, max=10),
            reraise=True,
        )
        def _do_request() -> ESPNResponse:
            logger.debug("espn_request", method=method, url=url, params=params)
            response = self.client.request(method, url, params=params)
            return self._handle_response(response, url)

        try:
            return _do_request()
        except RetryError as e:
            logger.error(
                "espn_request_failed_after_retries",
                url=url,
                retries=self.max_retries,
            )
            raise ESPNClientError(
                f"ESPN request failed after {self.max_retries} retries"
            ) from e
        except (ESPNNotFoundError, ESPNRateLimitError):
            # These should not be retried, re-raise directly
            raise
        except httpx.TransportError as e:
            logger.error("espn_transport_error", url=url, error=str(e))
            raise ESPNClientError(f"ESPN connection error: {e}") from e

    def get(
        self,
        path: str,
        domain: ESPNEndpointDomain = ESPNEndpointDomain.SITE,
        params: dict[str, Any] | None = None,
    ) -> ESPNResponse:
        """Make GET request to ESPN API.

        Args:
            path: API path (e.g., "/apis/site/v2/sports/basketball/nba/scoreboard")
            domain: Which ESPN domain to use
            params: Query parameters

        Returns:
            ESPNResponse with parsed data
        """
        url = self._build_url(domain, path)
        return self._request_with_retry("GET", url, params=params)

    # --------------------- Scoreboard Endpoints ---------------------

    def get_scoreboard(
        self,
        sport: str,
        league: str,
        date: str | datetime | None = None,
        limit: int | None = None,
    ) -> ESPNResponse:
        """Get scoreboard/schedule for a sport and league.

        Args:
            sport: Sport slug (e.g., "basketball", "football")
            league: League slug (e.g., "nba", "nfl")
            date: Date to get scoreboard for (YYYYMMDD format or datetime)
            limit: Maximum number of events to return

        Returns:
            ESPNResponse with scoreboard data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/scoreboard"
        params: dict[str, Any] = {}

        if date:
            if isinstance(date, datetime):
                date = date.strftime("%Y%m%d")
            params["dates"] = date

        if limit:
            params["limit"] = limit

        logger.info(
            "fetching_scoreboard",
            sport=sport,
            league=league,
            date=date,
        )
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    # --------------------- Team Endpoints ---------------------

    def get_teams(
        self,
        sport: str,
        league: str,
        limit: int = 100,
    ) -> ESPNResponse:
        """Get all teams for a sport and league.

        Args:
            sport: Sport slug (e.g., "basketball", "football")
            league: League slug (e.g., "nba", "nfl")
            limit: Maximum number of teams to return

        Returns:
            ESPNResponse with teams data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams"
        params = {"limit": limit}

        logger.info("fetching_teams", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    def get_team(
        self,
        sport: str,
        league: str,
        team_id: str,
    ) -> ESPNResponse:
        """Get details for a specific team.

        Args:
            sport: Sport slug
            league: League slug
            team_id: ESPN team ID

        Returns:
            ESPNResponse with team details
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}"

        logger.info(
            "fetching_team",
            sport=sport,
            league=league,
            team_id=team_id,
        )
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    # --------------------- Event/Game Endpoints ---------------------

    def get_event(
        self,
        sport: str,
        league: str,
        event_id: str,
    ) -> ESPNResponse:
        """Get details for a specific event/game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID

        Returns:
            ESPNResponse with event details
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/summary"
        params = {"event": event_id}

        logger.info(
            "fetching_event",
            sport=sport,
            league=league,
            event_id=event_id,
        )
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    # --------------------- Core API Endpoints ---------------------

    def get_league_info(
        self,
        sport: str,
        league: str,
    ) -> ESPNResponse:
        """Get league information from core API.

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with league information
        """
        path = f"/v2/sports/{sport}/leagues/{league}"

        logger.info("fetching_league_info", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_athletes(
        self,
        sport: str,
        league: str,
        team_id: str | None = None,
        limit: int = 100,
        page: int = 1,
    ) -> ESPNResponse:
        """Get athletes from core API.

        Args:
            sport: Sport slug
            league: League slug
            team_id: Optional team ID to filter by
            limit: Maximum number of athletes
            page: Page number for pagination

        Returns:
            ESPNResponse with athletes data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/athletes"
        params: dict[str, Any] = {"limit": limit, "page": page}

        if team_id:
            params["teams"] = team_id

        logger.info(
            "fetching_athletes",
            sport=sport,
            league=league,
            team_id=team_id,
        )
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)


# Default singleton instance
_default_client: ESPNClient | None = None


def get_espn_client() -> ESPNClient:
    """Get the default ESPN client instance.

    Returns:
        ESPNClient singleton instance
    """
    global _default_client
    if _default_client is None:
        _default_client = ESPNClient()
    return _default_client

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
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from apps.core.exceptions import (
    ESPNClientError,
    ESPNNotFoundError,
    ESPNRateLimitError,
)

logger = structlog.get_logger(__name__)


class ESPNTransientError(ESPNClientError):
    """An upstream server failure that can be retried safely."""


class ESPNEndpointDomain(str, Enum):
    """ESPN API domain types."""

    SITE = "site"          # site.api.espn.com
    CORE = "core"          # sports.core.api.espn.com
    SITE_V2 = "site_v2"    # site.api.espn.com/apis/v2/ — standings only
    WEB_V3 = "web_v3"      # site.web.api.espn.com/apis/common/v3/ — athlete data
    CDN = "cdn"            # cdn.espn.com/core/ — full game packages
    NOW = "now"            # now.core.api.espn.com/v1/ — real-time news


# ─────────────────────────────────────────────────────────────────────────────
# Sports & League Registry
# Curated metadata for 17 sports; see docs/data/leagues.json for live discovery.
# Format: "sport_slug": "Display Name"
# ─────────────────────────────────────────────────────────────────────────────

SPORT_NAMES: dict[str, str] = {
    "australian-football": "Australian Football",
    "baseball": "Baseball",
    "basketball": "Basketball",
    "cricket": "Cricket",
    "field-hockey": "Field Hockey",
    "football": "Football",
    "golf": "Golf",
    "hockey": "Hockey",
    "lacrosse": "Lacrosse",
    "mma": "Mixed Martial Arts",
    "racing": "Racing",
    "rugby": "Rugby",
    "rugby-league": "Rugby League",
    "soccer": "Soccer",
    "tennis": "Tennis",
    "volleyball": "Volleyball",
    "water-polo": "Water Polo",
}

# league_slug: (Display Name, Abbreviation)
LEAGUE_INFO: dict[str, tuple[str, str]] = {
    # Australian Football
    "afl": ("AFL", "AFL"),
    # Baseball
    "caribbean-series": ("Caribbean Series", "CAR"),
    "college-baseball": ("NCAA Baseball", "NCAAB"),
    "college-softball": ("NCAA Softball", "NCAAS"),
    "dominican-winter-league": ("Dominican Winter League", "DWL"),
    "llb": ("Little League Baseball", "LLB"),
    "lls": ("Little League Softball", "LLS"),
    "mexican-winter-league": ("Mexican League", "MLM"),
    "mlb": ("Major League Baseball", "MLB"),
    "olympics-baseball": ("Olympics Men's Baseball", "OLY"),
    "puerto-rican-winter-league": ("Puerto Rican Winter League", "PRWL"),
    "venezuelan-winter-league": ("Venezuelan Winter League", "VWL"),
    "world-baseball-classic": ("World Baseball Classic", "WBC"),
    # Basketball
    "fiba": ("FIBA World Cup", "FIBA"),
    "mens-college-basketball": ("NCAA Men's Basketball", "NCAAM"),
    "mens-olympics-basketball": ("Olympics Men's Basketball", "OLY"),
    "nba": ("National Basketball Association", "NBA"),
    "nba-development": ("NBA G League", "GLEA"),
    "nba-summer-california": ("NBA California Classic Summer League", "NBASL"),
    "nba-summer-golden-state": ("Golden State Summer League", "GSSL"),
    "nba-summer-las-vegas": ("Las Vegas Summer League", "LVSL"),
    "nba-summer-orlando": ("Orlando Summer League", "OSL"),
    "nba-summer-sacramento": ("Sacramento Summer League", "SASL"),
    "nba-summer-utah": ("Salt Lake City Summer League", "SLSL"),
    "nbl": ("National Basketball League", "NBL"),
    "wnba": ("Women's National Basketball Association", "WNBA"),
    "womens-college-basketball": ("NCAA Women's Basketball", "NCAAW"),
    "womens-olympics-basketball": ("Olympics Women's Basketball", "OLY"),
    # Field Hockey
    "womens-college-field-hockey": ("NCAA Women's Field Hockey", "NCAAFH"),
    # Football
    "cfl": ("Canadian Football League", "CFL"),
    "college-football": ("NCAA Football", "NCAAF"),
    "nfl": ("National Football League", "NFL"),
    "ufl": ("United Football League", "UFL"),
    "xfl": ("XFL", "XFL"),
    # Golf
    "champions-tour": ("PGA TOUR Champions", "CHAMP"),
    "eur": ("DP World Tour", "DP"),
    "liv": ("LIV Golf Invitational Series", "LIV"),
    "lpga": ("Ladies Pro Golf Association", "LPGA"),
    "mens-olympics-golf": ("Olympic Golf - Men", "OLY"),
    "ntw": ("Korn Ferry Tour", "KFT"),
    "pga": ("PGA TOUR", "PGA"),
    "tgl": ("TGL", "TGL"),
    "womens-olympics-golf": ("Olympic Golf - Women", "OLY"),
    # Hockey
    "hockey-world-cup": ("World Cup of Hockey", "WCOH"),
    "mens-college-hockey": ("NCAA Men's Ice Hockey", "NCAAH"),
    "nhl": ("National Hockey League", "NHL"),
    "olympics-mens-ice-hockey": ("Men's Ice Hockey Olympics", "OLY"),
    "olympics-womens-ice-hockey": ("Women's Ice Hockey Olympics", "OLY"),
    "womens-college-hockey": ("NCAA Women's Hockey", "NCAAWH"),
    # Lacrosse
    "mens-college-lacrosse": ("NCAA Men's Lacrosse", "NCAML"),
    "nll": ("National Lacrosse League", "NLL"),
    "pll": ("Premier Lacrosse League", "PLL"),
    "womens-college-lacrosse": ("NCAA Women's Lacrosse", "NCAWL"),
    # MMA
    "ufc": ("Ultimate Fighting Championship", "UFC"),
    "absolute": ("Absolute Championship Berkut", "ACB"),
    "affliction": ("Affliction", "AFF"),
    "bang-fighting": ("Bang Fighting Championships", "BFC"),
    "banni-fight": ("Banni Fight Combat", "BFC"),
    "banzay": ("Banzay Fight Championship", "BZY"),
    "barracao": ("Barracao Fight Championship", "BFC"),
    "battlezone": ("Battlezone Fighting Championships", "BZN"),
    "bellator": ("Bellator Fighting Championship", "BEL"),
    "benevides": ("Benevides Fight Championship", "BFG"),
    "big-fight": ("Big Fight Champions", "BFC"),
    "blackout": ("Blackout Fighting Championship", "BOF"),
    "bosnia": ("Bosnia Fight Championship", "BFC"),
    "boxe": ("Boxe Fight Combat", "BXE"),
    "brazilian-freestyle": ("Brazilian Freestyle Circuit", "BRC"),
    "budo": ("Budo Fighting Championships", "BDO"),
    "cage-warriors": ("Cage Warriors Fighting Championship", "CW"),
    "dream": ("Dream", "DRM"),
    "fng": ("Fight Nights Global", "FNG"),
    "ifc": ("Invicta FC", "IFC"),
    "ifl": ("International Fight League", "IFL"),
    "k1": ("K-1", "K1"),
    "ksw": ("Konfrontacja Sztuk Walki", "KSW"),
    "lfa": ("Legacy Fighting Alliance", "LFA"),
    "lfc": ("Legacy Fighting Championship", "LFC"),
    "m1": ("M-1 Mix-Fight Championship", "M1"),
    # Racing
    "f1": ("Formula 1", "F1"),
    "irl": ("IndyCar Series", "INDY"),
    "nascar-premier": ("NASCAR Cup Series", "CUP"),
    "nascar-secondary": ("NASCAR O'Reilly Auto Parts Series", "XFN"),
    "nascar-truck": ("NASCAR Truck Series", "TRUCK"),
    # Rugby (numeric IDs)
    "268565": ("British and Irish Lions Tour", "BILT"),
    "164205": ("Rugby World Cup", "RWC"),
    "180659": ("Six Nations", "6N"),
    "244293": ("The Rugby Championship", "TRC"),
    "271937": ("European Rugby Champions Cup", "EPCR"),
    "272073": ("European Rugby Challenge Cup", "ERCC"),
    "267979": ("Gallagher Premiership", "PREM"),
    "270557": ("United Rugby Championship", "URC"),
    "270559": ("French Top 14", "TOP14"),
    "2009": ("URBA Primera A", "URBA"),
    "242041": ("Super Rugby Pacific", "SRP"),
    "289271": ("Super Rugby Aotearoa", "SRA"),
    "289272": ("Super Rugby AU", "SRAU"),
    "289277": ("Super Rugby Trans-Tasman", "SRTT"),
    "289279": ("URBA Top 12", "T12"),
    "270555": ("Currie Cup", "CC"),
    "270563": ("Mitre 10 Cup", "M10"),
    "236461": ("Anglo-Welsh Cup", "AWC"),
    "289274": ("2020 Tri Nations", "TN"),
    "282": ("Olympic Men's 7s", "OLY"),
    "283": ("Olympic Women's Rugby Sevens", "OLY"),
    "289237": ("Women's Rugby World Cup", "WRWC"),
    "289262": ("Major League Rugby", "MLR"),
    "289234": ("International Test Match", "INT"),
    # Rugby League
    "3": ("Rugby League", "RL"),
    # Soccer
    "eng.2": ("English League Championship", "EFL"),
    "fifa.world": ("FIFA World Cup", "WC"),
    "fifa.wwc": ("FIFA Women's World Cup", "WWC"),
    "uefa.champions": ("UEFA Champions League", "UCL"),
    "eng.1": ("English Premier League", "EPL"),
    "eng.fa": ("English FA Cup", "FAC"),
    "eng.league_cup": ("English Carabao Cup", "ELC"),
    "esp.1": ("Spanish LALIGA", "LIGA"),
    "esp.super_cup": ("Spanish Supercopa", "SC"),
    "esp.copa_del_rey": ("Spanish Copa del Rey", "CDR"),
    "ger.1": ("German Bundesliga", "BUN"),
    "ger.dfb_pokal": ("German Cup", "DFB"),
    "usa.1": ("MLS", "MLS"),
    "concacaf.leagues.cup": ("Leagues Cup", "LC"),
    "campeones.cup": ("Campeones Cup", "CC"),
    "fifa.shebelieves": ("SheBelieves Cup", "SBC"),
    "fifa.w.champions_cup": ("FIFA Women's Champions Cup", "WCC"),
    "uefa.wchampions": ("UEFA Women's Champions League", "UWCL"),
    "usa.nwsl": ("NWSL", "NWSL"),
    "usa.nwsl.cup": ("NWSL Challenge Cup", "NWSLCC"),
    "uefa.europa": ("UEFA Europa League", "UEL"),
    "uefa.europa.conf": ("UEFA Conference League", "UECL"),
    "mex.1": ("Mexican Liga BBVA MX", "LIGAMX"),
    "ita.1": ("Italian Serie A", "SA"),
    "ita.coppa_italia": ("Coppa Italia", "CI"),
    "fra.1": ("French Ligue 1", "L1"),
    # Tennis
    "atp": ("ATP", "ATP"),
    "wta": ("WTA", "WTA"),
    # Volleyball
    "mens-college-volleyball": ("NCAA Men's Volleyball", "NCAMV"),
    "womens-college-volleyball": ("NCAA Women's Volleyball", "NCAWV"),
    # Water Polo
    "mens-college-water-polo": ("NCAA Men's Water Polo", "NCAMWP"),
    "womens-college-water-polo": ("NCAA Women's Water Polo", "NCAWWP"),
}


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
    - Multiple ESPN API domains (site, core v2, core v3)
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

        Supports all discovered ESPN API domains:
        - site.api.espn.com          → scoreboard, teams, news, injuries, etc.
        - site.api.espn.com/apis/v2/ → standings (site/v2 returns a stub)
        - sports.core.api.espn.com   → core data, odds, play-by-play
        - site.web.api.espn.com      → athlete stats, gamelog, splits (common/v3)
        - cdn.espn.com/core/         → full game packages with drives/plays
        - now.core.api.espn.com/v1/  → real-time news feed

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
        self.web_v3_url = config.get(
            "WEB_V3_API_BASE_URL", "https://site.web.api.espn.com"
        ).rstrip("/")
        self.cdn_url = config.get(
            "CDN_API_BASE_URL", "https://cdn.espn.com"
        ).rstrip("/")
        self.now_url = config.get(
            "NOW_API_BASE_URL", "https://now.core.api.espn.com"
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
        if domain == ESPNEndpointDomain.SITE_V2:
            return self.site_api_url
        if domain == ESPNEndpointDomain.WEB_V3:
            return self.web_v3_url
        if domain == ESPNEndpointDomain.CDN:
            return self.cdn_url
        if domain == ESPNEndpointDomain.NOW:
            return self.now_url
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
            raise ESPNTransientError(f"ESPN server error: {response.status_code}")

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
            retry=retry_if_exception(
                lambda exc: isinstance(exc, httpx.TransportError | ESPNTransientError)
            ),
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

    def get_team_roster(
        self,
        sport: str,
        league: str,
        team_id: str,
    ) -> ESPNResponse:
        """Get roster for a specific team.

        Args:
            sport: Sport slug
            league: League slug
            team_id: ESPN team ID

        Returns:
            ESPNResponse with roster data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/roster"
        logger.info("fetching_team_roster", sport=sport, league=league, team_id=team_id)
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

    def get_news(
        self,
        sport: str,
        league: str,
        limit: int = 25,
    ) -> ESPNResponse:
        """Get news for a sport and league.

        Args:
            sport: Sport slug
            league: League slug
            limit: Number of articles to return

        Returns:
            ESPNResponse with news data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/news"
        params: dict[str, Any] = {"limit": limit}
        logger.info("fetching_news", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    def get_standings(
        self,
        sport: str,
        league: str,
        season: int | None = None,
    ) -> ESPNResponse:
        """Get league standings.

        Uses /apis/v2/ domain — /apis/site/v2/ standings only returns a stub.
        Rugby Union standings are not available via this domain; use get_core_standings().

        Args:
            sport: Sport slug
            league: League slug
            season: Season year (optional)

        Returns:
            ESPNResponse with standings data
        """
        # NOTE: /apis/site/v2/ returns only a stub {"fullViewLink": {...}}
        # Use /apis/v2/ which returns the full standings tree
        path = f"/apis/v2/sports/{sport}/{league}/standings"
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        logger.info("fetching_standings", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE, params=params)

    def get_rankings(
        self,
        sport: str,
        league: str,
    ) -> ESPNResponse:
        """Get league rankings (college sports).

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with rankings data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/rankings"
        logger.info("fetching_rankings", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    # --------------------- Core API v2 Endpoints ---------------------

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
        active: bool | None = None,
    ) -> ESPNResponse:
        """Get athletes from core API.

        Args:
            sport: Sport slug
            league: League slug
            team_id: Optional team ID to filter by
            limit: Maximum number of athletes
            page: Page number for pagination
            active: Filter by active status

        Returns:
            ESPNResponse with athletes data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/athletes"
        params: dict[str, Any] = {"limit": limit, "page": page}

        if team_id:
            params["teams"] = team_id
        if active is not None:
            params["active"] = "true" if active else "false"

        logger.info(
            "fetching_athletes",
            sport=sport,
            league=league,
            team_id=team_id,
        )
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_athlete(
        self,
        sport: str,
        league: str,
        athlete_id: str | int,
    ) -> ESPNResponse:
        """Get a single athlete from the core API.

        Args:
            sport: Sport slug
            league: League slug
            athlete_id: ESPN athlete ID

        Returns:
            ESPNResponse with athlete data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/athletes/{athlete_id}"
        logger.info("fetching_athlete", sport=sport, league=league, athlete_id=athlete_id)
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_athlete_statistics(
        self,
        sport: str,
        league: str,
        athlete_id: str | int,
        season_type: str | None = None,
    ) -> ESPNResponse:
        """Get career statistics for an athlete.

        Args:
            sport: Sport slug
            league: League slug
            athlete_id: ESPN athlete ID
            season_type: Season type (e.g., "2" for regular season)

        Returns:
            ESPNResponse with statistics data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/athletes/{athlete_id}/statistics"
        params: dict[str, Any] = {}
        if season_type:
            params["seasonType"] = season_type
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_core_events(
        self,
        sport: str,
        league: str,
        dates: str | None = None,
        limit: int = 100,
        page: int = 1,
    ) -> ESPNResponse:
        """Get events from the core API (more detailed than site API).

        Args:
            sport: Sport slug
            league: League slug
            dates: Date or range filter (e.g., "2024" or "20241215")
            limit: Maximum results per page
            page: Page number

        Returns:
            ESPNResponse with events data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/events"
        params: dict[str, Any] = {"limit": limit, "page": page}
        if dates:
            params["dates"] = dates
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_seasons(
        self,
        sport: str,
        league: str,
        limit: int = 20,
    ) -> ESPNResponse:
        """Get seasons list for a league.

        Args:
            sport: Sport slug
            league: League slug
            limit: Maximum number of seasons

        Returns:
            ESPNResponse with seasons data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/seasons"
        params: dict[str, Any] = {"limit": limit}
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_core_teams(
        self,
        sport: str,
        league: str,
        limit: int = 100,
        page: int = 1,
    ) -> ESPNResponse:
        """Get teams from the core API.

        Args:
            sport: Sport slug
            league: League slug
            limit: Results per page
            page: Page number

        Returns:
            ESPNResponse with teams data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/teams"
        params: dict[str, Any] = {"limit": limit, "page": page}
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_core_standings(
        self,
        sport: str,
        league: str,
        season: int | None = None,
        season_type: int | None = None,
    ) -> ESPNResponse:
        """Get standings from the core API.

        Args:
            sport: Sport slug
            league: League slug
            season: Season year
            season_type: 1=pre, 2=regular, 3=post

        Returns:
            ESPNResponse with standings data
        """
        params: dict[str, Any] = {}
        if season and season_type:
            path = (
                f"/v2/sports/{sport}/leagues/{league}"
                f"/seasons/{season}/types/{season_type}/groups/standings"
            )
        elif season:
            path = f"/v2/sports/{sport}/leagues/{league}/seasons/{season}/standings"
        else:
            path = f"/v2/sports/{sport}/leagues/{league}/standings"
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_odds(
        self,
        sport: str,
        league: str,
        event_id: str,
        competition_id: str | None = None,
    ) -> ESPNResponse:
        """Get betting odds for a game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID
            competition_id: Competition ID (usually same as event_id)

        Returns:
            ESPNResponse with odds data
        """
        comp_id = competition_id or event_id
        path = (
            f"/v2/sports/{sport}/leagues/{league}"
            f"/events/{event_id}/competitions/{comp_id}/odds"
        )
        logger.info("fetching_odds", sport=sport, league=league, event_id=event_id)
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_win_probabilities(
        self,
        sport: str,
        league: str,
        event_id: str,
        competition_id: str | None = None,
    ) -> ESPNResponse:
        """Get win probabilities for a game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID
            competition_id: Competition ID (usually same as event_id)

        Returns:
            ESPNResponse with probability data
        """
        comp_id = competition_id or event_id
        path = (
            f"/v2/sports/{sport}/leagues/{league}"
            f"/events/{event_id}/competitions/{comp_id}/probabilities"
        )
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_plays(
        self,
        sport: str,
        league: str,
        event_id: str,
        competition_id: str | None = None,
        limit: int = 400,
    ) -> ESPNResponse:
        """Get play-by-play data for a game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID
            competition_id: Competition ID (usually same as event_id)
            limit: Max plays to return

        Returns:
            ESPNResponse with play data
        """
        comp_id = competition_id or event_id
        path = (
            f"/v2/sports/{sport}/leagues/{league}"
            f"/events/{event_id}/competitions/{comp_id}/plays"
        )
        params: dict[str, Any] = {"limit": limit}
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_venues(
        self,
        sport: str,
        league: str,
        limit: int = 500,
    ) -> ESPNResponse:
        """Get venues for a league.

        Args:
            sport: Sport slug
            league: League slug
            limit: Maximum venues to return

        Returns:
            ESPNResponse with venue data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/venues"
        params: dict[str, Any] = {"limit": limit}
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_leaders(
        self,
        sport: str,
        league: str,
        season: int | None = None,
        season_type: int | None = None,
    ) -> ESPNResponse:
        """Get statistical leaders for a league.

        Args:
            sport: Sport slug
            league: League slug
            season: Season year
            season_type: 1=pre, 2=regular, 3=post

        Returns:
            ESPNResponse with leaders data
        """
        params: dict[str, Any] = {}
        if season and season_type:
            path = (
                f"/v2/sports/{sport}/leagues/{league}"
                f"/seasons/{season}/types/{season_type}/leaders"
            )
        else:
            path = f"/v2/sports/{sport}/leagues/{league}/leaders"
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    # --------------------- Core API v3 Endpoints ---------------------

    def get_athletes_v3(
        self,
        sport: str,
        league: str,
        limit: int = 1000,
        active: bool | None = True,
        page: int = 1,
    ) -> ESPNResponse:
        """Get athletes from the v3 core API (richer data).

        Args:
            sport: Sport slug
            league: League slug
            limit: Max athletes
            active: Filter by active status
            page: Page number

        Returns:
            ESPNResponse with athletes data
        """
        path = f"/v3/sports/{sport}/{league}/athletes"
        params: dict[str, Any] = {"limit": limit, "page": page}
        if active is not None:
            params["active"] = "true" if active else "false"
        logger.info("fetching_athletes_v3", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_leaders_v3(
        self,
        sport: str,
        league: str,
    ) -> ESPNResponse:
        """Get statistical leaders from v3 API.

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with leaders data
        """
        path = f"/v3/sports/{sport}/{league}/leaders"
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    # --------------------- Team Sub-Resource Endpoints ---------------------

    def get_team_schedule(
        self, sport: str, league: str, team_id: str, season: int | None = None,
    ) -> ESPNResponse:
        """Get a team's schedule, optionally for a historical season."""
        return self.get(
            f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/schedule",
            params={"season": season} if season is not None else None,
        )

    def get_athlete_bio(self, sport: str, league: str, athlete_id: str | int) -> ESPNResponse:
        """Get athlete awards and team history from the Common v3 API."""
        return self.get(
            f"/apis/common/v3/sports/{sport}/{league}/athletes/{athlete_id}/bio",
            domain=ESPNEndpointDomain.WEB_V3,
        )

    def get_team_injuries(
        self,
        sport: str,
        league: str,
        team_id: str,
    ) -> ESPNResponse:
        """Get injury report for a specific team.

        Args:
            sport: Sport slug (e.g., "football", "basketball")
            league: League slug (e.g., "nfl", "nba")
            team_id: ESPN team ID

        Returns:
            ESPNResponse with injury data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/injuries"
        logger.info("fetching_team_injuries", sport=sport, league=league, team_id=team_id)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    def get_team_depth_chart(
        self,
        sport: str,
        league: str,
        team_id: str,
    ) -> ESPNResponse:
        """Get depth chart for a specific team.

        Args:
            sport: Sport slug (e.g., "football", "basketball")
            league: League slug (e.g., "nfl", "nba")
            team_id: ESPN team ID

        Returns:
            ESPNResponse with depth chart data grouped by position
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/depthcharts"
        logger.info("fetching_team_depth_chart", sport=sport, league=league, team_id=team_id)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    def get_team_transactions(
        self,
        sport: str,
        league: str,
        team_id: str,
    ) -> ESPNResponse:
        """Get recent transactions/moves for a specific team.

        Args:
            sport: Sport slug
            league: League slug
            team_id: ESPN team ID

        Returns:
            ESPNResponse with transaction data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/teams/{team_id}/transactions"
        logger.info("fetching_team_transactions", sport=sport, league=league, team_id=team_id)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    # --------------------- Game Situation Endpoints ---------------------

    def get_game_situation(
        self,
        sport: str,
        league: str,
        event_id: str,
        competition_id: str | None = None,
    ) -> ESPNResponse:
        """Get current game situation (down, distance, possession, etc.).

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID
            competition_id: Competition ID (defaults to event_id)

        Returns:
            ESPNResponse with current game situation data
        """
        comp_id = competition_id or event_id
        path = (
            f"/v2/sports/{sport}/leagues/{league}"
            f"/events/{event_id}/competitions/{comp_id}/situation"
        )
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_game_predictor(
        self,
        sport: str,
        league: str,
        event_id: str,
        competition_id: str | None = None,
    ) -> ESPNResponse:
        """Get ESPN game predictor (projected winner/score) for a game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID
            competition_id: Competition ID (defaults to event_id)

        Returns:
            ESPNResponse with predictor data
        """
        comp_id = competition_id or event_id
        path = (
            f"/v2/sports/{sport}/leagues/{league}"
            f"/events/{event_id}/competitions/{comp_id}/predictor"
        )
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    def get_game_broadcasts(
        self,
        sport: str,
        league: str,
        event_id: str,
        competition_id: str | None = None,
    ) -> ESPNResponse:
        """Get broadcast network info for a game.

        Args:
            sport: Sport slug
            league: League slug
            event_id: ESPN event ID
            competition_id: Competition ID (defaults to event_id)

        Returns:
            ESPNResponse with broadcast network data
        """
        comp_id = competition_id or event_id
        path = (
            f"/v2/sports/{sport}/leagues/{league}"
            f"/events/{event_id}/competitions/{comp_id}/broadcasts"
        )
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    # --------------------- Coaches Endpoints ---------------------

    def get_coaches(
        self,
        sport: str,
        league: str,
        season: int | None = None,
        limit: int = 100,
    ) -> ESPNResponse:
        """Get coaching staff for a league season.

        Args:
            sport: Sport slug
            league: League slug
            season: Season year (uses current season if None)
            limit: Maximum coaches to return

        Returns:
            ESPNResponse with coaches data
        """
        if season:
            path = f"/v2/sports/{sport}/leagues/{league}/seasons/{season}/coaches"
        else:
            path = f"/v2/sports/{sport}/leagues/{league}/coaches"
        params: dict[str, Any] = {"limit": limit}
        logger.info("fetching_coaches", sport=sport, league=league, season=season)
        return self.get(path, domain=ESPNEndpointDomain.CORE, params=params)

    def get_coach(
        self,
        sport: str,
        league: str,
        coach_id: str,
    ) -> ESPNResponse:
        """Get a single coach's profile.

        Args:
            sport: Sport slug
            league: League slug
            coach_id: ESPN coach ID

        Returns:
            ESPNResponse with coach data
        """
        path = f"/v2/sports/{sport}/leagues/{league}/coaches/{coach_id}"
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    # --------------------- QBR Endpoint ---------------------

    def get_qbr(
        self,
        league: str,
        season: int,
        season_type: int = 2,
        group: int = 1,
        split: int = 0,
        week: int | None = None,
    ) -> ESPNResponse:
        """Get ESPN Total Quarterback Rating (QBR) data.

        Only applicable to football leagues (nfl, college-football).

        Args:
            league: League slug ("nfl" or "college-football")
            season: Season year (e.g., 2024)
            season_type: 1=pre, 2=regular, 3=post
            group: Conference group ID (1=NFL, 80=FBS for NCAAF)
            split: 0=totals, 1=home, 2=away
            week: Optional week number (returns weekly QBR if provided)

        Returns:
            ESPNResponse with QBR data
        """
        if week is not None:
            path = (
                f"/v2/sports/football/leagues/{league}"
                f"/seasons/{season}/types/{season_type}/weeks/{week}/qbr/{split}"
            )
        else:
            path = (
                f"/v2/sports/football/leagues/{league}"
                f"/seasons/{season}/types/{season_type}/groups/{group}/qbr/{split}"
            )
        logger.info("fetching_qbr", league=league, season=season, week=week)
        return self.get(path, domain=ESPNEndpointDomain.CORE)

    # --------------------- Power Index Endpoint ---------------------

    def get_power_index(
        self,
        sport: str,
        league: str,
        season: int,
        team_id: str | None = None,
    ) -> ESPNResponse:
        """Get ESPN Power Index (BPI/SP+/FPI) data.

        Args:
            sport: Sport slug
            league: League slug
            season: Season year
            team_id: Optional team ID (returns league-wide data if None)

        Returns:
            ESPNResponse with power index data
        """
        if team_id:
            path = (
                f"/v2/sports/{sport}/leagues/{league}"
                f"/seasons/{season}/powerindex/{team_id}"
            )
        else:
            path = f"/v2/sports/{sport}/leagues/{league}/seasons/{season}/powerindex"
        logger.info("fetching_power_index", sport=sport, league=league, season=season)
        return self.get(path, domain=ESPNEndpointDomain.CORE)



    # --------------------- League-wide Site API Endpoints ---------------------

    def get_league_injuries(
        self,
        sport: str,
        league: str,
    ) -> ESPNResponse:
        """Get league-wide injury report (all teams).

        Not supported for MMA, Tennis, Golf (returns 500).

        Args:
            sport: Sport slug (e.g., "basketball", "football")
            league: League slug (e.g., "nba", "nfl")

        Returns:
            ESPNResponse with injuries grouped by team
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/injuries"
        logger.info("fetching_league_injuries", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    def get_league_transactions(
        self,
        sport: str,
        league: str,
    ) -> ESPNResponse:
        """Get recent league-wide transactions (signings, trades, waivers).

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with transaction data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/transactions"
        logger.info("fetching_league_transactions", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    def get_groups(
        self,
        sport: str,
        league: str,
    ) -> ESPNResponse:
        """Get conference/division groups for a league.

        Args:
            sport: Sport slug
            league: League slug

        Returns:
            ESPNResponse with group/conference data
        """
        path = f"/apis/site/v2/sports/{sport}/{league}/groups"
        logger.info("fetching_groups", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.SITE)

    # --------------------- common/v3 Athlete Endpoints ---------------------

    def get_athlete_overview(
        self,
        sport: str,
        league: str,
        athlete_id: str | int,
    ) -> ESPNResponse:
        """Get athlete overview (stats snapshot, next game, rotowire notes, news).

        Uses site.web.api.espn.com/apis/common/v3/. Confirmed working for:
        NFL, NBA, NHL, MLB. Soccer returns minimal data.

        Args:
            sport: Sport slug
            league: League slug
            athlete_id: ESPN athlete ID

        Returns:
            ESPNResponse with overview data
        """
        path = f"/apis/common/v3/sports/{sport}/{league}/athletes/{athlete_id}/overview"
        logger.info("fetching_athlete_overview", sport=sport, league=league, athlete_id=athlete_id)
        return self.get(path, domain=ESPNEndpointDomain.WEB_V3)

    def get_athlete_stats(
        self,
        sport: str,
        league: str,
        athlete_id: str | int,
        season: int | None = None,
        season_type: int | None = None,
    ) -> ESPNResponse:
        """Get season stats for an athlete.

        Uses site.web.api.espn.com/apis/common/v3/. Confirmed working for:
        NFL, NBA, NHL, MLB. Returns 404 for Soccer.

        Args:
            sport: Sport slug
            league: League slug
            athlete_id: ESPN athlete ID
            season: Season year (optional)
            season_type: 1=pre, 2=regular, 3=post (optional)

        Returns:
            ESPNResponse with stats (filters, teams, categories, glossary)
        """
        path = f"/apis/common/v3/sports/{sport}/{league}/athletes/{athlete_id}/stats"
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        if season_type:
            params["seasontype"] = season_type
        logger.info("fetching_athlete_stats", sport=sport, league=league, athlete_id=athlete_id)
        return self.get(path, domain=ESPNEndpointDomain.WEB_V3, params=params)

    def get_athlete_gamelog(
        self,
        sport: str,
        league: str,
        athlete_id: str | int,
        season: int | None = None,
    ) -> ESPNResponse:
        """Get game-by-game log for an athlete.

        Uses site.web.api.espn.com/apis/common/v3/. Confirmed working for:
        NFL, NBA, MLB. Returns 404 for NHL, 400 for Soccer.

        Args:
            sport: Sport slug
            league: League slug
            athlete_id: ESPN athlete ID
            season: Season year (optional)

        Returns:
            ESPNResponse with events/gamelog data
        """
        path = f"/apis/common/v3/sports/{sport}/{league}/athletes/{athlete_id}/gamelog"
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        logger.info("fetching_athlete_gamelog", sport=sport, league=league, athlete_id=athlete_id)
        return self.get(path, domain=ESPNEndpointDomain.WEB_V3, params=params)

    def get_athlete_splits(
        self,
        sport: str,
        league: str,
        athlete_id: str | int,
        season: int | None = None,
        season_type: int | None = None,
    ) -> ESPNResponse:
        """Get home/away/opponent splits for an athlete.

        Uses site.web.api.espn.com/apis/common/v3/. Confirmed working for:
        NFL, NBA, NHL, MLB. Not available for Soccer.

        Args:
            sport: Sport slug
            league: League slug
            athlete_id: ESPN athlete ID
            season: Season year (optional)
            season_type: 1=pre, 2=regular, 3=post (optional)

        Returns:
            ESPNResponse with splits by category (home/away/opponent)
        """
        path = f"/apis/common/v3/sports/{sport}/{league}/athletes/{athlete_id}/splits"
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        if season_type:
            params["seasontype"] = season_type
        logger.info("fetching_athlete_splits", sport=sport, league=league, athlete_id=athlete_id)
        return self.get(path, domain=ESPNEndpointDomain.WEB_V3, params=params)

    def get_statistics_by_athlete(
        self,
        sport: str,
        league: str,
        season: int | None = None,
        season_type: int | None = None,
        category: str | None = None,
        sort: str | None = None,
        limit: int = 50,
        page: int = 1,
    ) -> ESPNResponse:
        """Get ranked statistics leaderboard across all athletes.

        Uses site.web.api.espn.com/apis/common/v3/. Confirmed working for:
        NBA, NFL, NHL, MLB.

        Args:
            sport: Sport slug
            league: League slug
            season: Season year (optional)
            season_type: 1=pre, 2=regular, 3=post (optional)
            category: Stat category (e.g., "batting" for MLB, "passing" for NFL)
            sort: Sort field (e.g., "batting.homeRuns:desc")
            limit: Athletes per page
            page: Page number

        Returns:
            ESPNResponse with ranked athlete statistics
        """
        path = f"/apis/common/v3/sports/{sport}/{league}/statistics/byathlete"
        params: dict[str, Any] = {"limit": limit, "page": page}
        if season:
            params["season"] = season
        if season_type:
            params["seasontype"] = season_type
        if category:
            params["category"] = category
        if sort:
            params["sort"] = sort
        logger.info("fetching_statistics_by_athlete", sport=sport, league=league)
        return self.get(path, domain=ESPNEndpointDomain.WEB_V3, params=params)

    # --------------------- CDN Game Data Endpoints ---------------------

    def get_cdn_game(
        self,
        sport: str,
        game_id: str,
        view: str = "game",
    ) -> ESPNResponse:
        """Get full game package from cdn.espn.com.

        Returns a rich gamepackageJSON object containing drives, plays,
        scoring summary, win probability, boxscore, betting odds, and more.
        Requires ?xhr=1 (automatically added).

        Confirmed working for: nfl, nba, mlb, college-football.
        Soccer: use get_cdn_soccer_scoreboard() with a league param.

        Args:
            sport: ESPN CDN sport slug (e.g., "nfl", "nba", "mlb",
                   "college-football")
            game_id: ESPN event/game ID
            view: One of "game" (full), "boxscore", "playbyplay", "matchup"

        Returns:
            ESPNResponse containing gamepackageJSON key with all game data
        """
        path = f"/core/{sport}/{view}"
        params: dict[str, Any] = {"xhr": 1, "gameId": game_id}
        logger.info("fetching_cdn_game", sport=sport, game_id=game_id, view=view)
        return self.get(path, domain=ESPNEndpointDomain.CDN, params=params)

    def get_cdn_scoreboard(
        self,
        sport: str,
        league: str | None = None,
    ) -> ESPNResponse:
        """Get scoreboard via CDN domain.

        Args:
            sport: ESPN CDN sport slug (e.g., "nfl", "nba", "mlb",
                   "college-football", "soccer")
            league: League slug — only needed for soccer (e.g., "eng.1")

        Returns:
            ESPNResponse with scoreboard data
        """
        path = f"/core/{sport}/scoreboard"
        params: dict[str, Any] = {"xhr": 1}
        if league:
            params["league"] = league
        logger.info("fetching_cdn_scoreboard", sport=sport)
        return self.get(path, domain=ESPNEndpointDomain.CDN, params=params)

    # --------------------- Now/News Endpoints ---------------------

    def get_now_news(
        self,
        sport: str | None = None,
        league: str | None = None,
        team: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ESPNResponse:
        """Get real-time news from now.core.api.espn.com.

        Supports filtering by sport, league, or team. Returns a feed of
        articles with categories, images, and publication timestamps.

        Args:
            sport: Sport filter (e.g., "football", "basketball")
            league: League filter (e.g., "nfl", "nba")
            team: Team abbreviation filter (e.g., "dal", "gsw")
            limit: Number of articles (max 50)
            offset: Pagination offset

        Returns:
            ESPNResponse with resultsCount, resultsLimit, feed[]
        """
        path = "/v1/sports/news"
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if sport:
            params["sport"] = sport
        if league:
            params["league"] = league
        if team:
            params["team"] = team
        logger.info("fetching_now_news", sport=sport, league=league, team=team)
        return self.get(path, domain=ESPNEndpointDomain.NOW, params=params)


    # Additional discovery and event resources verified in the September audit.

    def get_core_event(self, sport: str, league: str, event_id: str) -> ESPNResponse:
        """Core event metadata and references; get_event() returns the Site summary."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}", domain=ESPNEndpointDomain.CORE)

    def get_competition(self, sport: str, league: str, event_id: str, competition_id: str) -> ESPNResponse:
        """Competition metadata; event and competition IDs need not be equal."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{competition_id}", domain=ESPNEndpointDomain.CORE)

    def get_competition_status(self, sport: str, league: str, event_id: str, competition_id: str) -> ESPNResponse:
        """Resolve the competition status reference."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{competition_id}/status", domain=ESPNEndpointDomain.CORE)

    def get_competitor_roster(self, sport: str, league: str, event_id: str, competition_id: str, competitor_id: str, page: int = 1, limit: int = 100) -> ESPNResponse:
        """Game roster (often entries rather than items); paging support varies."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{competition_id}/competitors/{competitor_id}/roster", domain=ESPNEndpointDomain.CORE, params={"page": page, "limit": limit})

    def get_competitor_statistics(self, sport: str, league: str, event_id: str, competition_id: str, competitor_id: str) -> ESPNResponse:
        """Game statistics for one competitor."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{competition_id}/competitors/{competitor_id}/statistics", domain=ESPNEndpointDomain.CORE)

    def get_competitor_linescores(self, sport: str, league: str, event_id: str, competition_id: str, competitor_id: str) -> ESPNResponse:
        """Period/inning scores for one competitor."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{competition_id}/competitors/{competitor_id}/linescores", domain=ESPNEndpointDomain.CORE)

    def get_drives(self, sport: str, league: str, event_id: str, competition_id: str, page: int = 1, limit: int = 100) -> ESPNResponse:
        """Football drive references; follow each drive's plays for detail."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/events/{event_id}/competitions/{competition_id}/drives", domain=ESPNEndpointDomain.CORE, params={"page": page, "limit": limit})

    def get_athlete_eventlog(self, sport: str, league: str, athlete_id: str, season: int | None = None) -> ESPNResponse:
        """Core athlete event participation references."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/athletes/{athlete_id}/eventlog", domain=ESPNEndpointDomain.CORE, params={"season": season} if season else None)

    def get_athlete_statisticslog(self, sport: str, league: str, athlete_id: str) -> ESPNResponse:
        """References to available athlete statistics by season/type."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/athletes/{athlete_id}/statisticslog", domain=ESPNEndpointDomain.CORE)

    def get_calendar(self, sport: str, league: str) -> ESPNResponse:
        """Core calendar; Site v2 calendar is not interchangeable."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/calendar", domain=ESPNEndpointDomain.CORE)

    def get_season_types(self, sport: str, league: str, season: int) -> ESPNResponse:
        """Discover supported season types rather than assuming all four exist."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/seasons/{season}/types", domain=ESPNEndpointDomain.CORE)

    def get_season_weeks(self, sport: str, league: str, season: int, season_type: int = 2) -> ESPNResponse:
        """Weeks for a season type (primarily football)."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/seasons/{season}/types/{season_type}/weeks", domain=ESPNEndpointDomain.CORE)

    def get_providers(self, sport: str, league: str, page: int = 1, limit: int = 100) -> ESPNResponse:
        """Discover odds providers instead of relying on stale hard-coded IDs."""
        return self.get(f"/v2/sports/{sport}/leagues/{league}/providers", domain=ESPNEndpointDomain.CORE, params={"page": page, "limit": limit})

    def search(self, query: str, limit: int = 10) -> ESPNResponse:
        """Global ESPN search; query values are encoded by httpx."""
        return self.get("/apis/search/v2", domain=ESPNEndpointDomain.WEB_V3, params={"query": query, "limit": limit})

    def get_personalized_scoreboard(self, sport: str, region: str = "us", timezone: str = "UTC") -> ESPNResponse:
        """Header leagues/events, useful for cricket series discovery."""
        return self.get("/apis/personalized/v2/scoreboard/header", params={"sport": sport, "region": region, "tz": timezone})

    def get_cricket_summary(self, league_id: str, event_id: str, region: str = "in") -> ESPNResponse:
        """Cricket scorecard on the Web Site API (numeric league ID)."""
        return self.get(f"/apis/site/v2/sports/cricket/{league_id}/summary", domain=ESPNEndpointDomain.WEB_V3, params={"event": event_id, "lang": "en", "region": region})

    def get_golf_player_summary(self, tour: str, event_id: str, player_id: str, season: int) -> ESPNResponse:
        """Golf hole-by-hole round data from the Web Site API."""
        return self.get(f"/apis/site/v2/sports/golf/{tour}/leaderboard/{event_id}/playersummary", domain=ESPNEndpointDomain.WEB_V3, params={"season": season, "player": player_id})


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

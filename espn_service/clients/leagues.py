"""Curated league scope for periodic ingestion."""

# Curated ingestion scope, shared by CLI and Celery; discovery includes historical leagues.
ALL_LEAGUES = [
    # Football
    ("football", "nfl"),
    ("football", "college-football"),
    ("football", "cfl"),
    ("football", "ufl"),
    ("football", "xfl"),
    # Basketball
    ("basketball", "nba"),
    ("basketball", "wnba"),
    ("basketball", "mens-college-basketball"),
    ("basketball", "womens-college-basketball"),
    ("basketball", "nba-development"),
    ("basketball", "nbl"),
    # Baseball
    ("baseball", "mlb"),
    ("baseball", "college-baseball"),
    # Hockey
    ("hockey", "nhl"),
    ("hockey", "mens-college-hockey"),
    ("hockey", "womens-college-hockey"),
    # Soccer — top leagues + major competitions
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
    ("soccer", "eng.2"),
    # MMA
    ("mma", "ufc"),
    ("mma", "bellator"),
    # Golf
    ("golf", "pga"),
    ("golf", "lpga"),
    ("golf", "liv"),
    ("golf", "eur"),
    # Tennis
    ("tennis", "atp"),
    ("tennis", "wta"),
    # Racing
    ("racing", "f1"),
    ("racing", "irl"),
    ("racing", "nascar-premier"),
    ("racing", "nascar-secondary"),
    ("racing", "nascar-truck"),
    # Rugby Union (numeric IDs)
    ("rugby", "164205"),   # Rugby World Cup
    ("rugby", "180659"),   # Six Nations
    ("rugby", "267979"),   # Gallagher Premiership
    ("rugby", "242041"),   # Super Rugby Pacific
    ("rugby", "289262"),   # Major League Rugby
    # Rugby League
    ("rugby-league", "3"),
    # Lacrosse
    ("lacrosse", "pll"),
    ("lacrosse", "nll"),
    ("lacrosse", "mens-college-lacrosse"),
    ("lacrosse", "womens-college-lacrosse"),
    # Australian Football
    ("australian-football", "afl"),
]

"""Validation for bounded, inclusive scoreboard date queries."""

import re
from datetime import datetime, timedelta


def scoreboard_dates(value: str) -> list[str]:
    """Expand a calendar date or an inclusive range of at most 31 days."""
    if not re.fullmatch(r"[0-9]{8}(?:-[0-9]{8})?", value):
        raise ValueError("Date must be YYYYMMDD or YYYYMMDD-YYYYMMDD")
    parts = value.split("-")
    start = datetime.strptime(parts[0], "%Y%m%d").date()
    end = datetime.strptime(parts[-1], "%Y%m%d").date()
    count = (end - start).days + 1
    if not 1 <= count <= 31:
        raise ValueError("Date range must be ordered and contain at most 31 days")
    return [(start + timedelta(days=offset)).strftime("%Y%m%d") for offset in range(count)]

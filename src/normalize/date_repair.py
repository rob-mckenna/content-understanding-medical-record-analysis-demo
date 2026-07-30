"""Detect and repair invalid dates from OCR output.

Medical records frequently contain dates like `6/78/0047` — clearly OCR
corruption. This module classifies each date into:

    * valid            -> parseable and within a plausible clinical range
    * suspicious       -> parseable but implausible (future dates, year < 1900)
    * unrepairable     -> cannot be parsed; must be surfaced for human review

Never silently coerce a bad date to `None` or `today()`. Always flag.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

Status = Literal["valid", "suspicious", "unrepairable"]

MIN_YEAR = 1900
MAX_YEAR = date.today().year + 1


@dataclass
class DateResult:
    original: str
    parsed: date | None
    status: Status
    reason: str | None = None


def repair(text: str) -> DateResult:
    """Best-effort parse; flag anything implausible."""
    text = text.strip()
    if not text:
        return DateResult(text, None, "unrepairable", "empty")

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y", "%d %b %Y"):
        try:
            parsed = datetime.strptime(text, fmt).date()
        except ValueError:
            continue
        if parsed.year < MIN_YEAR or parsed.year > MAX_YEAR:
            return DateResult(text, parsed, "suspicious", f"year {parsed.year} out of range")
        return DateResult(text, parsed, "valid")

    return DateResult(text, None, "unrepairable", "no format matched")

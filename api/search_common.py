"""Shared constants and helpers for the search API modules."""

import re

MIN_SCORE_THRESHOLD = 80

_ROOT_PREFIX_RE = r"^([a-gA-G][#b]?)\s"


def extract_root_note(query: str) -> str | None:
    """Return the canonical root note at the start of a query, or None."""
    root_match = re.search(_ROOT_PREFIX_RE, query)
    if root_match:
        return root_match.group(1).capitalize().replace("♯", "#").replace("♭", "b")
    return None

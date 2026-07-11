"""
filters.py

Handles keyword matching against scraped items.

This is deliberately separated from the sources (hackernews.py, etc.)
so that ANY source can reuse the same filtering logic — the filter
doesn't care where the item came from, only what its title says.
"""

import re


def build_keyword_pattern(keywords: list[str]) -> re.Pattern:
    """
    Turns a list of plain keywords (e.g. ["python", "ai"]) into a
    single compiled regex pattern that matches WHOLE WORDS only.

    This fixes the old bug where 'ai' matched inside "snails",
    "daily", "curtail", etc. \b means "word boundary" — it makes
    sure 'ai' only matches when it's a standalone word, not buried
    inside another word.
    """
    # Escape each keyword in case it contains special regex characters,
    # then join them with OR ( | ) so the pattern matches ANY of them.
    escaped = [re.escape(word) for word in keywords]
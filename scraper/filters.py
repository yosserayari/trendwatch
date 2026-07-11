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
    "daily", "curtail", etc. \\b means "word boundary" — it makes
    sure 'ai' only matches when it's a standalone word, not buried
    inside another word.
    """
    escaped = [re.escape(word) for word in keywords]
    pattern_string = r'\b(' + '|'.join(escaped) + r')\b'
    return re.compile(pattern_string, re.IGNORECASE)


def strip_source_suffix(title: str) -> str:
    """
    Removes a trailing "(source.com)" from a title before matching.

    Why: titles look like "Some Article (example.com)" — without
    this, a domain name like "dailymail.com" could accidentally
    contain a keyword and cause a false match.
    """
    return re.sub(r'\s*\([^)]*\)\s*$', '', title)


def filter_items(items: list[dict], keywords: list[str]) -> list[dict]:
    """
    Takes a list of standardized items (from any source) and returns
    only the ones whose title matches one of the given keywords.
    """
    pattern = build_keyword_pattern(keywords)

    matched = []
    for item in items:
        clean_title = strip_source_suffix(item["title"])
        if pattern.search(clean_title):
            matched.append(item)

    return matched

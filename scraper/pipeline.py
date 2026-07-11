"""
pipeline.py

The orchestrator. This file doesn't scrape or filter anything itself —
it just calls the right pieces in the right order:

    1. Load settings from config.yml (keywords, which sources to use)
    2. Ask each source for its items (fetch + parse)
    3. Filter those items by keyword
    4. Remove duplicates already seen before
    5. Append new matches to storage/history.csv, with a timestamp

Keeping this separate from the sources/filters means you can change
the ORDER or ADD steps (like alerts) here, without touching the
scraping or filtering logic itself.
"""

import csv
import os
from datetime import datetime, timezone

import yaml

from scraper.sources.hackernews import HackerNewsSource
from scraper.filters import filter_items

HISTORY_PATH = "storage/history.csv"
HISTORY_FIELDS = ["date_scraped", "source", "title", "url"]

# Maps a name used in config.yml to the actual Python class.
# When you add Reddit later, you just add one line here.
AVAILABLE_SOURCES = {
    "hackernews": HackerNewsSource,
}


def load_config(path: str = "config.yml") -> dict:
    """Reads keywords and enabled sources from config.yml."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_existing_urls() -> set[str]:
    """
    Reads storage/history.csv (if it exists) and returns the set of
    URLs already recorded, so we never save the same story twice.
    """
    if not os.path.exists(HISTORY_PATH):
        return set()

    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["url"] for row in reader}


def append_to_history(new_items: list[dict]) -> None:
    """
    Adds new matched items to history.csv, stamping each with the
    current UTC date/time. Creates the file with headers if it
    doesn't exist yet.
    """
    file_exists = os.path.exists(HISTORY_PATH)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with open(HISTORY_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
        if not file_exists:
            writer.writeheader()

        for item in new_items:
            writer.writerow({
                "date_scraped": timestamp,
                "source": item["source"],
                "title": item["title"],
                "url": item["url"],
            })


def run_pipeline() -> list[dict]:
    """
    Runs the full pipeline once. Returns the list of NEW items
    found this run (useful later for sending alerts on just the
    new ones, not everything).
    """
    config = load_config()
    keywords = config["keywords"]
    enabled_source_names = config["sources"]

    already_seen = load_existing_urls()
    all_new_items = []

    for source_name in enabled_source_names:
        source_class = AVAILABLE_SOURCES[source_name]
        source = source_class()

        raw_items = source.get_items()
        matched_items = filter_items(raw_items, keywords)

        # Only keep items we haven't already saved before.
        new_items = [item for item in matched_items if item["url"] not in already_seen]
        all_new_items.extend(new_items)

    if all_new_items:
        append_to_history(all_new_items)

    return all_new_items


if __name__ == "__main__":
    found = run_pipeline()
    print(f"Pipeline complete. {len(found)} new matching stories found.")
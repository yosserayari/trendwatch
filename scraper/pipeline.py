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


def load_config(path: str = "storage/config.yml") -> dict:
    """
    Reads keywords and enabled sources from config.yml.
    FIX: Changed default path to 'storage/config.yml' to match your structure.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_existing_urls() -> set[str]:
    """
    Reads storage/history.csv (if it exists) and returns the set of
    URLs already recorded, so we never save the same story twice.
    
    FIX: Handles both 'url' and 'URL' column names.
    """
    if not os.path.exists(HISTORY_PATH):
        return set()

    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Check if the file has the expected columns
            if not reader.fieldnames:
                print(f"⚠️ {HISTORY_PATH} is empty or has no headers")
                return set()
            
            # Find the URL column (case-insensitive)
            url_column = None
            for col in reader.fieldnames:
                if col.lower() == 'url':
                    url_column = col
                    break
            
            if url_column is None:
                print(f"⚠️ No 'url' column found in {HISTORY_PATH}")
                print(f"   Available columns: {reader.fieldnames}")
                print(f"   Will recreate the file with correct headers")
                # Rename the file as backup and recreate
                backup_path = HISTORY_PATH + ".backup"
                os.rename(HISTORY_PATH, backup_path)
                print(f"📦 Old file backed up to: {backup_path}")
                return set()
            
            # Get all URLs (skip empty ones)
            urls = {row[url_column] for row in reader if row.get(url_column)}
            print(f"📊 Loaded {len(urls)} existing URLs from history")
            return urls
            
    except Exception as e:
        print(f"❌ Error reading history file: {e}")
        print("   Starting with empty history")
        return set()


def append_to_history(new_items: list[dict]) -> None:
    """
    Adds new matched items to history.csv, stamping each with the
    current UTC date/time. Creates the file with headers if it
    doesn't exist yet.
    
    FIX: Added better error handling and file creation.
    """
    # Ensure the storage directory exists
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    
    file_exists = os.path.exists(HISTORY_PATH)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(HISTORY_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
            if not file_exists:
                writer.writeheader()
                print(f"📁 Created new history file: {HISTORY_PATH}")

            for item in new_items:
                writer.writerow({
                    "date_scraped": timestamp,
                    "source": item["source"],
                    "title": item["title"],
                    "url": item["url"],
                })
            print(f"✅ Added {len(new_items)} new items to history")
            
    except Exception as e:
        print(f"❌ Error writing to history: {e}")


def run_pipeline() -> list[dict]:
    """
    Runs the full pipeline once. Returns the list of NEW items
    found this run (useful later for sending alerts on just the
    new ones, not everything).
    
    FIX: Added better error handling for missing config.
    """
    try:
        config = load_config()
        keywords = config.get("keywords", [])
        enabled_source_names = config.get("sources", [])
        
        if not keywords:
            print("⚠️ No keywords found in config.yml")
            return []
        
        if not enabled_source_names:
            print("⚠️ No sources enabled in config.yml")
            return []
            
    except FileNotFoundError:
        print("❌ config.yml not found in storage/ directory")
        print("   Creating default config.yml...")
        create_default_config()
        return []
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return []

    already_seen = load_existing_urls()
    all_new_items = []

    for source_name in enabled_source_names:
        try:
            source_class = AVAILABLE_SOURCES.get(source_name)
            if not source_class:
                print(f"⚠️ Unknown source: {source_name}")
                continue
                
            source = source_class()
            raw_items = source.get_items()
            
            if not raw_items:
                print(f"ℹ️ No items from {source_name}")
                continue
                
            matched_items = filter_items(raw_items, keywords)
            print(f"🔍 {source_name}: {len(matched_items)} matched keywords")

            # Only keep items we haven't already saved before.
            new_items = [item for item in matched_items if item["url"] not in already_seen]
            all_new_items.extend(new_items)
            
            if new_items:
                print(f"🆕 {source_name}: {len(new_items)} new items found")
                
        except Exception as e:
            print(f"❌ Error processing source {source_name}: {e}")

    if all_new_items:
        append_to_history(all_new_items)

    return all_new_items


def create_default_config():
    """Create a default config.yml file if missing"""
    import yaml
    
    default_config = {
        "keywords": ["python", "ai", "openai", "chatgpt", "machine learning", "llm"],
        "sources": ["hackernews"],
        "alerts": {
            "discord": {"enabled": False, "webhook_url": ""},
            "email": {"enabled": False, "to": "", "smtp": ""}
        }
    }
    
    os.makedirs("storage", exist_ok=True)
    with open("storage/config.yml", "w", encoding="utf-8") as f:
        yaml.dump(default_config, f, default_flow_style=False)
    print("✅ Created default config.yml in storage/")


if __name__ == "__main__":
    found = run_pipeline()
    print(f"\n{'='*50}")
    print(f"✅ Pipeline complete. {len(found)} new matching stories found.")
    print(f"{'='*50}")
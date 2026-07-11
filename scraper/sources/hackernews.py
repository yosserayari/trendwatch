"""
hackernews.py

The concrete Hacker News source. This is where we implement the
two methods that base.py demands: fetch() and parse().

Anyone reading this file later (including a client) should be able
to tell exactly how HN data becomes standardized items.
"""

import requests
from bs4 import BeautifulSoup
from scraper.sources.base import BaseSource


class HackerNewsSource(BaseSource):
    """Scrapes the Hacker News front page."""

    name = "hackernews"
    URL = "https://news.ycombinator.com/"

    def fetch(self) -> str:
        """
        Downloads the raw HTML of the Hacker News front page.
        Raises an error if the request fails (e.g. site is down),
        so the pipeline can catch and log it instead of silently
        continuing with no data.
        """
        response = requests.get(self.URL, timeout=10)
        response.raise_for_status()
        return response.text

    def parse(self, raw_content: str) -> list[dict]:
        """
        Takes the raw HTML and extracts a clean list of stories.
        Every returned item follows the standard shape required
        by base.py: title, url, source.
        """
        soup = BeautifulSoup(raw_content, "html.parser")
        story_spans = soup.find_all("span", class_="titleline")

        items = []
        for span in story_spans:
            link_tag = span.find("a")
            if not link_tag:
                continue

            items.append({
                "title": span.get_text(),
                "url": link_tag["href"],
                "source": self.name,
            })

        return items
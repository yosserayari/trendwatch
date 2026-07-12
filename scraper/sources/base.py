"""
base.py

Defines the common interface every scraper source must follow.
This means the rest of the app (pipeline.py) can work with ANY
source the same way, without knowing its specific scraping details.

Think of this as a "contract": if you build a new source (Reddit,
a competitor's site, etc.), it must implement these two methods.
"""

from abc import ABC, abstractmethod


class BaseSource(ABC):
    """
    Abstract base class for a data source.

    'Abstract' means this class can never be used directly —
    it only exists to define what subclasses MUST implement.
    """

    # A short, human-readable name for this source (used in logs/reports)
    name: str = "base"

    @abstractmethod
    def fetch(self) -> str:
        """
        Fetch raw data from the source (e.g., an HTTP GET request).
        Must return the raw content as a string (usually HTML or JSON text).
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw_content: str) -> list[dict]:
        """
        Parse the raw content into a list of standardized items.

        Every item MUST be a dict with at least these keys:
            - "title": str
            - "url": str
            - "source": str  (should match self.name)

        This standardized shape is what lets filters.py and
        pipeline.py treat HN, Reddit, etc. identically.
        """
        raise NotImplementedError

    def get_items(self) -> list[dict]:
        """
        Convenience method: fetch + parse in one call.
        Subclasses normally don't need to override this —
        they just implement fetch() and parse() above.
        
        Added error handling to prevent pipeline crashes.
        """
        try:
            raw_content = self.fetch()
            return self.parse(raw_content)
        except Exception as e:
            print(f"❌ Error getting items from {self.name}: {e}")
            return []
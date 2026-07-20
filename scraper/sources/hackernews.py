import requests
from bs4 import BeautifulSoup
from scraper.sources.base import BaseSource
from scraper.retry import with_retry


class HackerNewsSource(BaseSource):
    """Scrapes the Hacker News front page."""

    name = "hackernews"
    URL = "https://news.ycombinator.com/"
    BASE_URL = "https://news.ycombinator.com/"

    def fetch(self) -> str:
        """
        Downloads the raw HTML of the Hacker News front page.
        Raises an error if the request fails (e.g. site is down),
        so the pipeline can catch and log it instead of silently
        continuing with no data.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(self.URL, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {self.URL}: {e}")
            raise

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
            try:
                link_tag = span.find("a")
                if not link_tag:
                    continue

                title = span.get_text(strip=True)
                href = link_tag.get("href")
                url = href if isinstance(href, str) else ""

                # Handle relative URLs (e.g., "item?id=12345")
                if url and url.startswith("item?"):
                    url = f"{self.BASE_URL}{url}"
                elif url and url.startswith("from?site="):
                    # Handle external links that go through HN's redirect
                    # Example: "from?site=github.com"
                    # We'll keep the original link from the href
                    url = f"{self.BASE_URL}{url}"
                elif url and not url.startswith("http"):
                    # Handle any other relative URLs
                    url = f"{self.BASE_URL}{url}"
                
                # Skip empty titles or URLs
                if not title or not url:
                    continue
                
                items.append({
                    "title": title,
                    "url": url,
                    "source": self.name,
                })
                
            except Exception as e:
                print(f"⚠️ Error parsing story: {e}")
                continue

        print(f"📊 Parsed {len(items)} stories from Hacker News")
        return items

    def get_items(self) -> list[dict]:
        """
        The main method called by the pipeline.
        Fetches the page and parses it into standardized items.
        """
        try:
            raw_content = self.fetch()
            return self.parse(raw_content)
        except Exception as e:
            print(f"❌ Failed to get items from {self.name}: {e}")
            return []
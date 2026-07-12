"""
Sources package - Data source implementations
"""
from scraper.sources.base import BaseSource
from scraper.sources.hackernews import HackerNewsSource

__all__ = ['BaseSource', 'HackerNewsSource']
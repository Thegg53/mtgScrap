"""mtgscrap.utils - Utilities for Legacy decklist scraping."""
# Re-export from submodules for convenience
from mtgscrap.utils.core import ParsingError, extract_int, seconds2readable, timed
from mtgscrap.utils.scraping import (
    ScrapingError,
    fetch,
    fetch_soup,
    fetch_throttled_soup,
    http_requests_counted,
)

__all__ = [
    "ParsingError",
    "extract_int",
    "seconds2readable",
    "timed",
    "ScrapingError",
    "fetch",
    "fetch_soup",
    "fetch_throttled_soup",
    "http_requests_counted",
]

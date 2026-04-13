"""Scraping utilities for MTGGoldfish."""
import logging
import random
import time
from functools import wraps
from typing import Callable, Type

import requests
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
from requests import Response
from requests.exceptions import HTTPError

from mtgscrap import Json
from mtgscrap.utils.core import timed
from mtgscrap.utils.check_type import type_checker

_log = logging.getLogger(__name__)
REQUESTS_TIMEOUT = 15.0  # seconds
DEFAULT_THROTTLING = 1.0  # seconds


class ScrapingError(OSError):
    """Raised whenever scraping produces unexpected results."""
    @property
    def scraper(self) -> Type | None:
        return self._scraper

    @property
    def url(self) -> str | None:
        return self._url

    def __init__(
            self, message="No page soup", scraper: Type | None = None, url: str | None = None) -> None:
        self._scraper, self._url = scraper, url
        scraper = scraper.__name__ if scraper else ""
        details = [item for item in (scraper, url) if item]
        if details:
            message += f" [{', '.join(details)}]"
        super().__init__(message)


_http_requests_count = 0


@timed("fetching")
@type_checker(str)
def fetch(
        url: str, postdata: Json | None = None, handle_http_errors=True,
        request_timeout=REQUESTS_TIMEOUT,
        **requests_kwargs) -> Response | None:
    """Do a GET (or POST with postdata) HTTP request for url and return the response (or None)."""
    _log.info(f"Fetching: '{url}'...")
    global _http_requests_count
    if postdata:
        response = requests.post(url, json=postdata, **requests_kwargs)
    else:
        response = requests.get(url, timeout=request_timeout, **requests_kwargs)
    _http_requests_count += 1
    if handle_http_errors:
        if str(response.status_code)[0] in ("4", "5"):
            msg = f"Request for '{url}' failed with: '{response.status_code} {response.reason}'"
            if response.status_code in (502, 503, 504):
                raise HTTPError(msg)
            _log.warning(msg)
            return None
    return response


@type_checker(str)
def fetch_soup(
        url: str, headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        request_timeout=REQUESTS_TIMEOUT) -> BeautifulSoup | None:
    """Do a GET HTTP request for url and return a BeautifulSoup object (or None).

    Args:
        url: URL string
        headers: a dictionary of headers to add to the request
        params: URL's query parameters (if not already present in the URL)
        request_timeout: request timeout in seconds

    Returns:
        a BeautifulSoup object or None on client-side errors
    """
    response = fetch(url, headers=headers, params=params, request_timeout=request_timeout)
    if not response or not response.text:
        return None
    http_encoding = response.encoding if 'charset' in response.headers.get(
        'content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(response.content, is_html=True)
    encoding = html_encoding or http_encoding
    return BeautifulSoup(response.content, "lxml", from_encoding=encoding)


def throttle(delay: float, offset=0.0) -> None:
    """Sleep for delay seconds with optional randomization."""
    if offset:
        delay = round(random.uniform(delay - offset / 2, delay + offset / 2), 3)
    _log.info(f"Throttling for {delay} seconds...")
    time.sleep(delay)


def throttled(delay: float, offset=0.0) -> Callable:
    """Add throttling delay after the decorated operation.

    Args:
        delay: throttling delay in fraction of seconds
        offset: randomization offset of the delay in fraction of seconds

    Returns:
        the decorated function
    """
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            throttle(delay, offset)
            return result
        return wrapper
    return decorate


@throttled(DEFAULT_THROTTLING)
def fetch_throttled_soup(url: str, headers: dict[str, str] | None = None) -> BeautifulSoup | None:
    """Fetch BeautifulSoup with throttling delay after."""
    return fetch_soup(url, headers=headers)


def http_requests_counted(operation="") -> Callable:
    """Count HTTP requests done by the decorated operation.

    Args:
        operation: name of the operation

    Returns:
        the decorated function
    """
    def decorate(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            initial_count = _http_requests_count
            result = func(*args, **kwargs)
            requests_made = _http_requests_count - initial_count
            nonlocal operation
            operation = operation or f"{func.__name__!r}"
            _log.info(f"Needed {requests_made} HTTP request(s) to carry out {operation}")
            return result
        return wrapper
    return decorate

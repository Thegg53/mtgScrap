"""Core utilities for mtgscrap."""
import logging
from functools import wraps
from typing import Callable

from contexttimer import Timer

_log = logging.getLogger(__name__)


def seconds2readable(seconds: float) -> str:
    """Convert seconds to human-readable format (e.g., 0h:01m:30s)."""
    seconds = round(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h:{minutes:02}m:{seconds:02}s"


def timed(operation="", precision=3) -> Callable:
    """Add time measurement to the decorated operation.

    Args:
        operation: name of the time-measured operation (default is function's name)
        precision: precision of the time measurement in seconds (decides output text formatting)

    Returns:
        the decorated function
    """
    if precision < 0:
        precision = 0

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Timer() as t:
                result = func(*args, **kwargs)
            activity = operation or f"'{func.__name__}()'"
            time = seconds2readable(t.elapsed)
            if not precision:
                _log.info(f"Completed {activity} in {time}")
            elif precision == 1:
                _log.info(f"Completed {activity} in {t.elapsed:.{precision}f} "
                          f"second(s) ({time})")
            else:
                _log.info(f"Completed {activity} in {t.elapsed:.{precision}f} "
                          f"second(s)")
            return result
        return wrapper
    return decorator


def extract_int(text: str) -> int:
    """Extract an integer from text.
    
    Args:
        text: text containing digits
        
    Returns:
        extracted integer
        
    Raises:
        ParsingError: if no digits found in text
    """
    num = "".join([char for char in text if char.isdigit()])
    if not num:
        raise ParsingError(f"No digits in text: {text!r}")
    return int(num)


class ParsingError(ValueError):
    """Raised on unexpected states of parsed data."""

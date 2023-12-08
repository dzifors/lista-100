from datetime import datetime
from enum import IntEnum
from typing import Optional
from zoneinfo import ZoneInfo


class Colors(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    GRAY = 90
    LIGHT_RED = 91
    LIGHT_GREEN = 92
    LIGHT_YELLOW = 93
    LIGHT_BLUE = 94
    LIGHT_MAGENTA = 95
    LIGHT_CYAN = 96
    LIGHT_WHITE = 97

    RESET = 0

    def __repr__(self) -> str:
        return f"\x1b[{self.value}m"


TIMEZONE = ZoneInfo("GMT")


def get_current_timestamp() -> str:
    format = "%I:%M:%S%p"
    return f"{datetime.now(tz=TIMEZONE):{format}}"


def log(message: str, color: Optional[Colors] = None):
    current_timestamp = get_current_timestamp()
    if color:
        print(
            f"{Colors.GRAY!r}[{current_timestamp}] {color!r}{message}{Colors.RESET!r}"
        )
    else:
        print(f"{Colors.GRAY!r}[{current_timestamp}] {Colors.RESET}{message}")


TIME_MAGNITUDE_SUFFIXES = ["nsec", "µsec", "msec", "sec"]


def format_time_magnitude(time: int | float) -> str:
    """Output nearest time unit form the amount of nanoseconds provided"""
    suffix = TIME_MAGNITUDE_SUFFIXES[0]
    for suffix in TIME_MAGNITUDE_SUFFIXES:
        if time < 1000:
            break
        time /= 1000

    return f"{time:.2f} {suffix}"

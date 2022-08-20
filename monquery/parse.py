from datetime import datetime
from typing import Tuple, Optional, Callable, TypeVar


def parse_datetime_iso(s: str) -> Tuple[datetime, Optional[str]]:
    try:
        return datetime.fromisoformat(s), None
    except ValueError as e:
        return datetime.utcfromtimestamp(0), e.args[0]


def parse_int(s: str) -> Tuple[int, Optional[str]]:
    try:
        return int(s), None
    except ValueError as e:
        return 0, e.args[0]


def parse_float(s: str) -> Tuple[float, Optional[str]]:
    try:
        return float(s), None
    except ValueError as e:
        return 0, e.args[0]


def parse_string(s: str) -> Tuple[str, Optional[str]]:
    return s, None


def parse_datetime_utc_timestamp(s: str) -> Tuple[datetime, Optional[str]]:
    try:
        return datetime.utcfromtimestamp(float(s)), None
    except ValueError as e:
        return datetime.utcfromtimestamp(0), e.args[0]


T = TypeVar("T")


def optional(
    f: Callable[[str], Tuple[T, Optional[str]]], null_value: str
) -> Callable[[str], Tuple[Optional[T], Optional[str]]]:
    def _parse_optional(s: str) -> Tuple[Optional[T], Optional[str]]:
        if s == null_value:
            return None, None
        return f(s)

    return _parse_optional


def parse_bool(s: str) -> Tuple[Optional[bool], Optional[str]]:
    return s.lower() in ("true", "1"), None

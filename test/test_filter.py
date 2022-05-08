from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import parse_qs

from monquery.fltr import Filter, ParamSimple, ParamMax, ParamMin


def datetime_from_iso_str(s: str) -> Tuple[datetime, Optional[str]]:
    try:
        return datetime.fromisoformat(s), None
    except ValueError as e:
        return datetime.utcfromtimestamp(0), e.args[0]


def int_from_str(s: str) -> Tuple[int, Optional[str]]:
    try:
        return int(s), None
    except ValueError as e:
        return 0, e.args[0]


def string_identity(s: str) -> Tuple[str, Optional[str]]:
    return s, None


def datetime_utc_from_timestamp(s: str) -> Tuple[datetime, Optional[str]]:
    try:
        return datetime.utcfromtimestamp(float(s)), None
    except ValueError as e:
        return datetime.utcfromtimestamp(0), e.args[0]


def test_filter():
    f = Filter(
        [
            ParamSimple("bar", string_identity),
            ParamSimple("baz", int_from_str),
            ParamMax("$lt-foo", datetime_from_iso_str, target_field="foo"),
            ParamMin("$gt-foo", datetime_from_iso_str, target_field="foo"),
            ParamSimple("foo", datetime_from_iso_str),
        ]
    )
    assert f.from_query(
        parse_qs("$lt-foo=2022-05-06T20:35:14.991282&bar=hello there&baz=4")
    ) == (
        {
            "bar": {"$in": ["hello there"]},
            "baz": {"$in": [4]},
            "foo": {"$lt": datetime(2022, 5, 6, 20, 35, 14, 991282)},
        },
        None,
    )

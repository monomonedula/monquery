from datetime import datetime
from urllib.parse import parse_qs

import pytest

from monquery import (
    FilterSimple,
    parse_datetime_iso,
    parse_int,
    SortingOption,
    Sorting,
    PaginationBasic,
    params_basic,
)
from monquery.db import pymongo_find


@pytest.fixture()
def fltr():
    return FilterSimple(
        [
            *params_basic(
                "baz",
                parse_datetime_iso,
                include_range_filters=True,
                include_equality_filter=False,
            ),
            *params_basic(
                "foo",
                parse_int,
                include_range_filters=True,
                include_equality_filter=True,
            ),
            *params_basic(
                "bar",
                parse_int,
                include_range_filters=False,
                include_equality_filter=True,
            ),
        ]
    )


@pytest.fixture()
def pagination():
    return PaginationBasic()


@pytest.fixture()
def sorting():
    return Sorting(
        options=[
            SortingOption("-foo", direction=-1),
            SortingOption("foo"),
            SortingOption("baz"),
        ]
    )


@pytest.mark.parametrize(
    "query, expected",
    [
        (
            "$gt-foo=22&sort=baz",
            [
                {
                    "foo": 12345,
                    "bar": "hello there",
                    "baz": datetime(year=2021, month=5, day=3),
                },
                {
                    "foo": 45,
                    "bar": "whateverrr",
                    "baz": datetime(year=2021, month=6, day=10),
                },
            ],
        ),
        (
            "$gt-foo=22&sort=baz&limit=1&skip=1",
            [
                {
                    "foo": 45,
                    "bar": "whateverrr",
                    "baz": datetime(year=2021, month=6, day=10),
                },
            ],
        ),
    ],
)
def test_pymongo(coll, fltr, pagination, sorting, query, expected):
    cursor, err = pymongo_find(
        coll,
        fltr,
        sorting,
        pagination,
        parse_qs(query),
        projection={"_id": False},
    )
    assert list(cursor) == expected
    assert err is None

from datetime import datetime
from urllib.parse import parse_qs

import pytest
from pymongo import MongoClient

from monquery import (
    Filter,
    parse_datetime_iso,
    parse_int,
    SortingOption,
    Sorting,
    PaginationBasic,
    params_basic,
)
from monquery.db import pymongo_search_find


@pytest.fixture()
def coll():
    client = MongoClient("localhost", 27017)
    coll = client["test"]["test_coll"]
    coll.delete_many({})
    coll.insert_many(
        [
            {
                "foo": 12345,
                "bar": "hello there",
                "baz": datetime(year=2021, month=5, day=3),
            },
            {
                "foo": -3445,
                "bar": "general kenobi",
                "baz": datetime(year=2021, month=5, day=1),
            },
            {
                "foo": 45,
                "bar": "whateverrr",
                "baz": datetime(year=2021, month=6, day=10),
            },
        ]
    )
    yield coll
    coll.delete_many({})


@pytest.fixture()
def fltr():
    return Filter(
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
    assert (
        list(
            pymongo_search_find(
                coll,
                fltr,
                sorting,
                pagination,
                parse_qs(query),
                projection={"_id": False}
            )
        )
        == expected
    )
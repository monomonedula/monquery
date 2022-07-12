from datetime import datetime
from urllib.parse import parse_qs

from monquery import (
    FilterSimple,
    ParamEq,
    ParamMax,
    ParamMin,
    PaginationBasic,
    Pg,
    Sorting,
    SortingOption,
    parse_string,
    parse_int,
    parse_datetime_iso,
)


def test_filter():
    f = FilterSimple(
        [
            ParamEq("bar", parse_string),
            ParamEq("baz", parse_int),
            ParamMax("$lt-foo", parse_datetime_iso, target_field="foo"),
            ParamMin("$gt-foo", parse_datetime_iso, target_field="foo"),
            ParamEq("foo", parse_datetime_iso),
        ]
    )
    assert f.from_query(
        parse_qs("$lt-foo=2022-05-06T20:35:14.991282&bar=hello there&baz=4")
    ) == (
        {
            "$and": [
                {"foo": {"$lt": datetime(2022, 5, 6, 20, 35, 14, 991282)}},
                {"bar": {"$in": ["hello there"]}},
                {"baz": {"$in": [4]}},
            ]
        },
        None,
    )
    assert f.from_query(parse_qs("$lt-foo=incorrect-format&bar=hello there&baz=4")) == (
        {},
        "Error while parsing '$lt-foo' param. Invalid isoformat string: 'incorrect-format'",
    )
    assert (
        repr(f) == "FilterSimple([ParamMin(ParamSingleValue(name='$gt-foo', "
        f"target_field=foo, conv={parse_datetime_iso!r}, operator=$gt)),"
        " ParamMax(ParamSingleValue(name='$lt-foo', target_field=foo,"
        f" conv={parse_datetime_iso!r}, operator=$lt)), "
        "ParamEq(ParamMultiValue(name='bar', target_field=bar,"
        f" conv={parse_string!r}, operator=$in)), "
        "ParamEq(ParamMultiValue(name='baz', target_field=baz,"
        f" conv={parse_int!r}, operator=$in)), "
        "ParamEq(ParamMultiValue(name='foo', target_field=foo,"
        f" conv={parse_datetime_iso!r}, operator=$in))])"
    )


def test_paginate():
    assert PaginationBasic().from_query(
        parse_qs("foo=bar&baz=55&skip=14&limit=32")
    ) == (
        Pg(skip=14, limit=32),
        None,
    )
    assert PaginationBasic().from_query(parse_qs("foo=bar&baz=55&skip=14")) == (
        Pg(skip=14, limit=None),
        None,
    )
    assert PaginationBasic().from_query(parse_qs("foo=bar&baz=55&limit=32")) == (
        Pg(skip=None, limit=32),
        None,
    )
    assert PaginationBasic().from_query(parse_qs("foo=bar&baz=55&limit=foo")) == (
        Pg(),
        "value of 'limit' must be integer",
    )
    assert PaginationBasic().from_query(parse_qs("foo=bar&baz=55&skip=foo")) == (
        Pg(),
        "value of 'skip' must be integer",
    )
    assert PaginationBasic(default_limit=40).from_query(parse_qs("foo=bar&baz=55")) == (
        Pg(limit=40),
        None,
    )
    assert PaginationBasic(
        skip_name="nobody_expects_the_spanish_inquisition", limit_name="some-other-name"
    ).from_query(
        parse_qs(
            "foo=bar&baz=55&nobody_expects_the_spanish_inquisition=22&some-other-name=54"
        )
    ) == (
        Pg(skip=22, limit=54),
        None,
    )


def test_sort():
    s = Sorting(
        options=[
            SortingOption(
                "foo",
            ),
            SortingOption("-foo", direction=-1),
            SortingOption("bar"),
            SortingOption("-bar", direction=-1),
            SortingOption("baz", direction=-1),
        ]
    )

    assert s.from_query(parse_qs("sort=foo")) == (SortingOption("foo"), None)
    assert s.from_query(parse_qs("sort=-bar")) == (
        SortingOption("-bar", direction=-1),
        None,
    )
    assert s.from_query(parse_qs("sort=-baz")) == (
        None,
        "unexpected sorting key: '-baz'",
    )
    assert s.from_query(parse_qs("whatever=baz")) == (
        None,
        None,
    )
    assert Sorting(options=[SortingOption("foo",),], key="xxx").from_query(
        parse_qs("whatever=234&xxx=foo")
    ) == (SortingOption("foo"), None)
    assert Sorting(
        options=[SortingOption("foo")],
        default=SortingOption("haha"),
    ).from_query(parse_qs("whatever=234")) == (SortingOption("haha"), None)

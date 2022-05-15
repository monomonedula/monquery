from datetime import datetime

import pytest
from pymongo import MongoClient


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

[![Build Status](https://app.travis-ci.com/monomonedula/monquery.svg?branch=master)](https://app.travis-ci.com/monomonedula/monquery)
[![codecov](https://codecov.io/gh/monomonedula/monquery/branch/master/graph/badge.svg?token=lIa1a4PWtX)](https://codecov.io/gh/monomonedula/monquery)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
### Monquery

A small toolkit enabling easier declarative approach to declaring
read API with MongoDB backend with rich filtering query parameters and minimum hustle.


It's framework-agnostic which means its role boils down to translating
HTTP request query string into a valid MongoDB query.

### Installation
```shell
pip install monquery
```

### How it works

**Filtering**:

```python
from urllib.parse import parse_qs
from monquery import (
    FilterSimple, ParamEq, parse_int, parse_string, parse_datetime_iso, ParamMax, ParamMin
)

FilterSimple(
    [
        ParamEq("bar", parse_string, multi=False),
        ParamEq("baz", parse_int, multi=False),
        ParamMax("foo[max]", parse_datetime_iso, target_field="foo"),
        ParamMin("foo[min]", parse_datetime_iso, target_field="foo"),
    ]
).from_query(
    parse_qs("foo[max]=2022-05-06T20:35:14.991282&bar=hello there&baz=4")
)

# returns the filter and error (which is None in this case meaning that everything is OK): 
# (
#    {
#        "bar": {"$eq": "hello there"},
#        "baz": {"$eq": 4},
#        "foo": {"$lt": datetime(2022, 5, 6, 20, 35, 14, 991282)},
#    },
#    None,
# )
#
```

**Sorting:**
```python
from urllib.parse import parse_qs
from monquery import (
    Sorting, SortingOption, 
)

Sorting(
    options=[
        SortingOption("foo"),
        SortingOption("-foo", field="foo", direction=-1),
        SortingOption("bar"),
        SortingOption("-bar", field="bar", direction=-1),
        SortingOption("baz", direction=-1),
    ]
).from_query(parse_qs("sort=foo"))

#   Returns:
#   (SortingOption("foo"), None)

```


**Pagination:**
```python
from urllib.parse import parse_qs
from monquery import PaginationBasic

PaginationBasic().from_query(parse_qs("skip=14&limit=32")) 

#   returns:
#    (
#        Pg(skip=14, limit=32),
#        None,
#    )

```

Utility function to bind it all together wtih a `pymongo` collection like this:

```python
import pymongo
from urllib.parse import parse_qs

from monquery import (
    pymongo_find,
    FilterSimple,
    ParamEq,
    PaginationBasic,
    parse_float,
    parse_int,
    Sorting,
    SortingOption,
)
from pymongo import MongoClient, ASCENDING, DESCENDING

client = MongoClient("your-connection-string-or-whatever")
coll = client["your-database-name"]["your-collection-name"]

cursor, error = pymongo_find(
    coll,
    fltr=FilterSimple([ParamEq("foo", parse_float), ParamEq("bar", parse_int)]),
    pg=PaginationBasic(),
    sorting=Sorting([SortingOption("foo", field="foo", direction=ASCENDING),
                     SortingOption("-foo", field="foo", direction=DESCENDING)]),
    query=parse_qs("foo=234.43&bar=68452"),
)

# Returns a pymongo cursor and optional error, if one occurred.

```

Don't be shy to look into the unit tests and source code if in doubt.

There's also a neat demo app [here](demo/).

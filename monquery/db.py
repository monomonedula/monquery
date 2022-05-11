from typing import Dict, List, Any, Optional

from monquery import Filter, Sorting, Pagination


def pymongo_search_find(
    collection,
    fltr: Filter,
    sorting: Sorting,
    pg: Pagination,
    query: Dict[str, List[str]],
    projection: Optional[Dict[str, Any]] = None,
):
    f, err = fltr.from_query(query)
    if err:
        return None, err
    p, err = pg.from_query(query)
    if err:
        return None, err
    s, err = sorting.from_query(query)
    if err:
        return None, err
    print(
        f,
        p,
        s,
    )
    cursor = (
        collection.find(f, projection) if projection is not None else collection.find(f)
    )
    if s is not None:
        cursor = cursor.sort([(s.name, s.direction)])
    if p.skip:
        cursor = cursor.skip(p.skip)
    if p.limit is not None:
        cursor = cursor.limit(p.limit)
    return cursor

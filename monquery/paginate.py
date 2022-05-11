from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

from monquery.util import get_one


@dataclass(frozen=True)
class Pg:
    skip: Optional[int] = None
    limit: Optional[int] = None


class Pagination(ABC):
    @abstractmethod
    def from_query(self, q: Dict[str, List[str]]) -> Tuple[Pg, Optional[str]]:
        pass


class PaginationBasic(Pagination):
    def __init__(
        self,
        default_limit: Optional[int] = None,
        skip_name: str = "skip",
        limit_name: str = "limit",
    ):
        self._default_limit: Optional[int] = default_limit
        self._skip: str = skip_name
        self._limit: str = limit_name

    def from_query(self, q: Dict[str, List[str]]) -> Tuple[Pg, Optional[str]]:
        skip, err = self._to_int(self._skip, q)
        if err:
            return Pg(), err
        limit, err = self._to_int(self._limit, q)
        if err:
            return Pg(), err
        return (
            Pg(
                skip=skip,
                limit=limit if limit is not None else self._default_limit,
            ),
            None,
        )

    @staticmethod
    def _to_int(
        key: str, q: Dict[str, List[str]]
    ) -> Tuple[Optional[int], Optional[str]]:
        val = get_one(q, key)
        if val is None:
            return None, None
        try:
            return int(val), None
        except ValueError:
            return None, f"value of {key!r} must be integer"


class PaginationDummy(Pagination):
    def from_query(self, q: Dict[str, List[str]]) -> Tuple[Pg, Optional[str]]:
        return Pg(), None

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from monquery.util import get_one


@dataclass(frozen=True)
class SortingOption:
    name: str
    field: Optional[str] = None
    direction: int = 1


class Sorting:
    def __init__(
        self,
        options: List[SortingOption],
        key: str = "sort",
        default: Optional[SortingOption] = None,
    ):
        self._options = {s.name: s for s in options}
        self._key: str = key
        self._default: Optional[SortingOption] = default

    def from_query(
        self, q: Dict[str, List[str]]
    ) -> Tuple[Optional[SortingOption], Optional[str]]:
        sort_key = get_one(q, self._key)
        if sort_key is None:
            return self._default, None
        if sort_key in self._options:
            return self._options[sort_key], None
        return None, f"unexpected sorting key: {sort_key!r}"

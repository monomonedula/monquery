from dataclasses import dataclass
from typing import Dict, List, Optional, FrozenSet, Tuple

from monquery.util import get_one


@dataclass(frozen=True)
class Srt:
    field: str
    direction: int


class Sorting:
    def __init__(
        self,
        allowed_fields: List[str],
        key: str = "sort",
        default: Optional[Srt] = None,
    ):
        self._allowed_fields: FrozenSet[str] = frozenset(allowed_fields)
        self._key: str = key
        self._default: Optional[Srt] = default

    def from_query(
        self, q: Dict[str, List[str]]
    ) -> Tuple[Optional[Srt], Optional[str]]:
        sort_key = get_one(q, self._key)
        if sort_key is None:
            return self._default, None
        if sort_key.startswith("-"):
            srt = Srt(sort_key.replace("-", "", 1), -1)
        else:
            srt = Srt(sort_key, 1)
        if srt.field not in self._allowed_fields:
            return None, f"unexpected sorting key: {sort_key!r}"
        return srt, None

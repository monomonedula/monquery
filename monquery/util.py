from typing import Dict, List, Optional


def get_one(q: Dict[str, List[str]], key: str) -> Optional[str]:
    val = q.get(key)
    if val:
        return val[0]
    return None

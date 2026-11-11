from __future__ import annotations

from typing import Any


def paginate(items: list[Any], skip: int = 0, limit: int | None = None) -> list[Any]:
    start = max(skip, 0)
    if limit is None:
        return items[start:]
    return items[start:start + limit]

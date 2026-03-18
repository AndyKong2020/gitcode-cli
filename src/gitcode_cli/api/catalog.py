from __future__ import annotations

import json
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parent.parent / "assets" / "gitcode_api" / "endpoint-catalog.json"


def load_catalog() -> list[dict]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def search_catalog(query: str, limit: int = 20) -> list[dict]:
    needle = query.lower()
    results = []
    for item in load_catalog():
        haystacks = [
            item.get("title", ""),
            item.get("method", ""),
            item.get("path", ""),
            item.get("permalink", ""),
            " ".join(item.get("categories", [])),
            " ".join(item.get("tags", [])),
        ]
        if needle in " | ".join(haystacks).lower():
            results.append(item)
    return results[:limit]

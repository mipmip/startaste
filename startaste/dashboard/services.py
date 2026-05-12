from __future__ import annotations

import json
import math

from startaste.sources import get_sources
from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.github.models import GithubStar


def _paginate(query, page: int = 1, per_page: int = 50) -> dict:
    total = query.count()
    pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, pages))
    items = list(query.paginate(page, per_page).dicts())
    # Parse body JSON for each item
    for item in items:
        if item.get("body"):
            try:
                item["body"] = json.loads(item["body"])
            except (json.JSONDecodeError, TypeError):
                pass
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def get_overview() -> dict:
    sources = []
    for src in get_sources():
        counts = {}
        last_sync = None
        for model, item_type in zip(src.models, src.item_types):
            count = model.count_all()
            counts[item_type] = count
            if count > 0:
                latest = (
                    model.select(model.timestamp)
                    .where(model.timestamp.is_null(False))
                    .order_by(model.timestamp.desc())
                    .limit(1)
                    .dicts()
                )
                for row in latest:
                    ts = row.get("timestamp")
                    if ts and (last_sync is None or ts > last_sync):
                        last_sync = ts
        sources.append({
            "name": src.name,
            "configured": src.is_configured(),
            "counts": counts,
            "last_sync": str(last_sync) if last_sync else None,
        })
    return {"sources": sources}


def get_hn_stories(page: int = 1, per_page: int = 50) -> dict:
    query = (
        HnStory.select()
        .where(HnStory.body.is_null(False))
        .order_by(HnStory.timestamp.desc())
    )
    return _paginate(query, page, per_page)


def get_hn_comments(page: int = 1, per_page: int = 50) -> dict:
    query = (
        HnComment.select()
        .where(HnComment.body.is_null(False))
        .order_by(HnComment.timestamp.desc())
    )
    return _paginate(query, page, per_page)


def get_github_stars(page: int = 1, per_page: int = 50) -> dict:
    query = (
        GithubStar.select()
        .where(GithubStar.body.is_null(False))
        .order_by(GithubStar.timestamp.desc())
    )
    return _paginate(query, page, per_page)

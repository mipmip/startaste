"""Queries over the collected data, shared by the dashboard and the MCP server."""

from __future__ import annotations

import json
import math

from urllib.parse import urlparse
from collections import Counter

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


# --- shared helpers for search and aggregation ------------------------------
#
# Both walk the stored API responses. A SQL LIKE narrows the rows first when
# there is a text term; the refinement happens in Python because the fields
# live inside a JSON body (repo.topics is an array, HN items differ by type).


def _repo_of(body: dict) -> dict:
    """GitHub stars are stored as {starred_at, repo}; tolerate a bare repo."""
    return body.get("repo", body) if isinstance(body, dict) else {}


def _bodies(model, contains: str | None = None):
    query = model.select().where(model.body.is_null(False))
    if contains:
        query = query.where(model.body.contains(contains))
    query = query.order_by(model.timestamp.desc())

    for row in query.dicts():
        try:
            body = json.loads(row["body"])
        except (json.JSONDecodeError, TypeError):
            continue
        yield row["_id"], body


def _bounded(items: list, limit: int) -> dict:
    return {
        "items": items[:limit],
        "total": len(items),
        "limit": limit,
        "truncated": len(items) > limit,
    }


def search_stars(
    query: str | None = None,
    language: str | None = None,
    topic: str | None = None,
    limit: int = 20,
) -> dict:
    needle = (query or "").lower()
    lang = (language or "").lower()
    tag = (topic or "").lower()

    matches = []
    for _id, body in _bodies(GithubStar, contains=query):
        repo = _repo_of(body)
        name = repo.get("full_name") or ""
        description = repo.get("description") or ""
        repo_lang = repo.get("language") or ""
        topics = [t.lower() for t in (repo.get("topics") or [])]

        if needle and needle not in name.lower() and needle not in description.lower():
            continue
        if lang and repo_lang.lower() != lang:
            continue
        if tag and tag not in topics:
            continue

        matches.append({
            "id": _id,
            "full_name": name,
            "description": description,
            "language": repo_lang or None,
            "topics": repo.get("topics") or [],
            "url": repo.get("html_url"),
            "stars": repo.get("stargazers_count"),
            "starred_at": body.get("starred_at") if isinstance(body, dict) else None,
        })

    return _bounded(matches, limit)


def search_upvotes(
    query: str | None = None,
    item_type: str | None = None,
    limit: int = 20,
) -> dict:
    needle = (query or "").lower()
    wanted = (item_type or "").lower()

    models = []
    if wanted in ("", "story"):
        models.append(("story", HnStory))
    if wanted in ("", "comment"):
        models.append(("comment", HnComment))

    matches = []
    for kind, model in models:
        for _id, body in _bodies(model, contains=query):
            # Stories carry a title; comments carry text.
            text = (body.get("title") or body.get("text") or "") if isinstance(body, dict) else ""
            if needle and needle not in text.lower():
                continue
            matches.append({
                "id": _id,
                "type": kind,
                "text": text,
                "url": body.get("url"),
                "score": body.get("score"),
                "by": body.get("by"),
            })

    return _bounded(matches, limit)


def _ranked(counter: Counter, limit: int) -> dict:
    ranked = [{"name": name, "count": n} for name, n in counter.most_common(limit)]
    return {"items": ranked, "total_distinct": len(counter), "limit": limit}


def top_topics(limit: int = 20) -> dict:
    counter: Counter = Counter()
    for _id, body in _bodies(GithubStar):
        for topic in _repo_of(body).get("topics") or []:
            if topic:
                counter[topic] += 1
    return _ranked(counter, limit)


def top_languages(limit: int = 20) -> dict:
    counter: Counter = Counter()
    for _id, body in _bodies(GithubStar):
        language = _repo_of(body).get("language")
        if language:
            counter[language] += 1
    return _ranked(counter, limit)


def top_domains(limit: int = 20) -> dict:
    counter: Counter = Counter()
    for _id, body in _bodies(HnStory):
        url = body.get("url") if isinstance(body, dict) else None
        if not url:
            continue
        host = (urlparse(url).netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host:
            counter[host] += 1
    return _ranked(counter, limit)


def get_item(source: str, item_id: str) -> dict:
    """Look up one stored item. `source` is "github" or "hn"."""
    lookup = {
        "github": [("star", GithubStar)],
        "hn": [("story", HnStory), ("comment", HnComment)],
    }.get((source or "").lower())

    if lookup is None:
        return {"found": False, "reason": f"unknown source {source!r}; use 'github' or 'hn'"}

    for kind, model in lookup:
        row = model.select().where(model._id == str(item_id)).dicts().first()
        if row is None:
            continue
        body = row.get("body")
        if body:
            try:
                body = json.loads(body)
            except (json.JSONDecodeError, TypeError):
                pass
        return {"found": True, "source": source, "type": kind, "id": row["_id"], "body": body}

    return {"found": False, "reason": f"no {source} item with id {item_id!r}"}

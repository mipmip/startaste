from __future__ import annotations

from startaste.sources.base import Source


def _load_sources() -> list[Source]:
    from startaste.sources.hn import HnSource
    from startaste.sources.github import GithubSource
    return [HnSource(), GithubSource()]


_ALL_SOURCES: list[Source] | None = None


def get_sources() -> list[Source]:
    global _ALL_SOURCES
    if _ALL_SOURCES is None:
        _ALL_SOURCES = _load_sources()
    return _ALL_SOURCES


def get_configured_sources() -> list[Source]:
    return [s for s in get_sources() if s.is_configured()]


def get_source(name: str) -> Source:
    for s in get_sources():
        if s.name == name:
            return s
    available = ", ".join(s.name for s in get_sources())
    raise SystemExit(f"Error: unknown source '{name}'. Available: {available}")

from __future__ import annotations

import logging

from startaste.sources import get_configured_sources, get_source

log = logging.getLogger(__name__)


def run_sync(source_name: str | None = None):
    if source_name:
        source = get_source(source_name)
        if not source.is_configured():
            missing = ", ".join(f"{k} ({v})" for k, v in source.env_help.items())
            raise SystemExit(f"Error: source '{source_name}' is not configured. Set: {missing}")
        sources = [source]
    else:
        sources = get_configured_sources()
        if not sources:
            raise SystemExit("Error: no sources configured. Set credentials in .env or environment.")

    for source in sources:
        log.info(f"Syncing {source.name}...")
        source.sync()

    log.info("Sync complete")

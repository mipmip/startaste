from __future__ import annotations

import logging

from startaste.sources import get_configured_sources, get_source
from startaste.sources.base import SourceError

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

    failed = []
    for source in sources:
        log.info(f"Syncing {source.name}...")
        try:
            source.sync()
        except SourceError as exc:
            # A condition the source understands: report it as one line and
            # carry on, so one source cannot silently skip the others.
            log.error(f"Error: {exc.detail}")
            failed.append(source.name)

    if failed:
        raise SystemExit(
            f"Sync failed for: {', '.join(failed)}. "
            "Other configured sources were synced."
            if len(failed) < len(sources)
            else f"Sync failed for: {', '.join(failed)}."
        )

    log.info("Sync complete")

from __future__ import annotations

import json
import logging

from startaste.db import Story, Comment, database, create_tables

log = logging.getLogger(__name__)

exporters = {
    "json": lambda stories, comments: json.dumps(
        {"saved_stories": stories, "saved_comments": comments},
        indent=2,
    ),
}


def run_export(format: str = "json", select: list[str] | None = None, file: str | None = None):
    if select is None:
        select = ["story", "comment"]

    create_tables()
    database.connect()

    stories = Story.to_dict() if "story" in select else []
    comments = Comment.to_dict() if "comment" in select else []

    exporter = exporters.get(format)
    if not exporter:
        raise SystemExit(f"Error: unknown format '{format}'. Available: {', '.join(exporters)}")

    output = exporter(stories, comments)

    if file:
        with open(file, "w") as f:
            f.write(output)
        log.info(f"Exported to {file}")
    else:
        print(output)

    database.close()

"""Presentation-shaped wrappers over the shared query layer.

The queries themselves live in `startaste.queries` because the MCP server needs
them too, and the dashboard package is the wrong home for something another
surface depends on.
"""

from __future__ import annotations

from startaste.queries import (  # noqa: F401  (re-exported for the dashboard)
    get_github_stars,
    get_hn_comments,
    get_hn_stories,
    get_overview,
)

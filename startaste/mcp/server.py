"""The MCP surface: streamable HTTP, bearer-authenticated, read-only.

Tools are thin wrappers over startaste.queries. The reasoning belongs to the
client: this server answers "what is in the collection", not "what does it mean".
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.routing import Route

from startaste import queries
from startaste.mcp.auth import StaticTokenAuthenticator, Unauthorized, load_records

log = logging.getLogger(__name__)

INSTRUCTIONS = """\
Read-only access to one person's collected taste: repositories they starred on
GitHub and stories and comments they upvoted on Hacker News.

Use the top_* tools to learn what they care about, the search_* tools to find
specific items, and get_item for a full record. Every search is bounded: check
`truncated` and `total` to see whether you saw everything.
"""


def build_mcp() -> FastMCP:
    mcp = FastMCP("startaste", instructions=INSTRUCTIONS)

    @mcp.tool()
    def search_stars(
        query: str | None = None,
        language: str | None = None,
        topic: str | None = None,
        limit: int = 20,
    ) -> dict:
        """Search starred GitHub repositories by text, language and/or topic.

        `query` matches the repository's full name and description. `language`
        and `topic` are exact (case-insensitive) filters. Returns items with
        full_name, description, language, topics, url and stars, plus `total`
        matched and `truncated`.
        """
        return queries.search_stars(query=query, language=language, topic=topic, limit=limit)

    @mcp.tool()
    def search_upvotes(
        query: str | None = None,
        item_type: str | None = None,
        limit: int = 20,
    ) -> dict:
        """Search upvoted Hacker News items by text.

        `query` matches story titles and comment text. `item_type` restricts to
        "story" or "comment"; omit it for both. Returns items with id, type,
        text, url and score, plus `total` matched and `truncated`.
        """
        return queries.search_upvotes(query=query, item_type=item_type, limit=limit)

    @mcp.tool()
    def get_item(source: str, item_id: str) -> dict:
        """Fetch one stored item in full.

        `source` is "github" (a starred repository) or "hn" (an upvoted story or
        comment). Returns the stored API record, or found=false with a reason.
        """
        return queries.get_item(source, item_id)

    @mcp.tool()
    def overview() -> dict:
        """Per-source item counts and when each source last had new data.

        Use this first to see how much there is to work with.
        """
        return queries.get_overview()

    @mcp.tool()
    def top_topics(limit: int = 20) -> dict:
        """The most common GitHub topics across starred repositories, by count.

        The best single answer to "what does this person care about". Note that
        topics are author-assigned and not every repository has them.
        """
        return queries.top_topics(limit=limit)

    @mcp.tool()
    def top_languages(limit: int = 20) -> dict:
        """The most common programming languages across starred repositories."""
        return queries.top_languages(limit=limit)

    @mcp.tool()
    def top_domains(limit: int = 20) -> dict:
        """The most upvoted domains on Hacker News, by count.

        Shows which sources and sites this person's attention goes to.
        """
        return queries.top_domains(limit=limit)

    return mcp


async def _healthz(request):
    """Liveness only. This endpoint is unauthenticated, so it must never
    disclose anything about the collection."""
    return JSONResponse({"status": "ok"})


class BearerAuthMiddleware:
    """Requires a valid bearer token on everything except the open paths."""

    def __init__(self, app, authenticator: StaticTokenAuthenticator, open_paths=("/healthz",)):
        self.app = app
        self.authenticator = authenticator
        self.open_paths = tuple(open_paths)

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("path") in self.open_paths:
            await self.app(scope, receive, send)
            return

        headers = {k.lower(): v for k, v in (scope.get("headers") or [])}
        raw = headers.get(b"authorization", b"").decode("latin-1")
        try:
            identity = self.authenticator.authenticate_header(raw or None)
        except Unauthorized:
            response = JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return

        log.debug("authenticated MCP request for %s", identity.name)
        await self.app(scope, receive, send)


def build_app(tokens_file):
    """The ASGI app: /healthz open, everything else bearer-authenticated."""
    records = load_records(tokens_file)
    if not records:
        raise SystemExit(f"Error: no usable token records in {tokens_file}")

    app = build_mcp().streamable_http_app()
    # Added to the app FastMCP built, so its session-manager lifespan is kept.
    app.router.routes.insert(0, Route("/healthz", _healthz, methods=["GET"]))
    app.add_middleware(BearerAuthMiddleware, authenticator=StaticTokenAuthenticator(records))
    return app


def serve(host: str, port: int, tokens_file: str) -> None:
    import uvicorn

    from startaste.db import open_readonly

    open_readonly()
    app = build_app(tokens_file)
    log.info(f"MCP server on http://{host}:{port}/mcp")
    uvicorn.run(app, host=host, port=port, log_level="info")

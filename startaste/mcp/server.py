"""The MCP surface: streamable HTTP, bearer-authenticated, read-only.

Tools are thin wrappers over startaste.queries. The reasoning belongs to the
client: this server answers "what is in the collection", not "what does it mean".
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
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


# Loopback is always allowed so local probes and health checks need no config.
LOOPBACK_HOSTS = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
LOOPBACK_ORIGINS = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]


def transport_security(allowed_hosts=()) -> TransportSecuritySettings:
    """Host/Origin allow-list for the MCP transport's DNS-rebinding defence.

    FastMCP turns that defence on by itself when its `host` setting is loopback —
    which is its default, and which we never override because uvicorn does the
    binding. The effect was that a server behind an HTTPS reverse proxy answered
    every request `421 Invalid Host header`: the proxy forwards the public
    hostname, and only loopback was on the list.

    So build the list explicitly from what the deployment actually serves. The
    defence stays ON; declaring a hostname widens the list, it does not disable
    anything.
    """
    hosts = list(LOOPBACK_HOSTS)
    origins = list(LOOPBACK_ORIGINS)
    for host in allowed_hosts:
        if not host:
            continue
        hosts.append(host)
        origins.extend([f"https://{host}", f"http://{host}"])
        if ":" not in host:
            # A proxy may or may not include the port in Host; accept both.
            hosts.append(f"{host}:*")
            origins.extend([f"https://{host}:*", f"http://{host}:*"])
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
        allowed_origins=origins,
    )


def build_mcp(allowed_hosts=()) -> FastMCP:
    mcp = FastMCP(
        "startaste",
        instructions=INSTRUCTIONS,
        transport_security=transport_security(allowed_hosts),
    )

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
    """Requires a valid bearer token on the MCP endpoint.

    Scoped to `protected_prefix` rather than guarding the whole app, so a path
    the server does not serve reaches the router and is answered 404. Guarding
    everything made unserved paths answer 401, which breaks clients following
    the MCP authorization flow: a 401 sends them looking for protected-resource
    metadata under /.well-known/, and a 401 there means they can neither
    complete discovery nor conclude there is none, so they give up instead of
    using the static token they were given.

    For the same reason the rejection carries no WWW-Authenticate challenge. A
    bare `Bearer` challenge names no realm and points at no metadata, so it
    tells a client nothing it can act on while sending it down that dead end.
    """

    def __init__(self, app, authenticator: StaticTokenAuthenticator, protected_prefix="/mcp"):
        self.app = app
        self.authenticator = authenticator
        self.protected_prefix = protected_prefix

    def _is_protected(self, path: str) -> bool:
        # "/mcp" and "/mcp/..." are the endpoint; "/mcpsomething" is not.
        return path == self.protected_prefix or path.startswith(self.protected_prefix + "/")

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or not self._is_protected(scope.get("path", "")):
            await self.app(scope, receive, send)
            return

        headers = {k.lower(): v for k, v in (scope.get("headers") or [])}
        raw = headers.get(b"authorization", b"").decode("latin-1")
        try:
            identity = self.authenticator.authenticate_header(raw or None)
        except Unauthorized:
            response = JSONResponse({"error": "unauthorized"}, status_code=401)
            await response(scope, receive, send)
            return

        log.debug("authenticated MCP request for %s", identity.name)
        await self.app(scope, receive, send)


def build_app(tokens_file, allowed_hosts=()):
    """The ASGI app: the MCP endpoint bearer-authenticated, everything else routed.

    Only /mcp is guarded, so /healthz stays open and any other path 404s rather
    than claiming to need credentials.
    """
    records = load_records(tokens_file)
    if not records:
        raise SystemExit(f"Error: no usable token records in {tokens_file}")

    app = build_mcp(allowed_hosts).streamable_http_app()
    # Added to the app FastMCP built, so its session-manager lifespan is kept.
    app.router.routes.insert(0, Route("/healthz", _healthz, methods=["GET"]))
    app.add_middleware(BearerAuthMiddleware, authenticator=StaticTokenAuthenticator(records))
    return app


def serve(host: str, port: int, tokens_file: str, allowed_hosts=()) -> None:
    import uvicorn

    from startaste.db import open_readonly

    open_readonly()
    # The address we bind is always a legitimate Host: it is how a client on the
    # same network reaches us directly, without anyone having to declare it.
    app = build_app(tokens_file, [f"{host}:{port}", *allowed_hosts])
    log.info(f"MCP server on http://{host}:{port}/mcp")
    uvicorn.run(app, host=host, port=port, log_level="info")

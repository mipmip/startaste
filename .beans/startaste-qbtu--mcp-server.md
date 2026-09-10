---
# startaste-qbtu
title: mcp server
status: completed
type: task
priority: normal
created_at: 2026-09-09T12:11:08Z
updated_at: 2026-09-10T16:00:03Z
---

authenticated for one person only. See how the mcp server works of Linny.vim (github.com/linden-project)

Decisions from the 2026-09-10 exploration session:

- Endpoint: `https://taste.pimsnel.com/mcp`, TLS terminated on durer, reverse
  proxied over nebula to dapperehaan. Same shape as
  `mipnix/openspec/specs/linny-mcp-hosting/spec.md`, which is the template to
  copy: mesh-only bind, unauthenticated `/healthz`, `Authorization: Bearer`
  on `/mcp` with hashed token records from an agenix `tokensFile`, and an nginx
  vhost with `proxy_buffering off` + HTTP/1.1 + long read timeout because the
  streamable-HTTP transport is SSE.
- Language: stays Python, in this codebase. linny-mcp-server is Go
  (`github.com/modelcontextprotocol/go-sdk v1.7.0`) and a Go port would reuse
  its `auth.Middleware` and module glue verbatim — but that is ~150 lines
  against splitting a 900-line project across two toolchains. The fiddly parts
  (nebula bind, agenix, durer vhost) live outside the application either way.
- Transport is streamable HTTP, which is ASGI in the Python SDK while the
  dashboard is Flask/WSGI. Run them as separate systemd units on separate
  ports rather than adapting one into the other.
- Tools: start simple — retrieval and aggregation over the existing SQLite
  (`dashboard/services.py` is already close to the query layer needed).
  Aggregations are wanted; the reasoning is NOT startaste's job. "Find news
  about topics I like" means Claude calls `top_topics()` and does its own
  search. Keep the server a data surface.
- Requires [[startaste-zrap]] (module) and WAL mode
  ([[startaste-hq9c]]) before a reader can run alongside the sync timer.
- Later: the interest graph ([[startaste-gnw6]]) becomes the more
  interesting thing to expose once tiers 1-2 exist.

## Summary of Changes

Shipped as openspec change `mcp-server`, archived at
`openspec/changes/archive/2026-09-10-mcp-server`, commit `e1c5858`.

`startaste mcp --host --port --tokens-file` serves streamable HTTP: `/mcp`
bearer-authenticated, `/healthz` open and liveness-only. Seven read-only tools —
`search_stars`, `search_upvotes`, `get_item`, `overview`, `top_topics`,
`top_languages`, `top_domains` — each bounded, reporting `total` and
`truncated`.

Authentication mirrors `linny-mcp-server/internal/auth`: `{name, hash, scopes}`
records, hex SHA-256, constant-time comparison with no early exit, one
indistinguishable failure. `startaste mcp-token` mints a token and prints its
record. `scopes` is parsed but unused, so adding a write tool later needs no
token-file migration.

The database is opened read-only via `mode=ro`, so SQLite refuses writes rather
than application code remembering to. Query functions moved to
`startaste/queries.py`, shared with the dashboard, and gained search and
aggregation. `services.startaste.mcp.*` adds the unit.

Verified with a real MCP client against real data: 2975 stars and 2288 upvotes,
all seven tools plausible. The VM test covers 401 without a token, non-401 with
one, open `/healthz`, and the hardened profile. 128 tests, coverage 94%.

Two bugs the VM test caught that local tests could not: `startaste.mcp` was
missing from `pyproject.toml`'s package list, so the packaged build had no
module; and the unit would have exhausted systemd's start limit on a host with
no database yet, before the first sync could create one.

New live capabilities: `mcp-server` (5 requirements). Unblocks `mipnix` change
`deploy-startaste-dapperehaan` group 5.

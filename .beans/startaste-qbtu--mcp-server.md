---
# startaste-qbtu
title: mcp server
status: todo
type: task
priority: normal
created_at: 2026-09-09T12:11:08Z
updated_at: 2026-09-10T15:06:48Z
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

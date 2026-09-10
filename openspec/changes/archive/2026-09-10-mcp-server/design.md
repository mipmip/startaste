## Context

See proposal.md — Why. Three existing things constrain the shape:

- **The hosting is already decided and specced.** `mipnix` change
  `deploy-startaste-dapperehaan` and the live `linny-mcp-hosting` capability fix
  the topology: mesh-only bind, TLS on durer, `proxy_buffering off` for SSE,
  `/healthz` open, `/mcp` bearer-protected, tokens from agenix. This change has
  to fit that, not redesign it.
- **linny already solved authentication** in
  `linny-mcp-server/internal/auth`: records of `{name, hash, scopes}` where
  `hash` is hex SHA-256 of the raw token, compared with a constant-time
  comparison that never early-exits, behind a single `ErrUnauthorized` for every
  failure mode, and a `GenerateToken` producing 32 random bytes as base64url.
  Two services on one host should not authenticate differently.
- **The query layer is half there.** `dashboard/services.py` has `_paginate`,
  `get_overview`, `get_hn_stories`, `get_hn_comments`, `get_github_stars` — all
  pagination-shaped, all parsing the stored JSON body. There is no search and no
  aggregation, which is most of what the tools need.

## Goals / Non-Goals

**Goals:**

- A tool set a model can use without a manual: obvious names, descriptions that
  say what comes back, bounded results.
- The endpoint is safe to expose: authenticated, read-only, and unable to
  disclose anything through its unauthenticated health check.
- Behaves like linny where a host operator has to reason about both.

**Non-Goals:**

- Write tools. Nothing about "what do I care about" needs mutation, and the
  endpoint is the one thing reachable from outside the mesh.
- The interest graph (`startaste-gnw6`). Its first tool would be the 156
  starred-and-upvoted repos; that belongs with the graph, and adding a
  cross-source join here would quietly start it.
- OIDC or multi-user scoping. Records carry a name so the log can say who
  called, but this is a single-person endpoint.
- Semantic search. Text matching over names, descriptions and titles first; if
  it proves too blunt, embeddings are a separate change.

## Decisions

**Streamable HTTP, and therefore ASGI in its own process.** The transport the
Python SDK offers for remote clients is streamable HTTP, which is Starlette/ASGI;
the dashboard is Flask/WSGI. Rather than adapt one into the other, they run as
separate units on separate ports, as `nixos-service` already does for sync and
the dashboard. Alternative considered: stdio transport, which is simpler but
local-only and cannot serve Claude Mobile.

**A shared query module, not more functions in `dashboard/services.py`.** Two
consumers now need the same queries, and the dashboard package is the wrong home
for something the MCP server depends on. Move the query functions to a
`startaste/queries.py` and let both call it; the dashboard keeps its
presentation-shaped wrappers. This is a refactor with no behaviour change, so
the dashboard's existing tests are the safety net.

**Read-only database connection, enforced by SQLite.** Opening with
`mode=ro` in the connection URI means a write is refused by the database, not by
application discipline — the property survives a future tool that forgets. The
cost is that a missing database can no longer be created on demand, which is why
a missing file is a clear startup error instead. WAL (shipped in
`sqlite-wal-mode`) is what lets this connection read while sync writes.

**Seven small tools rather than a few polymorphic ones.** `top_topics`,
`top_languages` and `top_domains` could be one tool with a dimension enum, but
three obvious tools cost a few hundred tokens of schema and remove a chance for
the model to pass the wrong dimension. Search is split by source because the
filters genuinely differ (language and topic mean nothing for an HN title).

**Every result is bounded and says so.** Each search takes a limit with a
default, and returns the total it matched alongside the items, so a model can
tell the difference between "these are all of them" and "there are more". An
unbounded tool over 2975 repos would blow a context window on one call.

**Token records mirror linny's format exactly**, including the field names, so
an operator reading `/run/agenix/startaste-mcp-tokens` sees the same shape as
the linny file next to it. `startaste mcp-token` prints the raw token once and
the record to paste; nothing stores the raw value.

**`scopes` is accepted and ignored for now.** The field exists in the record
format because linny's does and because every tool being read-only makes scopes
moot today. Parsing it now means adding write tools later does not need a token
file migration.

## Risks / Trade-offs

- **An internet-reachable endpoint over a personal dataset.** Mitigated in
  layers rather than one: the service binds the mesh only, durer proxies just
  `/mcp`, tokens are hashed and agenix-encrypted, the connection is read-only,
  and a leaked token exposes reading a taste database — not the host, not a
  write path.
- **The health endpoint is unauthenticated by requirement.** It must therefore
  say nothing but liveness — no counts, no last-sync time, nothing that profiles
  the owner. Stated as a scenario so a future "helpful" addition to it fails
  review.
- **Text search over descriptions may be too blunt** for questions like "find
  my Rust CLI tools" → the language and topic filters carry most of that weight,
  and 38% of stars have no topics, which is a known gap logged in
  `startaste-gnw6` rather than solved here.
- **Moving query functions touches the dashboard.** A pure move, but it is the
  one part of this change that can break something already working → the
  dashboard's existing tests must pass unchanged, and that is a task rather than
  an assumption.
- **Two new dependencies** (`mcp`, `uvicorn`) on a project that has been
  deliberately small. Both are in nixpkgs (1.26.0, 0.40.0) so packaging is not a
  risk; the exposure is upstream churn in a young SDK → pinned through nixpkgs
  like everything else.
- **A read-only connection is a second connection shape** in `db.py`, which has
  so far had exactly one → keep it as an explicit alternative opener rather than
  a flag threaded through `init_database`.

## Migration Plan

1. Extract the query module and prove the dashboard is unaffected.
2. Add the authenticator and `mcp-token`, with tests for the failure modes,
   before anything is served.
3. Add the server and tools; verify locally over HTTP with a real token.
4. Add the module option and extend the VM test.
5. Then `deploy-startaste-dapperehaan` group 5 can proceed: DNS, vhost, token,
   client.

Rollback is not enabling the unit; the other two surfaces are untouched.

## Open Questions

- Whether search should match the stored description text or only names. Starting
  with both and a limit; if precision is poor in practice, narrowing it changes
  no requirement and no task.

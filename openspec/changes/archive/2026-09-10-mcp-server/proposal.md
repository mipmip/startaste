<!-- Epic: .beans/startaste-qbtu--mcp-server.md -->

## Why

The data startaste collects is only reachable through a local dashboard. The
point of collecting it is to be able to ask questions of it — "what do I care
about", "find news about my topics" — and the client that answers those
questions is Claude, not startaste.

An MCP endpoint makes the collection queryable by Claude Online and Claude
Mobile. It is the last piece of the dapperehaan deployment: `mipnix` change
`deploy-startaste-dapperehaan` has the hosting worked out
(`taste.pimsnel.com/mcp`, TLS on durer, nebula, agenix tokens) and its group 5
is blocked only on this server existing.

The reasoning stays with the client. startaste exposes retrieval and
aggregation; Claude decides what to do with them. That keeps this change a data
surface rather than an inference pipeline.

## What Changes

- Add an MCP server exposing the collection over the **streamable HTTP**
  transport, served by `startaste mcp` with `--host`, `--port` and
  `--tokens-file`.
- Serve two endpoints: `/mcp` requiring `Authorization: Bearer`, and
  `/healthz` requiring nothing, so a reverse proxy and monitoring can probe it.
- Authenticate against hashed token records in a file — hex SHA-256 of the raw
  token, compared in constant time, with a single indistinguishable failure for
  missing, malformed, unknown and wrong tokens. Mirrors
  `linny-mcp-server/internal/auth`, so both services on the host behave the
  same way. Add `startaste mcp-token` to mint a token and print its record.
- Expose **seven read-only tools**:
  - `search_stars(query, language, topic, limit)` — over repo name and description
  - `search_upvotes(query, item_type, limit)` — over HN titles
  - `get_item(source, id)` — one full record
  - `overview()` — per-source counts and last sync time
  - `top_topics(limit)`, `top_languages(limit)`, `top_domains(limit)` — the
    aggregations that make "what do I care about" answerable
- Open the database **read-only** in the MCP server. It is the one surface
  reachable from outside the mesh, and it has no reason to write. A missing
  database fails with a clear "run startaste sync first" error rather than
  creating an empty one.
- Add `services.startaste.mcp.*` to the NixOS module (`enable`,
  `listenAddress`, `port`, `tokensFile`), the piece deliberately deferred by
  `nixos-service-module` until this server existed. Defaults to loopback like
  the dashboard.
- Add `mcp` and `uvicorn` dependencies (both in nixpkgs: 1.26.0 and 0.40.0).

## Capabilities

### New Capabilities
- `mcp-server`: the MCP surface — transport, the two endpoints, token
  authentication, the tool set and its read-only guarantee.

### Modified Capabilities
- `nixos-service`: gains a requirement for the MCP unit, alongside the existing
  sync and dashboard units. Additive — no existing requirement changes.

## Impact

- `startaste/mcp/` — new package: the server, the tool definitions, the token
  authenticator.
- `startaste/dashboard/services.py` — the existing query layer has pagination
  helpers (`get_overview`, `get_hn_stories`, `get_github_stars`) but no search
  and no aggregation. Search and the three aggregations are new query functions;
  where they belong (a shared query module vs. the dashboard package) is a
  design decision.
- `startaste/cli.py` — `mcp` and `mcp-token` subcommands.
- `startaste/db.py` — a read-only open path.
- `requirements.txt`, `flake.nix` — the two new dependencies.
- `nix/module.nix`, `nix/tests/module.nix` — the MCP unit and its VM coverage.
- Unblocks `mipnix` change `deploy-startaste-dapperehaan` group 5.
- Deliberately out of scope: the interest graph and its cross-source edges
  (`startaste-gnw6`) — the first tool it would add is the 156 starred-and-upvoted
  repos, and that belongs with the graph work, not here. Also out of scope: any
  write tool, and OIDC (the token interface is an implementation detail behind
  one authenticator, so it can be added later without touching callers).

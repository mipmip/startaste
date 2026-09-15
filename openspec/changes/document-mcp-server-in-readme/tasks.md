# Tasks — document the MCP server in the README

Bean: [startaste-sea0](../../../.beans/startaste-sea0--update-readme-with-new-mcp-server-functionality.md)
Schema: [openspec-tinychange-schema](https://github.com/speclib/openspec-tinychange-schema)

No spec delta (`skip_specs: true`): the behaviour is already specified in
`openspec/specs/mcp-server/spec.md` and `openspec/specs/cli/spec.md`; only the
README lags behind.

## 1. Implementation

- [x] 1.1 Add an **MCP server** subsection to "How to use" in `README.md`,
      after "Dashboard", covering:
      - what it is — a read-only MCP endpoint over the synced collection,
        streamable HTTP, safe to put behind an HTTPS reverse proxy
      - `startaste mcp-token --name <name>` to mint a token, and the
        `{"name": ..., "hash": ..., "scopes": ["read"]}` record to paste into
        the tokens file (raw token shown once, only hashes are stored)
      - `startaste mcp --tokens-file <path>` with `--host` (default
        `127.0.0.1`), `--port` (default `8766`) and repeatable `--allowed-host`
        for the public hostname a reverse proxy forwards
      - the two paths: `/mcp` (bearer token required) and `/healthz`
        (unauthenticated liveness)
      - the tools a client gets: `search_stars`, `search_upvotes`, `get_item`,
        `overview`, `top_topics`, `top_languages`, `top_domains`
      - that the database is opened read-only and `startaste sync` must have
        run first
- [x] 1.2 Add the MCP port to the existing tables/prose where the dashboard's
      port and env vars are listed, so the two servers are not confused.
- [x] 1.3 Add a `### Changed` note under `## [Unreleased]` in `CHANGELOG.md`.

## 2. Verification

- [x] 2.1 Every command, flag, default and tool name in the new section is
      checked against `startaste/cli.py` and `startaste/mcp/server.py` —
      run `startaste mcp --help` and `startaste mcp-token --help` and diff the
      documented defaults against the real output.
- [x] 2.2 Markdown tables added or touched are space-padded to aligned borders
      (repo style) and the rendered README has no broken links or stray fences.

### How it was verified

`startaste mcp --help` and `startaste mcp-token --name laptop` were run in the
nix devshell; the documented defaults (`--host 127.0.0.1`, `--port 8766`,
required `--tokens-file`, repeatable `--allowed-host`) and the record shape
`{"name", "hash", "scopes": ["read"]}` match their real output.

A checker script then re-derived the facts from source rather than from that
run: it parses `startaste/cli.py` with `ast` to compare the `mcp` subparser's
flags, defaults, `required` and `action="append"` against what the README
claims, greps `@mcp.tool()` definitions out of `startaste/mcp/server.py` to
confirm the seven documented tool names are exactly the seven that exist, and
asserts the `/healthz` route, the `protected_prefix="/mcp"` auth scope and the
`open_readonly` database call the README describes. It also checks every
markdown table for equal-length borders, consistent column counts and the
90-char limit, and that code fences are balanced. Result: PASS — 5 tables,
7 tools, 4 mcp flags.

The pytest suite was not run: the machine's root filesystem is full, so
`nix develop` could not materialise the devshell. No Python changed here.

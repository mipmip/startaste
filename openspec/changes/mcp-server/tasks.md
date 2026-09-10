## 1. Shared query layer

- [ ] 1.1 Extract the query functions from `startaste/dashboard/services.py`
      into `startaste/queries.py` and have the dashboard call them; verify the
      existing dashboard and service tests pass unchanged (a pure move)
- [ ] 1.2 Add search queries — stars by text over full name and description with
      optional language and topic filters, HN items by text over title with an
      optional item-type filter — each taking a limit and returning the total
      matched; verify tests covering a match, no match, each filter, the limit,
      and an empty database
- [ ] 1.3 Add aggregation queries for top topics, top languages and top upvoted
      domains, ordered by count; verify tests assert ordering, the limit, and
      that items missing the field are skipped rather than counted as null
      (38% of stars have no topics)

## 2. Read-only database access

- [ ] 2.1 Add an explicit read-only opener in `startaste/db.py` using a SQLite
      URI with `mode=ro`; verify a test that a write on that connection is
      refused by the database itself
- [ ] 2.2 Verify a test that opening read-only against a missing file raises a
      clear "run startaste sync first" error and creates no file
- [ ] 2.3 Verify a test that a read on the read-only connection succeeds while
      another connection holds an open write transaction (WAL, from
      `sqlite-wal-mode`)

## 3. Token authentication

- [ ] 3.1 Add a token authenticator reading records of `{name, hash, scopes}`
      where hash is hex SHA-256, matching
      `linny-mcp-server/internal/auth/static.go`; compare in constant time
      without early exit and return one indistinguishable failure for missing,
      malformed, unknown and wrong tokens; verify a test per failure mode
      asserting identical outcomes
- [ ] 3.2 Verify tests that a malformed record never authenticates and does not
      stop the valid records in the same file from working
- [ ] 3.3 Add `startaste mcp-token` minting a token with at least 256 bits of
      entropy, printing the raw token once plus the record to add; verify a test
      that the printed record's hash matches the printed token and that the raw
      token is not written anywhere
- [ ] 3.4 Verify that starting the server with a missing or unreadable token
      file exits with a clear error rather than serving unauthenticated

## 4. The MCP server

- [ ] 4.1 Add `startaste/mcp/` serving streamable HTTP with `/mcp` behind the
      authenticator and an unauthenticated `/healthz`; verify tests that `/mcp`
      without a token is rejected, with a valid token is served, and that
      `/healthz` responds with liveness only and discloses no collection data
- [ ] 4.2 Register the seven tools — `search_stars`, `search_upvotes`,
      `get_item`, `overview`, `top_topics`, `top_languages`, `top_domains` —
      each with a description stating what it returns; verify a test that an
      initialised client lists exactly these with descriptions present
- [ ] 4.3 Verify per-tool tests against a seeded database: results are bounded
      by the limit and report the total matched, `get_item` returns a clear
      not-found for an unknown id, and every tool returns an empty result rather
      than failing on an empty database
- [ ] 4.4 Add the `mcp` subcommand with `--host` (default `127.0.0.1`),
      `--port`, `--tokens-file`; verify the default bind is loopback and that
      arguments reach the server
- [ ] 4.5 Add `mcp` and `uvicorn` to `requirements.txt` and the flake's package
      dependencies; verify `nix build .#default` succeeds and the built binary
      can start the MCP server

## 5. NixOS module

- [ ] 5.1 Add `services.startaste.mcp.{enable,listenAddress,port,tokensFile}`
      creating a hardened unit like the others, defaulting to loopback, with
      `tokensFile` typed as a path; verify by evaluating configurations that the
      unit is independent of the other two, that arguments reach ExecStart, and
      that a token value cannot appear in the store
- [ ] 5.2 Extend `nix/tests/module.nix`: with a token file provisioned in the
      VM, `/healthz` answers unauthenticated, `/mcp` rejects an unauthenticated
      request, and a request with the valid token is accepted; verify the VM
      test passes

## 6. Verification

- [ ] 6.1 Live check outside the VM: start the server against a real synced
      database with a minted token, and call each of the seven tools with a real
      MCP client, confirming plausible results from real data
- [ ] 6.2 `pytest tests/ -v` passes, coverage does not regress, and
      `nix build .#default` plus `nix flake check` succeed
- [ ] 6.3 Update CHANGELOG.md under Unreleased
- [ ] 6.4 Confirm `mipnix` change `deploy-startaste-dapperehaan` group 5 needs
      no edits beyond what it already specifies (port 8766, `tokensFile`,
      `taste.pimsnel.com` vhost), and note any drift

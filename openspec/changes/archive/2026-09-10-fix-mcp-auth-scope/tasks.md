# Tasks — fix-mcp-auth-scope

Schema source: <https://github.com/speclib/openspec-tinychange-schema>

## Context

A Claude connector pointed at a deployed instance failed with *"Couldn't connect
to the server. Check that the URL points to a valid MCP server."* Probed against
a working reference (linny-mcp, the service `auth.py` is written to behave
identically to) on the same client:

| probe                                        | startaste | linny |
|----------------------------------------------|-----------|-------|
| `/healthz`                                   | 200       | 200   |
| `POST /mcp` no token                         | 401 + `WWW-Authenticate: Bearer` | 401, no header |
| `/.well-known/oauth-protected-resource`      | **401**   | 404   |
| `/.well-known/oauth-authorization-server`    | **401**   | 404   |
| `/mcp/`                                      | **401**   | 404   |

`build_app` called `app.add_middleware(...)`, which wraps the whole ASGI app, so
the guard ran before routing and every unserved path was answered 401 instead of
reaching the router. Combined with the `WWW-Authenticate: Bearer` challenge, a
client following the MCP authorization flow was told the endpoint is
OAuth-protected, went looking for protected-resource metadata, and got 401 there
too — leaving it unable to complete discovery or to rule OAuth out, so it gave up
before ever using its configured token.

## 1. Implementation

- [x] 1.1 Scope `BearerAuthMiddleware` to a `protected_prefix` (default `/mcp`)
      instead of guarding everything but `open_paths`, matching `/mcp` and
      `/mcp/...` but not `/mcpsomething`, so unserved paths reach the router and
      404.
- [x] 1.2 Drop the `WWW-Authenticate: Bearer` header from the rejection — a bare
      challenge names no realm and points at no metadata, so it tells a client
      nothing while sending it down the dead end above.
- [x] 1.3 Document both in the class docstring and in `build_app`, so the next
      reader does not "tidy" the guard back to wrapping the whole app.

## 2. Verification

- [x] 2.1 `test_unserved_paths_are_not_found_not_unauthorized` covers three
      `/.well-known/` OAuth discovery paths plus an unrelated path; all 404.
- [x] 2.2 `test_rejection_carries_no_authentication_challenge` asserts no
      `WWW-Authenticate` on a rejected `/mcp` request; the existing
      `test_mcp_without_a_token_is_rejected` was updated to drop its assertion of
      that header, since the header is deliberately gone.
- [x] 2.3 `test_a_path_merely_prefixed_with_mcp_is_not_the_endpoint` pins the
      prefix match so `/mcpsomething` is not treated as the endpoint.
- [x] 2.4 `test_an_unserved_path_discloses_nothing` keeps the security property:
      a 404 still reveals nothing about the collection.
- [x] 2.5 Existing auth behaviour unchanged: valid token served, wrong token
      rejected, `/healthz` open, failures indistinguishable.
- [x] 2.6 Full suite: `pytest tests/ --cov=startaste` → **146 passed, 95%
      total coverage** (`startaste/mcp/server.py` 92%).

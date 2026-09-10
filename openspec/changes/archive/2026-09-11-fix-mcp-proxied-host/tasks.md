# Tasks — fix-mcp-proxied-host

Schema source: <https://github.com/speclib/openspec-tinychange-schema>

## Context

With a valid token, a request through the HTTPS reverse proxy came back:

```
HTTP/2 421
Invalid Host header
```

`build_mcp()` constructed `FastMCP("startaste", instructions=…)` without a `host`,
so FastMCP used its default `127.0.0.1` — and FastMCP *auto-enables* DNS-rebinding
protection when its host is loopback, with `allowed_hosts` limited to loopback
patterns. `serve()` passes the real bind address to uvicorn only, never to
FastMCP, so that default stood in every deployment. Behind a proxy the forwarded
`Host: taste.pimsnel.com` matched nothing and the transport answered 421.

The fix widens the allow-list to what the deployment actually serves. It does
**not** disable the defence.

Note on why the sibling change `fix-mcp-auth-scope` did not surface this: it was
verified by probing a locally-run server on `127.0.0.1`, which is exactly the one
Host value the default allow-list accepts. Only a proxied request could have
caught it — hence the tests below set the `Host` header explicitly.

## 1. Implementation

- [x] 1.1 Add `transport_security(allowed_hosts)` building
      `TransportSecuritySettings` with rebinding protection ON, loopback always
      allowed, and each declared hostname added as a host and as an http/https
      origin — bare and with `:*`, since a proxy may or may not include the port.
- [x] 1.2 Thread it through: `build_mcp(allowed_hosts)`,
      `build_app(tokens_file, allowed_hosts)`, and `serve(..., allowed_hosts)`,
      which also allows its own `listenAddress:port` so direct access needs no
      declaration.
- [x] 1.3 Add a repeatable `--allowed-host` CLI flag whose help says why it is
      needed behind a proxy.
- [x] 1.4 Add `services.startaste.mcp.publicHostname` to the NixOS module, passed
      through as `--allowed-host` only when set.

## 2. Verification

- [x] 2.1 `test_proxied_public_host_is_accepted_when_declared` — a declared
      hostname in the `Host` header is no longer 421.
- [x] 2.2 `test_proxied_public_host_with_a_port_is_accepted` — same with `:443`.
- [x] 2.3 `test_undeclared_host_is_still_refused` — asserts **421** for an
      undeclared host, proving the defence still holds and the pair is not
      vacuous.
- [x] 2.4 `test_loopback_needs_no_declaration` — loopback works unconfigured.
- [x] 2.5 `test_declared_host_is_also_an_allowed_origin` and
      `test_rebinding_protection_stays_enabled`.
- [x] 2.6 `test_allowed_host_is_repeatable_and_passed_through` — CLI plumbing.
      The two existing CLI tests that pinned the exact kwargs were updated to
      include `allowed_hosts`, since the signature deliberately changed.
- [x] 2.7 Full suite: **153 passed, 95% coverage**.

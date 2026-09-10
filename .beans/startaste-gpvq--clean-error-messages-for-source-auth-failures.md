---
# startaste-gpvq
title: clean error messages for source auth failures
status: completed
type: bug
priority: normal
created_at: 2026-09-10T11:14:05Z
updated_at: 2026-09-10T19:10:01Z
---

Credential problems are reported inconsistently: a *missing* credential exits
cleanly, an *invalid* one dumps a traceback.

- Missing token: `Error: GITHUB_TOKEN not set in environment or .env` (clean
  `SystemExit`, from `startaste/sources/github/__init__.py`).
- Invalid token: `requests.exceptions.HTTPError: 401 Client Error: Unauthorized
  for url: https://api.github.com/user/starred?page=1&per_page=100` plus a full
  traceback, because `resp.raise_for_status()` in
  `startaste/sources/github/api.py` is uncaught.
- HN login failure raises a bare `Exception("Hacker News authentication
  failed!")` from `Req.login`, which reaches the user the same way.

Reproduce: `env GITHUB_TOKEN=ghp_invalid startaste sync github`.

Wanted: a 401/403 from any source should say which credential was rejected and
how to renew it, in the same shape as the missing-credential message, and with
no traceback. Distinguish "rejected" from "network / rate-limited" so a
transient failure is not reported as a bad token. One source failing to
authenticate should not abort the sync of the other configured sources.

## Summary of Changes

Shipped as openspec change `clean-source-auth-errors`, archived at
`openspec/changes/archive/2026-09-10-clean-source-auth-errors`.

`startaste/sources/base.py` gains `SourceError` with `SourceAuthError` (carrying
the source and the variables it uses) and `SourceUnavailableError`, so a caller
tells the two apart by type rather than by matching messages.

GitHub translates in `api.py`: 401 and a plain 403 become a rejected token
naming `GITHUB_TOKEN` and where to renew it; a 403 carrying
`X-RateLimit-Remaining: 0` becomes rate limiting; connection failures and retry
exhaustion become unreachable. HN's bare `Exception` on a refused login becomes
`SourceAuthError` naming `HN_COMMENTS_ACCT` and `HN_COMMENTS_PW`, with an
unreachable login request reported separately.

`run_sync` catches `SourceError` per source, logs one clean line, continues with
the remaining sources, and exits non-zero at the end naming what failed. An
exception that is *not* a `SourceError` still propagates — a genuine bug must
not be flattened into a tidy message.

Verified live against the real services. Before: a traceback ending in
`requests.exceptions.HTTPError: 401 Client Error`. After, same command:

    Syncing github...
    Error: GITHUB_TOKEN was rejected (401). Renew it at github.com/settings/tokens
    Sync failed for: github.

and with both sources' credentials wrong, HN fails first and GitHub is still
attempted — where before the first failure aborted the rest:

    Syncing hn...
    Error: Hacker News refused the account and password
    Syncing github...
    Error: GITHUB_TOKEN was rejected (401). Renew it at github.com/settings/tokens
    Sync failed for: hn, github.

Exit status 1, no tracebacks in either case. 139 tests pass, coverage 95%. Four
capabilities updated: `cli` (the shape of a credential error), `sync` (partial
failure and exit status), `github-source` and `hn-sync` (each source's mapping).

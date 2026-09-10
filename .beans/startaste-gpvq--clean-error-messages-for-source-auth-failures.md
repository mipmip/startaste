---
# startaste-gpvq
title: clean error messages for source auth failures
status: todo
type: bug
created_at: 2026-09-10T11:14:05Z
updated_at: 2026-09-10T11:14:05Z
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

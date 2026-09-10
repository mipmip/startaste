## 1. Implementation

- [x] 1.1 Add source-failure exception types next to the `Source` protocol —
      one for rejected credentials (carrying the source and the variables it
      uses) and one for a source that could not be reached or was rate-limited
      — so a caller can tell the two apart without matching on messages
- [x] 1.2 GitHub: catch the HTTP error from `resp.raise_for_status()` in
      `startaste/sources/github/api.py` and translate it — 401 to rejected
      credentials, 403 to rate limiting when the response says the limit is
      exhausted and to rejected credentials otherwise, connection and retry
      exhaustion to unreachable
- [x] 1.3 HN: replace the bare `Exception("Hacker News authentication
      failed!")` in `Req.login` with the rejected-credentials type, and report a
      login request that could not be completed as unreachable
- [x] 1.4 `run_sync` in `startaste/sync.py`: catch a source failure, log it as
      one clean line naming the source and what to do, carry on with the
      remaining sources, and exit non-zero at the end if any source failed —
      naming which ones

## 2. Verification

- [x] 2.1 Reproduce the bug first and keep the output: `env
      GITHUB_TOKEN=ghp_invalid startaste sync github` currently ends in
      `requests.exceptions.HTTPError: 401 ...` with a traceback; after the
      change it must be one clean line naming `GITHUB_TOKEN`, with a non-zero
      exit and no traceback
- [x] 2.2 Tests with mocked responses for each mapping: 401, 403 with the rate
      limit exhausted, 403 without it, and a connection error — asserting the
      failure type and that no traceback reaches the user
- [x] 2.3 Test that a run with two configured sources, the first failing,
      still syncs the second, exits non-zero, and names the failed source
- [x] 2.4 Test that HN refusing the login, and HN not confirming the account,
      both surface as rejected credentials naming `HN_COMMENTS_ACCT` and
      `HN_COMMENTS_PW`
- [x] 2.5 `pytest tests/ -v` passes and coverage does not regress
- [x] 2.6 Update CHANGELOG.md under Unreleased

## Notes

- Schema source: https://github.com/speclib/openspec-tinychange-schema
- Bean [[startaste-gpvq]].
- Four capabilities move, which is more than a typical tinychange: `cli` owns
  the shape of a credential error, `sync` owns what happens to the other
  sources, and each source owns its own translation. No proposal or design is
  needed because none of the decisions are open — the bean states the wanted
  behaviour and the mapping is mechanical — but it is worth knowing the change
  is wider than it is deep.
- Current state, read from the code: `github/api.py:38` calls
  `resp.raise_for_status()` with nothing catching it; `hn/scraper.py` raises a
  bare `Exception` on a refused login; `sync.py:22-24` loops
  `for source in sources: source.sync()` with no handler, so the first failure
  aborts every source after it.
- The retry adapter already retries 429 and 5xx five times, so those surface as
  retry exhaustion rather than a raw status — that is the "unreachable" case,
  not a credential one.
- GitHub returns 403 for both a forbidden token and an exhausted rate limit, so
  the response has to be inspected rather than the status alone. This is the one
  place the mapping is not a straight status lookup.

## 1. Implementation

- [x] 1.1 Add a pre-flight check that jj can operate in the checkout (`jj root`)
      and that git sees a repository, after the tool-on-PATH loop and before
      anything is written; the message should say how to fix it
- [x] 1.2 Stop the coverage-badge rewrite of README.md from running during a
      dry run — it currently runs unconditionally at the test step, before the
      dry-run branch prints "No changes made"

## 2. Verification

- [x] 2.1 `./release.sh patch --dry-run` on a clean working tree leaves it
      clean: confirm with `jj status` before and after
- [x] 2.2 Confirm the VCS predicate is right: `jj root` succeeds in this
      checkout and fails outside a jj repo
- [x] 2.3 Confirm the guard fires and writes nothing when jj cannot operate,
      by running the script's pre-flight in a checkout with no jj repo

## Notes

- Schema source: https://github.com/speclib/openspec-tinychange-schema
- Bean [[startaste-2j0n]]. The repository half is already resolved: the
  checkout is now colocated (`.jj` and `.git` both present, `jj root` succeeds,
  and the existing git history is visible in `jj log`), so `release.sh` can run
  its jj steps. What remains is the soundness problem the bean identified — a
  tool check that passes while the operation cannot work, with the VCS steps
  sequenced after VERSION and the changelog are rewritten.
- The dry-run leak was found while verifying this: `sed -i` on README.md at the
  test step runs before the dry-run branch, so a dry run modifies the repo and
  then reports "No changes made". That contradicts the `release` capability
  shipped in `backfill-live-specs`, so it is fixed here rather than filed.
- Not changed: `release.sh` uses `jj describe` + `jj new`, while
  `mipnix`'s `jj-workflow-aliases` capability says not to duplicate that motion
  in *aliases* since `jj commit` exists. The two are equivalent and the script
  is not an alias, so it is left alone.

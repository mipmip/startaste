---
# startaste-lvbt
title: release.sh does not push the release commit to main
status: todo
type: bug
priority: high
created_at: 2026-09-10T19:45:54Z
updated_at: 2026-09-10T19:45:54Z
---

`release.sh` tags and publishes the release but does not get the release commit
onto `main`. Observed cutting v3.1.0:

```
step 6: jj git push --all
  Warning: Refusing to create new remote tag v3.1.0@origin
  Nothing changed.
step 7: git push origin v3.1.0   -> [new tag] v3.1.0

after the script finished:
  refs/tags/v3.1.0  36d75faec5ce   <- the release commit
  refs/heads/main   4e378d797adf   <- its parent
```

`jj describe` + `jj new` leave the `main` bookmark pointing at the release
commit's *parent*, so `jj git push --all` has nothing to advance and says
"Nothing changed". The tag push carries the commit object to the remote, so the
GitHub release is valid — but `main` does not contain the release commit until
someone runs `jj tug && jj git push` by hand, which is what I did.

This makes the `release` capability's "Push: commits and tags both reach the
remote" scenario false (`openspec/specs/release/spec.md`).

Fix: move the bookmark before pushing, i.e. `jj tug` (or
`jj bookmark set main -r @-`) between the `jj new` and the push, and prefer an
explicit `jj git push` for the bookmark over `--all`, which also produces the
misleading "Refusing to create new remote tag" warnings for every historical
tag.

Related: [[startaste-2j0n]] fixed the pre-flight half of release.sh. This is a
second, independent flaw in the same script — worth checking the remaining steps
against what they actually do rather than what they read like.

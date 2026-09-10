---
# startaste-2j0n
title: release.sh requires jj but the repo is plain git
status: completed
type: bug
priority: high
created_at: 2026-09-10T18:47:24Z
updated_at: 2026-09-10T18:56:21Z
---

`release.sh` cannot run in this checkout: it requires `jj`, but the repository
is plain git.

- line 59 checks `for tool in jj git gh pytest`, which passes because jj is
  installed
- lines 146-155 then run `jj describe -m "release vX.Y.Z"`, `jj new`,
  `git tag`, `jj git push --all`
- `jj status` in the repository root reports "There is no jj repo in '.'"

So a release fails part-way: the pre-flight passes, VERSION and CHANGELOG.md are
modified, and then `jj describe` fails — leaving the working tree half-released.
CLAUDE.md also says "We use jj", which no longer matches the repository.

Decide which is true and make them agree:

- run `jj git init --colocate` so the repo is what the script and CLAUDE.md
  assume, or
- rewrite the release steps in `release.sh` to use git (`git commit`,
  `git tag`, `git push`) and drop jj from the tool check and from CLAUDE.md

Either way the pre-flight should verify the VCS is usable, not just that the
binary exists — a tool check that passes while the operation cannot work is what
made this failure land mid-release.

The `release` capability (`openspec/specs/release/spec.md`, from
`backfill-live-specs`) describes the script as written, jj included. Whichever
way this is resolved, that spec needs a MODIFIED delta.

## Summary of Changes

Resolved in two halves. The repository half was done outside this change: the
checkout is now colocated (`.jj` and `.git` both present, `jj root` succeeds,
and the pre-existing git history is visible in `jj log`), so CLAUDE.md's "we use
jj" and `release.sh`'s jj steps are both true again.

The code half shipped as openspec change `release-preflight-vcs`, archived at
`openspec/changes/archive/2026-09-10-release-preflight-vcs`.

`release.sh` now verifies the VCS is *usable* rather than merely installed:
`jj -R "$SCRIPT_DIR" root` and a `git rev-parse --git-dir` check run after the
tool-on-PATH loop and before anything is written, and the error says to run
`jj git init --colocate`. Verified in a copied checkout with no jj repo: exit
status 1, VERSION and CHANGELOG.md unchanged.

A second defect surfaced while verifying this and is fixed here: the
coverage-badge `sed -i` on README.md ran unconditionally at the test step,
before the dry-run branch printed "No changes made", so `--dry-run` modified the
repository. It is now guarded by the dry-run flag. Verified: a dry run leaves
README.md untouched, and it would certainly have changed it — the badge still
says 83% while the suite reports 94%.

Both requirements in the `release` capability were updated by MODIFIED delta:
pre-flight now covers a tool that is present but cannot operate, and the dry-run
requirement now states that no file is written, including files the script
touches as a side effect of its own checks.

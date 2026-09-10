---
# startaste-2j0n
title: release.sh requires jj but the repo is plain git
status: todo
type: bug
priority: high
created_at: 2026-09-10T18:47:24Z
updated_at: 2026-09-10T18:47:24Z
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

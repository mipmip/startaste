## Context

See proposal.md — Why. The material is fourteen archived capability deltas
written across six changes between 2026-05-12 and 2026-09-10. They were never
reconciled with each other, so some describe behaviour that a later change
replaced without a formal delta.

The mechanism is ordinary: this change's `specs/` deltas are `ADDED`
requirements, and archiving applies them, creating the live specs. No special
tooling is involved — the only unusual thing is that the specs *are* the
deliverable, so verification means checking each requirement against the code
rather than running a new feature.

## Goals / Non-Goals

**Goals:**

- Every capability with a live spec states what the code does today.
- Fewer capabilities than archived deltas, where two deltas described one thing.
- Future changes can write `MODIFIED` deltas instead of being blocked.

**Non-Goals:**

- Changing any behaviour. Where text and code disagree, the code wins and the
  text is corrected.
- Fixing the one real code problem this surfaced (`release.sh` requires jj in a
  git-only checkout). Recorded as a bean; fixing it here would smuggle a
  behaviour change into a documentation change.
- Backfilling the archived `paths` delta, which the live `paths` spec already
  supersedes.
- Retro-specifying history. Requirements describe the current contract, not the
  sequence of changes that produced it.

## Decisions

**Merge deltas that describe one capability.** `cli` absorbs `cli-sources`, and
`export` absorbs `export-sources`. Those pairs exist because a later change
added requirements to an area it had not created, and naming the addition
separately was the cheapest thing to do at the time. Keeping them separate would
preserve the exact problem this change exists to remove: two specs claiming one
subject, neither complete.

Similarly `serve-command` and `dashboard-views` become one `dashboard`, and the
two migration capabilities (`db-migration`, `db-rename`) become requirements of
the existing `database` capability, because they are part of what happens when
the database is opened.

**`service-layer` becomes `queries`, not a renamed copy.** Its subject moved: it
described the query functions as a dashboard-internal layer whose value was
being "reusable by a future API route". `mcp-server` moved them to
`startaste/queries.py` and made that future concrete. Writing the old text as a
live spec would encode a location that is now wrong, so the capability is named
for what it is, and the shared-not-owned property is stated as a requirement in
its own right.

**Drop `cli`'s "Installable binary via flake".** The live `nixos-service`
capability specifies the flake surface — module, overlay, per-system packages —
in far more detail. Two capabilities asserting the same thing is the failure
mode being fixed, and the more specific one wins.

**Narrow `sync` to orchestration.** The archived `sync` mixed cross-source
orchestration ("only configured sources", "metadata only for items that lack
it") with HN scraping mechanics ("scraping all pages until HN returns an empty
page"). The mechanics are wrong now — `fix-hn-upvoted-pagination` replaced page
counting with cursor traversal — and they belong to `hn-sync`, which already
states them correctly. `sync` keeps only what is true of every source.

**Requirements are written against observable behaviour, not code shape.** The
archived text names functions and files (`get_hn_stories(page=2, per_page=50)`,
`startaste/sources/__init__.py`). That is why moving a function invalidated a
spec. The reconciled requirements state what a caller can rely on, so the next
refactor does not silently falsify them.

**`release` is written to match `release.sh`, including jj.** The script really
does commit with jj and tag with git; the spec describing that is correct. What
is wrong is the repository — no jj repo exists, so a release would fail
part-way. Recording the requirement honestly and filing the repo problem
separately keeps the spec a description of intent rather than of a bug.

## Risks / Trade-offs

- **A backfilled requirement could be wrong in a way I did not notice**, which
  would then be treated as the contract → every requirement is checked against
  a named file or an observed behaviour as a task, and the checks are listed
  individually rather than as "review the specs".
- **Merging capabilities loses the mapping to archived deltas.** Someone reading
  the archive will not find a live `cli-sources` → the proposal names each
  merge and each drop explicitly, so the trail is in this change.
- **Nine new specs is a lot of text to keep true.** The mitigation is that they
  are now in the place where a `MODIFIED` delta can update them, which is the
  whole point; the previous state guaranteed drift instead of merely risking it.
- **`testing` and `release` describe process, not runtime behaviour**, and a
  spec is a slightly awkward home for them → they were already capabilities in
  the archive, and dropping them would lose the only written record; they are
  kept but phrased as properties that can be checked.

---
# startaste-h46w
title: resumable full sync via a completion marker
status: todo
type: feature
priority: normal
created_at: 2026-09-10T11:14:05Z
updated_at: 2026-09-10T15:18:26Z
---

A first HN sync takes ~14 minutes (77 listing pages plus metadata for 2288
items). Interrupt it and all scraping progress is lost, because a listing's IDs
are only stored once its walk finishes.

That atomicity is deliberate, from `fix-hn-upvoted-pagination`: saving IDs per
page leaves the database non-empty, which sends the next run down the
incremental path where it stops on the first page of known IDs and silently
abandons the rest of the listing. Verified — interrupting after 9 of 77 pages
left 270 rows, and the next run then walked exactly 1 page and left the
remaining 2018 items permanently unfetched.

To get both progress *and* a sound incremental stop condition, the
full-vs-incremental decision has to stop being inferred from "is the table
empty". Something must record that a listing was walked all the way to its last
page.

Scope to decide in the proposal:

- where that state lives (a small state table, or a marker per source and
  listing) and how it migrates for existing databases
- resuming a partial walk: store the cursor, or re-walk and rely on known IDs
- how it interacts with the metadata phase, which already resumes on its own
  via `list_empty`
- whether GitHub stars need the same treatment (2973 items, same shape)

# Rename & Rebrand: hackerNews-to-json → startaste

## Summary

Rename the project to **startaste** and publish the vision for what it will become: a self-hostable platform for owning your stars, upvotes, and favorites across the web.

The existing code stays as-is. This change is about identity and direction.

## Why

- Platforms like Hacker News, GitHub, Reddit don't let you truly own your curation data
- The current project name (`hackerNews-to-json`) is too narrow for where this is headed
- A clear identity and direction makes it easier to build toward the bigger vision

## What changes

- Rename the project from `hackerNews-to-json` to **startaste**
- Write a new README that communicates the vision, current state, and roadmap
- Update LICENSE with the new project name

## Vision

**startaste** — your stars are your taste.

```
  Sources             Store            Outputs

  HN upvotes ──┐
                ├──▶  SQLite  ──▶  REST API
  GitHub stars ─┘     (yours)      AT Proto feed
  ...more                          JSON export
```

## Scope of this change

1. Update README with new name, vision, and roadmap
2. Update LICENSE (done)

## Non-goals

- Code changes, refactoring, or restructuring
- New features

---
# startaste-ef1p
title: 'CLI restructure: sync and export subcommands'
status: in-progress
type: task
priority: normal
created_at: 2026-05-12T09:00:44Z
updated_at: 2026-05-12T09:01:53Z
blocking:
    - startaste-1r78
---

Restructure startaste from a single-script CLI into a proper CLI with subcommands: `startaste sync` (auto-detects full vs incremental) and `startaste export` (with --format and -s filters). Install as a bin via flake.nix.

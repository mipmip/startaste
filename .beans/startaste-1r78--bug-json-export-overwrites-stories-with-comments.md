---
# startaste-1r78
title: 'Bug: JSON export overwrites stories with comments'
status: todo
type: bug
created_at: 2026-05-12T08:53:11Z
updated_at: 2026-05-12T08:53:11Z
---

In hn2json.py line 291, `json_items["saved_stories"] = Comment.to_dict()` uses the wrong key. It should be `json_items["saved_comments"]`. This means when running with both stories and comments (the default), the comments overwrite the stories in the JSON output. The SQLite DB is unaffected — only the JSON export is broken.

---
# startaste-gnw6
title: interest graph relating github stars and hn upvotes
status: todo
type: feature
created_at: 2026-09-10T15:07:17Z
updated_at: 2026-09-10T15:07:17Z
---

Relate GitHub stars and HN upvotes into one graph of interests, so it can be
queried (and eventually exposed over MCP, [[startaste-qbtu]]) to answer "what do I
care about" and to drive things like "find news about my topics".

The graph is already latent in synced data. Measured 2026-09-10:

- 2975 stars with metadata: 2830 have `language` (73 distinct), 1854 (62%) have
  `topics[]` (5616 distinct)
- 2134 HN stories with metadata, but the HN API gives only `title` and `url` —
  no tags
- `github.com` is the single most-upvoted domain: 357 stories, 356 of which
  point at a specific repo
- **156 of those repos are also starred** — a double signal (upvoted the post
  AND starred the repo) that is a far stronger interest marker than either
  source alone. Examples: `altsem/gitu`, `ahujasid/blender-mcp`,
  `acly/krita-ai-diffusion`, `andmarti1424/sc-im`, `amrdeveloper/gql`

Build it in tiers, cheapest first:

1. SQL joins only, no NLP: star to language, star to topic, hn to domain, and
   the 156 star/upvote edges.
2. URL-based topic inheritance, still no NLP: the 357 HN stories that link to
   github.com inherit `topics[]` and `language` from the repo, so both sources
   end up sharing one topic vocabulary for free.
3. Topic inference for the remaining ~1780 non-GitHub HN titles — embeddings
   (sqlite-vec, sentence-transformers) or an LLM pass. This tier is the main
   reason the project stays in Python.
4. Reasoning stays with the client. Claude asks for topics and does its own
   searching; startaste does not need an inference pipeline.

The hard part is not the graph, it is topic normalization: 5616 distinct topics
over 1854 repos is sparse and dirty — `nix` (138) and `nixos` (91) are one
interest, so are `golang` (103) and `go`, and `rust` the topic versus Rust the
language. 38% of stars have no topics at all, leaving only `language` and
`description`. A synonym map or co-occurrence clustering decides the quality of
everything above. Worth its own exploration before any implementation.

Scale note: ~5k nodes needs no graph database — recursive CTEs over the existing
SQLite are enough.

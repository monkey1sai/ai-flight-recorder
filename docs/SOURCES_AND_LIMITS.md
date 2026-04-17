# Sources and limits

This note captures the practical external constraints that shape the repository design.

## 1. Codex operating assumptions

Use this repository with the assumption that:

- Codex reads `AGENTS.md` before starting work.
- Project-specific lint/test commands should be discoverable from repository guidance.
- Skills are repo-scoped in `.agents/skills/`.
- Local runs should stay in a bounded sandbox by default.
- Research tasks may need live web search, but web content remains untrusted.
- Non-interactive validation runs should prefer read-only mode.
- Config, profiles, and OTel export behavior belong in `.codex/config.toml` or `~/.codex/config.toml`.

## 2. Google Drive constraints

The repository design should assume:

- file search is based on `files.list`
- search behavior depends on official query operators
- Google Docs export has a size limit
- incremental sync should use change tokens and change listing
- push notifications require webhook channels
- audit-style timelines may need Drive Activity data

## 3. arXiv constraints

The repository design should assume:

- real-time search comes from the arXiv API
- paging uses `start` and `max_results`
- repeated calls should be rate-limited politely
- large metadata sync is better handled with OAI-PMH
- metadata can be stored; full-text redistribution is constrained by rights and policy
- the product should link back to arXiv rather than serving copyrighted PDFs by default

## 4. OpenTelemetry constraints

The repository should assume:

- GenAI semantic conventions are still evolving
- agent spans and MCP spans should be mapped deliberately
- a stable internal canonical schema should exist even when exporting OTel-compatible data
- raw prompts / outputs should be controlled separately from trace metadata

## 5. Research rationale for this product

This product is intentionally designed around:

- structured reasoning provenance
- dynamic agent telemetry
- separation between observed evidence and model self-report
- human-readable replay, not hidden-thought claims

## 6. Recommendation

Treat this note as a compact policy summary. The full product intent and implementation details remain in `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`.

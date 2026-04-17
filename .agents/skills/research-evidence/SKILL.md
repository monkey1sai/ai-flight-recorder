---
name: research-evidence
description: Use when a task depends on current external information, official documentation, Google Drive search strategy, arXiv papers, API behavior, terms, limits, or provenance-sensitive research notes. Do not use for pure local coding tasks with no external unknowns.
---

## Goal

Produce a **verified evidence pack** that a coding agent can safely build from.

## Required workflow

1. Prefer official vendor documentation first.
2. Use up-to-date sources for anything that may have changed recently.
3. Separate:
   - confirmed facts
   - inferred conclusions
   - open questions
4. Record the result in a reusable note under `docs/` or in the active ExecPlan.

## Source order

1. official product or API docs
2. standards bodies / protocol specs
3. official blogs / release notes
4. primary research papers
5. reputable secondary sources only if needed for context

## For Google Drive related tasks

Extract and record:
- the query pattern to use
- required scopes or auth assumptions
- any export limits
- how change tracking works
- whether activity history is needed
- provenance fields that must be stored

## For arXiv related tasks

Extract and record:
- exact search strategy
- paging parameters
- delay / rate-limit expectations
- metadata fields required by the product
- whether the task needs real-time API results or daily OAI-PMH harvesting
- copyright / linking constraints

## Output format

Create or update a note containing:
- `Question`
- `Why this matters`
- `Source table`
- `Key facts`
- `Implementation consequences`
- `Open questions`
- `Next safe action`

## Non-negotiables

- Do not present stale memory as a confirmed current fact.
- Do not merge self-reported model explanations with observed evidence.
- Do not store copyrighted papers or PDFs unless the task explicitly confirms licensing allows it.
- Keep quotes short and rely on paraphrase + structure.

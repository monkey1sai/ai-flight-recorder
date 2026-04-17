# Codex-ready Project Kit for AI / Agent / LLM Observability

This bundle is a practical starting kit for building an **AI Flight Recorder / Observability / Why Engine** product with **OpenAI Codex** as the primary coding agent.

## What is included

- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`  
  The main human-readable specification. It explains the product, architecture, research workflow, testing, security rules, and the exact operating model for Codex.

- `AGENTS.md`  
  The concise repository contract Codex should read first.

- `.agent/PLANS.md`  
  The execution-plan template and rules for long-horizon work.

- `.codex/config.toml.example`  
  Suggested local Codex profiles for build, research, CI validation, and observability.

- `.agents/skills/*`  
  Repo-scoped Codex skills for research, implementation, and validation workflows.

- `docs/TASK_SEEDS.md`  
  Ready-to-run task prompts for Codex.

- `docs/ACCEPTANCE_CHECKLIST.md`  
  Definition of done and release checklist.

- `docs/SOURCES_AND_LIMITS.md`  
  Source policy notes and external-system constraints.

- `evals/codex_bootstrap_prompts.csv`  
  A starter eval prompt set for validating skills and instruction behavior.

## Recommended adoption order

1. Copy this bundle into the repository root.
2. Read `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`.
3. Review and trim `AGENTS.md` so it matches your exact stack and naming.
4. Copy `.codex/config.toml.example` into either:
   - `~/.codex/config.toml` for user-level defaults, or
   - `.codex/config.toml` for project-scoped defaults.
5. Create the first plan under `plans/active/`.
6. Run the prompts in `docs/TASK_SEEDS.md`.

## Important notes

- The `.codex/` directory is intended to be human- or admin-controlled configuration.
- The `.agents/skills/` directory contains reusable skill instructions. Treat it as stable infrastructure, not routine feature code.
- Active work plans should live under `plans/active/` so Codex can update them during normal workspace-write runs.

## Suggested first run

```bash
codex --ask-for-approval never "Summarize the current instructions and list the files you will use as the system of record."
```

Then, once the repo is trusted and dependencies are ready:

```bash
codex exec --json --full-auto "Read AGENTS.md, COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md, and .agent/PLANS.md. Create the first ExecPlan in plans/active/ for Milestone 0 bootstrap and execute it."
```

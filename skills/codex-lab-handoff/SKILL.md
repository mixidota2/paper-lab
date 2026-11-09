---
name: Codex Lab Handoff
description: >-
  Implement or hand off Interactive Lab experiments, paper-lab pages, and repository changes.
  Use for converting selected research into traceable artifacts and verified Lab output.
---
# Codex Lab Handoff

## Scope and inputs
Work in the authorized checkout of `mixidota2/paper-lab` (no org repos). Follow the current task's executor and model choice rather than a model fixed in this file. Continue the assigned implementation task when one already exists.

Before implementation, establish the goal, success criteria, paper IDs and primary sources, core claim, baseline and proposed mechanism, what may or must not be simplified, verification boundary, and expected artifacts. Use an existing task brief or template if supplied; no particular absolute workspace path is required.

## Related skills
`skills/` is the authored source for this repository's skills. `.cursor/skills/` retains byte-identical compatibility copies; update both in the same change and run the parity test. Do not maintain independent instructions in the copies.

- Read `skills/personal-research-bot/SKILL.md` when selecting research or deciding whether a Lab is worthwhile.
- Read `skills/natural-japanese/SKILL.md` when writing Japanese Lab or report prose. Apply its checks, rather than merely linking it.

## Lab implementation
Own the requested information architecture, templates, HTML/CSS/JS, and per-paper artifacts. Redesign the structure when the task calls for it; do not substitute cosmetic edits for requested content or design work. Human-facing Pages content is Japanese.

Human-facing library lives in the `paper-lab` repo/site. HTML is the main interface but **not** source of truth — generate pages from `lab.yaml`, README, code, `results.json`, `mapping.md`.

### Standard HTML sections (required)
Overview; Problem; Core Idea (author claims vs our interpretation); Why It Might Work (label inference); Evidence; Executable Understanding; Results; What We Verified; What We Did NOT Verify; Implementation; Original Paper / Official Code Mapping.

Choose the best medium inside sections: text, diagram, animation, interactive viz, equations, tables, charts, code comparison, parameter exploration, attention/embedding viz, execution traces, etc.

### Executable understanding
Convert the paper into the most understandable executable form. Code is optional.
If the core is an implementable mechanism, create a minimal implementation:
- understanding over production quality
- avoid unnecessary abstraction / inheritance / factories
- allow some duplication; prefer locality
- make baseline vs proposed obvious
- aim for ~200–300 lines for the core when practical

Tiny verification compares Baseline vs Proposed under identical minimal conditions. No giant datasets / long GPU runs by default.
Never overclaim tiny results. Label Mechanism / Performance / Scaling / Production applicability as CONFIRMED | PARTIAL | NOT OBSERVED | NOT TESTED, and state what the experiment does and does not establish.

Track Paper ↔ Minimal code ↔ Official code mappings; list intentional omissions.

Keep each paper flat-first. Do not create single-file directories; split into src/tests/data/assets only when files actually multiply.

## Verification and completion
Use `uv` and the checkout's current README and test configuration for validation. Run the relevant checks against the final changes and distinguish passed, failed, and unrun checks. From the repository root, the Japanese lint entry point is `uv run skills/natural-japanese/scripts/lint.py --genre tech <file>`.

Review the resulting diff and report the verified outcome, source or artifact links, and remaining limits. Check deployed Pages only when deployment was part of the authorized task. Update an existing research registry's Lab links only when registry maintenance is in scope; do not assume a registry path.

## Pages topics
`lab.yaml` topics must be from: `demand-forecasting`, `retail-supply`, `recommender-systems`, `causal-inference`, `ml-systems`, `ai-agents` only. Coalesce generative/retrieval/watch-time into `recommender-systems`; inventory/shelf into `retail-supply`; agent-* into `ai-agents`. Do not add `evaluation` as a theme tag.

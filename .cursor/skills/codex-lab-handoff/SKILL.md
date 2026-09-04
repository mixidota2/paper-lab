---
name: Codex Lab Handoff
description: >-
  Use this when handing Interactive Lab coding, site/HTML redesign, experiments,
  or paper-lab repository work to a Codex cloud agent (default model Terra),
  including sharing natural-japanese and other skills in-repo.
---
# Codex Lab Handoff

## When to use
Use this whenever James needs real coding, Interactive Lab construction, site/HTML redesign, experiments, tests, or repository changes for the Research Library / paper-lab.

## Who does the work
- **Research Bot (this assistant)**: investigation, judgment, understanding specs, feedback, and user communication.
- **Codex cloud agent**: all implementation. Default model: `gpt-5.6-terra` (Terra). Do not do heavy coding inline or with a generic local executor when Codex can own the repo.

## Shared skills
Codex must be able to use the same skills as this assistant.
- Keep skill copies in the paper-lab repo under `skills/` (and mirror into `.cursor/skills/` if helpful).
- Always include at least:
  - `skills/natural-japanese/` (full skill: SKILL.md, references, scripts, assets)
  - `skills/personal-research-bot/` (selection / library principles)
  - `skills/codex-lab-handoff/` (this skill)
- When launching Codex, tell it to read those skills before writing Japanese or Lab pages. Japanese Lab/report prose must follow natural-japanese and run its lint before shipping.

## Lab / HTML work
For Interactive Labs, Codex owns:
1. Information architecture and visual design of the static site (not just CSS tweaks)
2. HTML/CSS/JS templates and generators
3. Per-paper artifacts (`lab.yaml`, README, mapping, minimal code, results)
4. Build with `uv`, tests, GitHub Pages deploy path

Human-facing Pages content is Japanese. Rebuild text and structure when quality is wrong — do not lightly patch translationese.

## Handoff packet (minimum)
Every Codex launch for lab work should include:
- goal and success criteria
- paper ids / arXiv links and non-negotiable facts
- verification boundary
- path to shared skills in-repo
- `uv` requirement
- personal repo only: `mixidota2/paper-lab` (no org repos)
- instruction to redesign site IA/UI if asked for 全面的作り直し

## After Codex finishes
Review the PR/commit, confirm Pages, update `/workspace/research-bot/papers.csv` library paths, and tell James with links. If Japanese still feels off, relaunch Codex with natural-japanese full mode — do not half-fix locally unless blocked.

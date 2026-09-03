# Interactive Research Library (paper-lab)

Static site for Interactive Labs. **`papers/*/lab.yaml` plus markdown/json artifacts are the source of truth.** Generated HTML under `site/` is a view — do not edit it by hand.

This is a library of *labs worth the time*, not a paper dump. Optimize for time to trustworthy understanding.

## Install and build

From this directory (Python 3.10+):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
paper-lab build
# equivalent:
python -m paper_lab.build
python -m paper_lab build
```

On PEP 668 / “externally managed” systems, the venv step is required (do not `pip install` into system Python).

Output is `site/index.html` and one page per lab under `site/papers/`. Open `site/index.html` in a browser (works offline; filters are client-side JS, no network).

Useful flags:

```bash
paper-lab build --root . --out site
paper-lab build --papers papers --out /tmp/library-site
```

A committed `site/` is included so the demo works without running Python. Re-run the build after any lab change.

Tests:

```bash
python -m pytest
```

GitHub Pages: `.github/workflows/pages.yml` installs the package, runs `paper-lab build`, and deploys `site/`.

## How to add a paper lab

1. Create `papers/<paper-id>/` (use a URL-safe slug; leading `_` is fine for fixtures).
2. Add `lab.yaml` with the schema below. Put section prose inline or as a filename in the same directory (`mapping.md`, `overview.md`, …).
3. Add `results.json` if you ran anything; add `mapping.md` for paper ↔ code ↔ official repo.
4. Ship code (`baseline.py` / `proposed.py` / `run.py`) **only** when a tiny real experiment is the right medium. Do not invent science.
5. Run `paper-lab build` and confirm the new page on `site/index.html`.

Do **not** add a lab for a low-value paper. Registry entries can live elsewhere; a full Interactive Lab is for high relevance × novelty × importance × evidence × information gain, and only when expected understanding gain exceeds implementation and compute cost. Tiny benchmark deltas, architecture-only novelty, marketing with thin evidence, and incremental extensions of already-known work should not get labs.

## `lab.yaml` schema

Required:

| Field | Notes |
| --- | --- |
| `id` | URL-safe slug; becomes `site/papers/<id>.html` |
| `title` | Human title |
| `authors` | List of strings (or `{name: ...}`) |
| `year` | Int or string |
| `topics` | List of topic slugs |
| `urls` | `paper`, `arxiv`, `official_code`, `pdf` (string or `null`) |
| `verdict` | Short library verdict |
| `verification` | `mechanism`, `performance`, `scaling`, `production_applicability` each `CONFIRMED` \| `PARTIAL` \| `NOT OBSERVED` \| `NOT TESTED` |
| `related_threads` | List of thread ids |
| `status` | `draft` \| `published` |

Optional: `summary` (index card), `example: true`, `sections` (or `content`) mapping standard keys to markdown or a relative filename, structured `core_idea.author_claim` / `core_idea.research_bot_interpretation`.

Standard page sections, in order: Overview, Problem, Core Idea (author claim vs Research Bot interpretation), Why It Might Work (labeled inference), Evidence, Executable Understanding, Results, What We Verified, What We Did NOT Verify, Implementation, Original Paper / Official Code Mapping.

`mapping.md` and `results.json` in the paper directory are picked up automatically when present.

## Example lab

`papers/_example_demo/` is a **fictional format demonstration**. It is not a paper. Numbers are invented. Do not cite it.

## Layout

```
paper-lab/
├── README.md
├── pyproject.toml
├── papers/_example_demo/   # lab.yaml + artifacts
├── paper_lab/              # generator
├── site/                   # generated output
├── tests/
└── .github/workflows/pages.yml
```

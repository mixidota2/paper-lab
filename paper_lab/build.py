"""Generate site/ from papers/*/lab.yaml.

CLI:
    paper-lab build
    python -m paper_lab.build
    python -m paper_lab
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import Markdown

from paper_lab.models import (
    STANDARD_SECTIONS,
    TOPIC_LABELS,
    VERIFICATION_KEYS,
    VERIFICATION_LABELS,
    VERIFICATION_STATUS_LABELS,
    VERIFICATION_STATUSES,
    Lab,
    LabError,
    load_all_labs,
)

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def find_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    cwd = Path.cwd()
    if (cwd / "papers").is_dir():
        return cwd
    pkg_root = Path(__file__).resolve().parent.parent
    if (pkg_root / "papers").is_dir():
        return pkg_root
    return cwd


def markdown_to_html(text: str) -> str:
    if not text or not str(text).strip():
        return ""
    md = Markdown(extensions=["tables", "fenced_code", "smarty", "sane_lists"])
    return md.convert(text)


def results_to_html(results: Any) -> str:
    if results is None:
        return ""
    chunks: list[str] = []
    note = None
    if isinstance(results, dict):
        note = results.get("note") or results.get("disclaimer")
        if note:
            chunks.append(f'<p class="callout-body"><em>{_escape(str(note))}</em></p>')
        experiments = results.get("experiments")
        if isinstance(experiments, list) and experiments:
            for i, exp in enumerate(experiments, start=1):
                if not isinstance(exp, dict):
                    continue
                name = exp.get("name") or f"実験 {i}"
                chunks.append(f"<h3>{_escape(str(name))}</h3>")
                meta_bits = []
                for key in ("dataset", "n", "seed"):
                    if key in exp:
                        meta_bits.append(
                            f"<li><strong>{_escape(key)}</strong>: {_escape(str(exp[key]))}</li>"
                        )
                if meta_bits:
                    chunks.append("<ul>" + "".join(meta_bits) + "</ul>")
                metrics = exp.get("metrics")
                if isinstance(metrics, dict) and metrics:
                    chunks.append(_metrics_table(metrics))
    raw = json.dumps(results, indent=2, ensure_ascii=False)
    chunks.append(
        "<details><summary>生の results.json</summary>"
        f'<pre><code>{_escape(raw)}</code></pre></details>'
    )
    return "\n".join(chunks)


def _metrics_table(metrics: dict[str, Any]) -> str:
    rows = []
    cols: list[str] = []
    for spec in metrics.values():
        if isinstance(spec, dict):
            for col in spec:
                if col not in cols:
                    cols.append(str(col))
    if not cols:
        cols = ["value"]
    head = "".join(f"<th>{_escape(c)}</th>" for c in cols)
    body = []
    for name, spec in metrics.items():
        cells = [f"<th scope='row'>{_escape(str(name))}</th>"]
        if isinstance(spec, dict):
            for col in cols:
                val = spec.get(col, "")
                cells.append(f"<td>{_escape(str(val))}</td>")
        else:
            cells.append(f"<td colspan='{len(cols)}'>{_escape(str(spec))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<table class="metrics"><thead><tr><th>指標</th>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def paper_sections(lab: Lab) -> list[dict[str, Any]]:
    rendered: list[dict[str, Any]] = []
    for key, title in STANDARD_SECTIONS:
        html = ""
        extra: dict[str, Any] = {}
        if key == "core_idea":
            extra["author_claim_html"] = markdown_to_html(lab.core_idea.author_claim)
            extra["interpretation_html"] = markdown_to_html(
                lab.core_idea.research_bot_interpretation
            )
            leftover = lab.sections.get("core_idea") or ""
            html = markdown_to_html(leftover)
            if not extra["author_claim_html"] and not extra["interpretation_html"] and not html:
                html = ""
        elif key == "results":
            html = results_to_html(lab.results)
            leftover = lab.sections.get("results") or ""
            # Skip leftover if it is only a filename or raw JSON already rendered.
            if leftover and not leftover.strip().endswith(".json"):
                stripped = leftover.strip()
                if not (stripped.startswith("{") or stripped.startswith("[")):
                    html = (html + markdown_to_html(leftover)).strip()
        elif key == "mapping":
            html = markdown_to_html(lab.mapping_markdown or lab.sections.get("mapping", ""))
        else:
            html = markdown_to_html(lab.sections.get(key, ""))

        rendered.append(
            {
                "key": key,
                "title": title,
                "html": html,
                "empty": not html and not extra.get("author_claim_html")
                and not extra.get("interpretation_html"),
                **extra,
            }
        )
    return rendered


def jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["md"] = markdown_to_html
    return env


def build(
    root: Path | None = None,
    papers_dir: Path | None = None,
    site_dir: Path | None = None,
) -> list[Lab]:
    root = find_root(root)
    papers = Path(papers_dir) if papers_dir else root / "papers"
    site = Path(site_dir) if site_dir else root / "site"
    papers = papers.resolve()
    site = site.resolve()

    if not papers.is_dir():
        raise LabError(f"papers directory not found: {papers}")

    labs = load_all_labs(papers)
    env = jinja_env()

    # site/ is entirely generated. Recreate it so a build cannot retain stale files.
    if site.exists():
        shutil.rmtree(site)
    assets = site / "assets"
    papers_out = site / "papers"
    assets.mkdir(parents=True)
    papers_out.mkdir()
    figures_out = site / "figures"

    css_src = TEMPLATES_DIR / "style.css"
    (assets / "style.css").write_text(css_src.read_text(encoding="utf-8"), encoding="utf-8")
    for name in ("library.js", "interactives.js"):
        shutil.copy2(TEMPLATES_DIR / name, assets / name)
    (site / ".nojekyll").write_text("", encoding="utf-8")

    topics = sorted({topic for lab in labs for topic in lab.topics})
    verdicts = sorted({lab.verdict for lab in labs})
    catalog = [lab.to_catalog_entry() for lab in labs]

    index_html = env.get_template("index.html").render(
        labs=labs,
        topics=topics,
        verdicts=verdicts,
        verification_statuses=VERIFICATION_STATUSES,
        verification_status_labels=VERIFICATION_STATUS_LABELS,
        verification_keys=VERIFICATION_KEYS,
        verification_labels=VERIFICATION_LABELS,
        topic_labels=TOPIC_LABELS,
        catalog_json=json.dumps(catalog, ensure_ascii=False),
        paper_count=len(labs),
    )
    (site / "index.html").write_text(index_html, encoding="utf-8")

    paper_template = env.get_template("paper.html")
    for lab in labs:
        download_dir = site / "downloads" / lab.id
        download_dir.mkdir(parents=True)
        for name in ("run.py", "results.json", "lab.yaml", "method.md"):
            source = lab.source_dir / name
            if source.is_file():
                shutil.copy2(source, download_dir / name)
        helper = papers / "_toy_common.py"
        if helper.is_file():
            shutil.copy2(helper, site / "downloads" / "_toy_common.py")
        rendered_figures = []
        for figure in lab.figures:
            source = lab.source_dir / figure["path"]
            destination = figures_out / lab.id / figure["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            rendered_figures.append({**figure, "url": f"../figures/{lab.id}/{figure['path']}"})
        html = paper_template.render(
            lab=lab,
            sections=paper_sections(lab),
            verification_keys=VERIFICATION_KEYS,
            verification_labels=VERIFICATION_LABELS,
            verification_status_labels=VERIFICATION_STATUS_LABELS,
            topic_labels=TOPIC_LABELS,
            figures=rendered_figures,
        )
        (papers_out / f"{lab.slug}.html").write_text(html, encoding="utf-8")

    # Drop stale generated paper pages that no longer have a lab.
    live = {f"{lab.slug}.html" for lab in labs}
    for existing in papers_out.glob("*.html"):
        if existing.name not in live:
            existing.unlink()

    print(f"Built {len(labs)} paper page(s) → {site}")
    for lab in labs:
        flag = " EXAMPLE" if lab.example else ""
        print(f"  - {lab.id}: {lab.title}{flag}")
    return labs


def _add_build_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root (directory that contains papers/). Default: cwd, then package root.",
    )
    parser.add_argument(
        "--papers",
        type=Path,
        default=None,
        help="Papers directory (default: <root>/papers)",
    )
    parser.add_argument(
        "--out",
        "--site",
        dest="out",
        type=Path,
        default=None,
        help="Output directory (default: <root>/site)",
    )


def run_build(args: argparse.Namespace) -> int:
    try:
        build(root=args.root, papers_dir=args.papers, site_dir=args.out)
    except LabError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Direct entry: `python -m paper_lab.build`."""
    parser = argparse.ArgumentParser(
        prog="python -m paper_lab.build",
        description="Generate the Interactive Research Library static site from papers/*/lab.yaml.",
    )
    _add_build_args(parser)
    args = parser.parse_args(list(argv) if argv is not None else None)
    return run_build(args)


def cli(argv: Sequence[str] | None = None) -> int:
    """Console script entry: `paper-lab` / `paper-lab build`."""
    parser = argparse.ArgumentParser(
        prog="paper-lab",
        description="Interactive Research Library generator. HTML is generated from lab.yaml; do not edit site/ by hand.",
    )
    sub = parser.add_subparsers(dest="cmd")
    build_parser = sub.add_parser(
        "build",
        help="Read papers/*/lab.yaml and write site/",
    )
    _add_build_args(build_parser)

    raw = list(argv) if argv is not None else sys.argv[1:]
    if not raw:
        raw = ["build"]
    args = parser.parse_args(raw)
    if args.cmd == "build":
        return run_build(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

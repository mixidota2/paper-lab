"""Load and validate papers/*/lab.yaml (source of truth for the library)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Machine identifiers stay English for filtering / schema stability.
VERIFICATION_STATUSES = (
    "CONFIRMED",
    "PARTIAL",
    "NOT OBSERVED",
    "NOT TESTED",
)
# Japanese display labels for Pages UI (values above remain in lab.yaml).
VERIFICATION_STATUS_LABELS = {
    "CONFIRMED": "確認済み",
    "PARTIAL": "部分的",
    "NOT OBSERVED": "未観測",
    "NOT TESTED": "未検証",
}
LAB_STATUSES = ("draft", "published")
LAB_STATUS_LABELS = {
    "draft": "下書き",
    "published": "公開",
}
URL_KEYS = ("paper", "arxiv", "official_code", "pdf")
VERIFICATION_KEYS = (
    "mechanism",
    "performance",
    "scaling",
    "production_applicability",
)
VERIFICATION_LABELS = {
    "mechanism": "メカニズム",
    "performance": "性能",
    "scaling": "スケーリング",
    "production_applicability": "本番適用性",
}
URL_LABELS = {
    "paper": "論文",
    "arxiv": "arXiv",
    "official_code": "公式コード",
    "pdf": "PDF",
}

# Page section order is fixed. Missing content still renders a placeholder.
# Keys stay English; titles are Japanese for human-facing Pages.
STANDARD_SECTIONS: list[tuple[str, str]] = [
    ("overview", "概要"),
    ("problem", "問題設定"),
    ("core_idea", "核心"),
    ("why_it_might_work", "なぜ効きそうか"),
    ("evidence", "根拠"),
    ("executable_understanding", "実行可能な理解"),
    ("results", "結果"),
    ("what_we_verified", "検証できたこと"),
    ("what_we_did_not_verify", "検証していないこと"),
    ("implementation", "実装"),
    ("mapping", "原論文・公式コード対応"),
]

_FILE_REF = re.compile(r"^[\w./-]+\.(md|txt|json|yaml|yml)$", re.IGNORECASE)


class LabError(ValueError):
    """Invalid lab.yaml or paper directory."""


@dataclass
class Urls:
    paper: str | None = None
    arxiv: str | None = None
    official_code: str | None = None
    pdf: str | None = None

    def present(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for key in URL_KEYS:
            val = getattr(self, key)
            if val:
                out.append((URL_LABELS[key], str(val)))
        return out


@dataclass
class Verification:
    mechanism: str
    performance: str
    scaling: str
    production_applicability: str

    def as_dict(self) -> dict[str, str]:
        return {key: getattr(self, key) for key in VERIFICATION_KEYS}

    def statuses(self) -> set[str]:
        return set(self.as_dict().values())

    def labeled(self) -> dict[str, str]:
        """English status values mapped to Japanese display labels."""
        return {
            key: VERIFICATION_STATUS_LABELS.get(status, status)
            for key, status in self.as_dict().items()
        }


@dataclass
class CoreIdea:
    author_claim: str = ""
    research_bot_interpretation: str = ""


@dataclass
class Lab:
    id: str
    title: str
    authors: list[str]
    year: int | str
    topics: list[str]
    urls: Urls
    verdict: str
    verification: Verification
    related_threads: list[str]
    status: str
    source_dir: Path
    summary: str = ""
    example: bool = False
    sections: dict[str, str] = field(default_factory=dict)
    core_idea: CoreIdea = field(default_factory=CoreIdea)
    results: Any = None
    mapping_markdown: str = ""

    @property
    def slug(self) -> str:
        return self.id

    @property
    def authors_text(self) -> str:
        return ", ".join(self.authors)

    @property
    def status_label(self) -> str:
        return LAB_STATUS_LABELS.get(self.status, self.status)

    def search_text(self) -> str:
        parts = [
            self.id,
            self.title,
            self.authors_text,
            str(self.year),
            self.verdict,
            self.summary,
            " ".join(self.topics),
            " ".join(self.related_threads),
            self.status,
            self.status_label,
        ]
        # Include Japanese verification labels for client-side search.
        for status in self.verification.as_dict().values():
            parts.append(status)
            parts.append(VERIFICATION_STATUS_LABELS.get(status, ""))
        return " ".join(parts).lower()

    def to_catalog_entry(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors_text,
            "year": self.year,
            "topics": list(self.topics),
            "verdict": self.verdict,
            "status": self.status,
            "status_label": self.status_label,
            "example": self.example,
            "verification": self.verification.as_dict(),
            "verification_labels": self.verification.labeled(),
            "href": f"papers/{self.slug}.html",
            "summary": self.summary,
            "related_threads": list(self.related_threads),
        }


def discover_paper_dirs(papers_dir: Path) -> list[Path]:
    if not papers_dir.is_dir():
        return []
    found: list[Path] = []
    for child in sorted(papers_dir.iterdir()):
        if child.is_dir() and (child / "lab.yaml").is_file():
            found.append(child)
    return found


def load_lab(paper_dir: Path) -> Lab:
    path = paper_dir / "lab.yaml"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise LabError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise LabError(f"{path}: expected a mapping at the top level")
    return lab_from_dict(raw, paper_dir)


def load_all_labs(papers_dir: Path) -> list[Lab]:
    labs = [load_lab(directory) for directory in discover_paper_dirs(papers_dir)]
    seen: dict[str, Path] = {}
    for lab in labs:
        if lab.id in seen:
            raise LabError(
                f"duplicate lab id {lab.id!r} in {seen[lab.id]} and {lab.source_dir}"
            )
        seen[lab.id] = lab.source_dir
    return labs


def lab_from_dict(raw: dict[str, Any], paper_dir: Path) -> Lab:
    lab_id = _require_str(raw, "id", paper_dir)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", lab_id):
        raise LabError(
            f"{paper_dir}/lab.yaml: id must be a URL-safe slug (got {lab_id!r})"
        )

    title = _require_str(raw, "title", paper_dir)
    authors = _string_list(raw.get("authors"), "authors", paper_dir)
    if not authors:
        raise LabError(f"{paper_dir}/lab.yaml: authors must be a non-empty list")

    year = raw.get("year")
    if year is None or isinstance(year, bool) or not isinstance(year, (int, str)):
        raise LabError(f"{paper_dir}/lab.yaml: year must be an int or string")

    topics = _string_list(raw.get("topics"), "topics", paper_dir)
    related_threads = _string_list(
        raw.get("related_threads"), "related_threads", paper_dir
    )
    verdict = _require_str(raw, "verdict", paper_dir)

    status = _require_str(raw, "status", paper_dir).lower()
    if status not in LAB_STATUSES:
        raise LabError(
            f"{paper_dir}/lab.yaml: status must be one of {LAB_STATUSES} (got {status!r})"
        )

    urls = _parse_urls(raw.get("urls"), paper_dir)
    verification = _parse_verification(raw.get("verification"), paper_dir)

    summary = raw.get("summary") or ""
    if not isinstance(summary, str):
        raise LabError(f"{paper_dir}/lab.yaml: summary must be a string")
    summary = summary.strip()

    example = bool(raw.get("example", False))
    if _looks_like_example(title, lab_id) or paper_dir.name.startswith("_example"):
        example = True

    section_raw = _load_section_source(raw, paper_dir)
    if section_raw is None:
        section_raw = {}
    if not isinstance(section_raw, dict):
        raise LabError(f"{paper_dir}/lab.yaml: sections/content must be a mapping")

    core_idea = _parse_core_idea(raw.get("core_idea"), section_raw.get("core_idea"))
    sections: dict[str, str] = {}
    for key, value in section_raw.items():
        if key == "core_idea" and isinstance(value, dict):
            continue
        sections[key] = _resolve_content(value, paper_dir, key)

    # File-name conventions: mapping.md and results.json are loaded when present.
    mapping_path = paper_dir / "mapping.md"
    if "mapping" not in sections and mapping_path.is_file():
        sections["mapping"] = mapping_path.read_text(encoding="utf-8")
    mapping_markdown = sections.get("mapping", "")

    results = _load_results(paper_dir, sections.get("results"))
    if isinstance(sections.get("results"), str) and sections["results"].strip().startswith("{"):
        # results.json was inlined as text; prefer the parsed object for rendering.
        pass

    return Lab(
        id=lab_id,
        title=title,
        authors=authors,
        year=year,
        topics=topics,
        urls=urls,
        verdict=verdict,
        verification=verification,
        related_threads=related_threads,
        status=status,
        source_dir=paper_dir.resolve(),
        summary=summary,
        example=example,
        sections=sections,
        core_idea=core_idea,
        results=results,
        mapping_markdown=mapping_markdown,
    )


def _load_section_source(raw: dict[str, Any], paper_dir: Path) -> Any:
    """Return inline sections or a local YAML section artifact."""
    source = raw.get("content_file")
    if source is None:
        return raw.get("sections") or raw.get("content") or {}
    if not isinstance(source, str) or not source.strip():
        raise LabError(f"{paper_dir}/lab.yaml: content_file must be a non-empty string")
    path = (paper_dir / source).resolve()
    try:
        path.relative_to(paper_dir.resolve())
    except ValueError as exc:
        raise LabError(f"{paper_dir}/lab.yaml: content_file escapes paper directory") from exc
    if path.suffix not in {".yaml", ".yml"} or not path.is_file():
        raise LabError(f"{paper_dir}/lab.yaml: content_file must name a local YAML file")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise LabError(f"{path}: invalid YAML: {exc}") from exc


def _looks_like_example(title: str, lab_id: str) -> bool:
    blob = f"{title} {lab_id}".lower()
    return (
        "example" in blob
        or "fictional" in blob
        or "架空" in title
        or "EXAMPLE" in title
    )


def _require_str(raw: dict[str, Any], key: str, paper_dir: Path) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LabError(f"{paper_dir}/lab.yaml: {key} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, key: str, paper_dir: Path) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise LabError(f"{paper_dir}/lab.yaml: {key} must be a list")
    out: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item.strip()
        elif isinstance(item, dict) and "name" in item:
            text = str(item["name"]).strip()
        else:
            raise LabError(
                f"{paper_dir}/lab.yaml: {key} items must be strings "
                f"(or mappings with name=)"
            )
        if text:
            out.append(text)
    return out


def _parse_urls(value: Any, paper_dir: Path) -> Urls:
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise LabError(f"{paper_dir}/lab.yaml: urls must be a mapping")
    unknown = set(value) - set(URL_KEYS)
    if unknown:
        raise LabError(
            f"{paper_dir}/lab.yaml: unknown urls keys {sorted(unknown)}; "
            f"allowed: {list(URL_KEYS)}"
        )
    cleaned: dict[str, str | None] = {}
    for key in URL_KEYS:
        item = value.get(key)
        if item in (None, "", False):
            cleaned[key] = None
        elif isinstance(item, str):
            cleaned[key] = item.strip() or None
        else:
            raise LabError(f"{paper_dir}/lab.yaml: urls.{key} must be a string or null")
    return Urls(**cleaned)


def _parse_verification(value: Any, paper_dir: Path) -> Verification:
    if not isinstance(value, dict):
        raise LabError(f"{paper_dir}/lab.yaml: verification must be a mapping")
    missing = [key for key in VERIFICATION_KEYS if key not in value]
    if missing:
        raise LabError(
            f"{paper_dir}/lab.yaml: verification missing keys {missing}; "
            f"required: {list(VERIFICATION_KEYS)}"
        )
    cleaned: dict[str, str] = {}
    for key in VERIFICATION_KEYS:
        status = value[key]
        if not isinstance(status, str):
            raise LabError(
                f"{paper_dir}/lab.yaml: verification.{key} must be a string"
            )
        status = " ".join(status.strip().upper().replace("_", " ").split())
        if status not in VERIFICATION_STATUSES:
            raise LabError(
                f"{paper_dir}/lab.yaml: verification.{key} must be one of "
                f"{VERIFICATION_STATUSES} (got {value[key]!r})"
            )
        cleaned[key] = status
    return Verification(**cleaned)


def _parse_core_idea(top: Any, nested: Any) -> CoreIdea:
    data: dict[str, Any] = {}
    if isinstance(top, dict):
        data.update(top)
    if isinstance(nested, dict):
        data.update(nested)
    author = data.get("author_claim") or data.get("author") or ""
    interp = (
        data.get("research_bot_interpretation")
        or data.get("interpretation")
        or ""
    )
    if isinstance(nested, str) and not author and not interp:
        # Unstructured core idea markdown is stored in sections, not here.
        return CoreIdea()
    return CoreIdea(
        author_claim=str(author).strip(),
        research_bot_interpretation=str(interp).strip(),
    )


def _resolve_content(value: Any, paper_dir: Path, key: str) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        # Structured blocks belong elsewhere (e.g. core_idea).
        return ""
    if not isinstance(value, str):
        raise LabError(
            f"{paper_dir}/lab.yaml: sections.{key} must be markdown or a file name"
        )
    text = value.strip()
    if "\n" not in text and _FILE_REF.match(text):
        path = (paper_dir / text).resolve()
        try:
            path.relative_to(paper_dir.resolve())
        except ValueError as exc:
            raise LabError(
                f"{paper_dir}/lab.yaml: sections.{key} path escapes paper directory"
            ) from exc
        if not path.is_file():
            raise LabError(
                f"{paper_dir}/lab.yaml: sections.{key} file not found: {text}"
            )
        return path.read_text(encoding="utf-8")
    return value


def _load_results(paper_dir: Path, section_value: str | None) -> Any:
    json_path = paper_dir / "results.json"
    if json_path.is_file():
        try:
            return json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise LabError(f"{json_path}: invalid JSON: {exc}") from exc
    if section_value:
        stripped = section_value.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return None
        ref_path = paper_dir / stripped
        if stripped.endswith(".json") and ref_path.is_file():
            try:
                return json.loads(ref_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise LabError(f"{ref_path}: invalid JSON: {exc}") from exc
    return None

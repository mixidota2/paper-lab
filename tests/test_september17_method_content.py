"""Prevent a file reference plus a figure from silently hiding the method text."""
from pathlib import Path

import pytest

from paper_lab.models import load_all_labs

ROOT = Path(__file__).resolve().parents[1]
SLUGS = (
    "genpage-netflix-homepage",
    "unirec-chain-of-attribute",
    "agentx-kuaishou",
    "static-constrained-gr",
    "flashtrie-gpu-beam",
    "gatesid-coldstart-ranking",
    "coral-meta-config-harness",
)


@pytest.mark.parametrize("slug", SLUGS)
def test_complete_method_source_reaches_page_section(slug):
    lab = next(lab for lab in load_all_labs(ROOT / "papers") if lab.id == slug)
    method = (ROOT / "papers" / slug / "method.md").read_text().strip()
    assert method in lab.sections["method"], (
        f"{slug}: method.md must be resolved before adding a teaching figure; "
        "a multiline 'method.md\\n<figure>' is treated as literal text"
    )

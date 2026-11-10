"""The reader can reproduce FeatureArc from the files linked on its page."""
import ast
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from paper_lab.build import build

ROOT = Path(__file__).resolve().parents[1]
SLUG = "featurearc-inherited-defects-chain-gates"
INPUTS = {"run.py", "render.py", "interactive.js"}
OUTPUTS = {"results.json", "experiment.md"}


class Downloads(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "download" in attrs:
            self.links.append(attrs["href"])


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    target = tmp_path_factory.mktemp("featurearc-distribution") / "site"
    build(root=ROOT, site_dir=target)
    return target


def test_page_links_transitive_inputs_and_explains_same_directory(site):
    page = (site / "papers" / f"{SLUG}.html").read_text(encoding="utf-8")
    links = Downloads(page).links
    for name in INPUTS:
        assert links.count(f"../downloads/{SLUG}/{name}") == 1
        assert (site / "downloads" / SLUG / name).read_bytes() == (
            ROOT / "papers" / SLUG / name).read_bytes()
    assert "実行コードと補助ファイル（render.py、interactive.js）を同じフォルダーへ保存" in page
    assert "run.py 単体で実行できます" not in page
    assert "計算本体</a>" not in page


@pytest.mark.parametrize("working_directory", ["download", "unrelated"])
def test_advertised_inputs_reproduce_both_outputs(site, tmp_path, working_directory):
    page = (site / "papers" / f"{SLUG}.html").read_text(encoding="utf-8")
    downloaded = tmp_path / "ダウンロード files"
    elsewhere = tmp_path / "unrelated working directory"
    downloaded.mkdir()
    elsewhere.mkdir()
    # Never copy an unlinked file or either expected output into the test input.
    for href in Downloads(page).links:
        if Path(href).name in INPUTS:
            shutil.copy2(site / "papers" / href, downloaded / Path(href).name)
    original_inputs = {p.name: p.read_bytes() for p in downloaded.iterdir()}
    cwd = downloaded if working_directory == "download" else elsewhere
    script = "run.py" if working_directory == "download" else str(downloaded / "run.py")
    # Ignore Python environment variables and site packages, but preserve normal
    # script-directory imports. cwd is never the checkout; no repository helper.
    command = [sys.executable, "-E", "-s", "-S", "-B", script]
    for _ in range(2):
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                timeout=20)
        assert result.returncode == 0, result.stderr
        for name in OUTPUTS:
            assert (downloaded / name).read_bytes() == (
                site / "downloads" / SLUG / name).read_bytes()
        assert {p.name: p.read_bytes() for p in downloaded.iterdir()
                if p.name in INPUTS} == original_inputs
        assert set(p.name for p in downloaded.iterdir()) == INPUTS | OUTPUTS
        assert not list(elsewhere.iterdir())
    data = json.loads((downloaded / "results.json").read_text(encoding="utf-8"))
    assert data["kind"] == "featurearc-teaching-v1"
    assert len(data["synthetic"]) == 10
    assert all(len(case["stages"]) == 3 for case in data["synthetic"])


def test_all_download_pages_link_local_python_dependencies(site):
    """Static sibling-module coverage, not execution of every experiment."""
    missing = []
    for directory in sorted((site / "downloads").iterdir()):
        if not (directory / "run.py").is_file():
            continue
        page = (site / "papers" / (directory.name + ".html")).read_text(encoding="utf-8")
        linked = {Path(href).name for href in Downloads(page).links}
        pending = [directory / "run.py"]
        visited = set()
        while pending:
            script = pending.pop()
            if script in visited:
                continue
            visited.add(script)
            modules = []
            for node in ast.walk(ast.parse(script.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    modules.extend(item.name.split(".")[0] for item in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules.append(node.module.split(".")[0])
            for module in modules:
                dependency = directory / (module + ".py")
                if dependency.is_file():
                    if dependency.name not in linked:
                        missing.append(f"{directory.name}: {script.name} needs {dependency.name}")
                    pending.append(dependency)
    assert not missing, "\n".join(missing)


@pytest.mark.parametrize("algorithm", ["sha256", "blob"])
def test_download_readme_revision_pins_exact_bytes(algorithm):
    from prose_preservation import revised_hash
    path = "papers/featurearc-inherited-defects-chain-gates/README.md"
    row = json.loads((ROOT / "tests/prose_revision_hashes.json").read_text())["files"][path]
    data = (ROOT / path).read_bytes()

    def digest(value):
        if algorithm == "sha256":
            return hashlib.sha256(value).hexdigest()
        return hashlib.sha1(b"blob " + str(len(value)).encode() + b"\0" + value).hexdigest()

    assert revised_hash(ROOT, path, row["before_" + algorithm], algorithm) == digest(data)
    with pytest.raises(AssertionError):
        revised_hash(ROOT, path, "unreviewed", algorithm)
    assert row["after_" + algorithm] != digest(data + b"\nchanged\n")

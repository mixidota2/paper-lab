"""Reproduce the advertised download-only CLI, without repository dependencies."""
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from paper_lab.build import build

ROOT = Path(__file__).resolve().parents[1]
SLUG = "series-wise-validation"


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
    target = tmp_path_factory.mktemp("series-distribution") / "site"
    build(root=ROOT, site_dir=target)
    return target


def test_page_lists_both_required_files_and_truthful_guidance(site):
    page = (site / "papers" / f"{SLUG}.html").read_text(encoding="utf-8")
    links = Downloads(page).links
    for name in ("run.py", "table3.json"):
        assert links.count(f"../downloads/{SLUG}/{name}") == 1
        assert (site / "downloads" / SLUG / name).read_bytes() == (
            ROOT / "papers" / SLUG / name
        ).read_bytes()
    assert "実行コードと補助ファイル（table3.json）を同じフォルダーへ保存" in page
    assert "run.py 単体で実行できます" not in page
    assert "計算本体</a>" not in page


@pytest.mark.parametrize("output_mode", ["default", "relative", "absolute"])
def test_linked_files_reproduce_results_outside_repository(site, tmp_path, output_mode):
    page = (site / "papers" / f"{SLUG}.html").read_text(encoding="utf-8")
    downloaded = tmp_path / "ダウンロード files"
    elsewhere = tmp_path / "unrelated working directory"
    downloaded.mkdir()
    elsewhere.mkdir()
    # Select only advertised execution inputs. A hidden file in downloads must
    # not make this test pass if the reader cannot find its link on the page.
    for href in Downloads(page).links:
        if Path(href).name in {"run.py", "table3.json"}:
            shutil.copy2(site / "papers" / href, downloaded / Path(href).name)
    args = [sys.executable, "-I", "-S", str(downloaded / "run.py")]
    if output_mode == "default":
        output = downloaded / "results.json"
    elif output_mode == "relative":
        output = elsewhere / "series-cv-results.json"
        args += ["--out", output.name]
    else:
        output = tmp_path / "explicit output.json"
        args += ["--out", str(output)]
    # Isolated Python and no site packages: neither the checkout nor uv is
    # available as a hidden dependency. Resolve Table3 beside the script.
    result = subprocess.run(args, cwd=elsewhere, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    expected = site / "downloads" / SLUG / "results.json"
    assert output.read_bytes() == expected.read_bytes()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert set(data) == {"toy", "table3_checks", "without_weather"}
    assert len(data["toy"]["records"]) == 50
    assert all(x["dataset_count"] == 11 for x in data["table3_checks"].values())
    assert all(x["dataset_count"] == 10 for x in data["without_weather"].values())
    assert sorted(p.name for p in downloaded.iterdir()) == sorted(
        ["run.py", "table3.json"] + (["results.json"] if output_mode == "default" else [])
    )

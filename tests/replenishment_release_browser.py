"""Issue 21 assertions within the existing signed/sandboxed Chrome route."""
import hashlib
import itertools
import json
from pathlib import Path
from review_capture import capture_segments

def inspect_replenishment(page, base, out, width, snapshot):
    record = {"width": width, "status": "STARTED", "manual_visual_review": "NOT TESTED"}
    try:
        assert page.goto(base + "/guides/index.html").ok
        page.locator("[data-replenishment-guide-link]").click()
        assert page.url.endswith("/guides/forecast-to-replenishment.html")
        page.wait_for_function('document.fonts.status === "loaded"')
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        dates = page.locator("[data-survey-dates]")
        text = dates.inner_text()
        assert "2026-11-18" in text and "2026-11-02（5件）" in text and "2026-11-17（2件）" in text
        snapshot(page, out, f"replenishment-{width}-dates", dates)
        table = page.locator(".repl-comparison")
        assert table.locator("[data-comparison-row]").count() == 7
        assert table.locator("thead th").count() == 6
        region = page.locator(".repl-comparison-scroll")
        assert region.get_attribute("tabindex") == "0"
        region.focus()
        assert region.evaluate("e => e === document.activeElement")
        geometry = region.evaluate("e => ({width:e.clientWidth, scroll:e.scrollWidth, overflow:getComputedStyle(e).overflowX})")
        assert geometry["width"] > 0 and geometry["overflow"] == "auto"
        snapshot(page, out, f"replenishment-{width}-table-left", region)
        if geometry["scroll"] > geometry["width"] + 1:
            region.evaluate("e => e.scrollLeft=e.scrollWidth")
            assert region.evaluate("e => e.scrollLeft > 0")
            snapshot(page, out, f"replenishment-{width}-table-right", region)
            region.evaluate("e => e.scrollLeft=0")
        record["table_geometry"] = geometry
        # Capture every comparison row, including the evidence-boundary column.
        for i, row in enumerate(table.locator("tbody tr").all()):
            snapshot(page, out, f"replenishment-{width}-row-{i}-left", row)
            region.evaluate("e => e.scrollLeft=e.scrollWidth")
            snapshot(page, out, f"replenishment-{width}-row-{i}-right")
            region.evaluate("e => e.scrollLeft=0")
        values = [["all", "current", "legacy"], ["all", "retail", "maintenance"],
                  ["all", "backtest", "model", "observational", "randomized"]]
        combinations = 0
        for selections in itertools.product(*values):
            for key, value in zip(("period", "domain", "evaluation"), selections):
                page.locator(f'[data-filter="{key}"]').select_option(value)
            expected = page.locator("[data-evidence-card]").evaluate_all("""(cards, values) =>
                cards.filter(c => ['period','domain','evaluation'].every((k,i) =>
                    values[i]==='all'||c.dataset[k]===values[i])).length""", list(selections))
            assert page.locator("[data-evidence-card]:visible").count() == expected
            assert page.locator("[data-filter-count]").inner_text() == f"{expected}件 / 全7件"
            assert page.locator("[data-filter-empty]").is_visible() == (expected == 0)
            assert table.locator("[data-comparison-row]").count() == 7
            combinations += 1
        snapshot(page, out, f"replenishment-{width}-filtered", page.locator(".repl-controls"))
        page.locator("[data-filter-reset]").click()
        assert page.locator("[data-evidence-card]:visible").count() == 7
        snapshot(page, out, f"replenishment-{width}-reset", page.locator(".repl-controls"))
        record["filter_combinations"] = combinations
        downloads = []
        for filename in ("replenishment-evidence.yaml", "forecast-to-replenishment.md"):
            link = page.locator(f'a[download][href$="/{filename}"]')
            with page.expect_download() as event:
                link.click()
            download = event.value
            assert download.failure() is None
            assert download.suggested_filename == filename
            raw = Path(download.path()).read_bytes()
            expected = (Path(__file__).resolve().parents[1] / "guides" / filename).read_bytes()
            assert raw == expected
            downloads.append({"name": filename, "sha256": hashlib.sha256(raw).hexdigest()})
        record["downloads"] = downloads
        links = page.locator('.guide-body a[href^="../papers/"]').evaluate_all("es=>[...new Set(es.map(e=>e.getAttribute('href')))]")
        for href in links:
            response = page.request.get(base + "/" + href.removeprefix("../"))
            assert response.ok, href
        record["lab_links"] = links
        capture_segments(page, out / f"replenishment-{width}.png")
        assert page.goto(base + "/guides/index.html").ok
        assert "2026-11-02（5件）" in page.locator("body").inner_text()
        snapshot(page, out, f"replenishment-{width}-index", page.locator("[data-replenishment-guide-link]"))
        record["status"] = "AUTOMATED PASS"
    finally:
        (out / f"replenishment-{width}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))

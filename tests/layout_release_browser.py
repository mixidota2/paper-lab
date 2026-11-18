"""Focused release evidence using the existing signed, sandboxed macOS Chrome route."""
import hashlib
import json
import os
import plistlib
from pathlib import Path
import subprocess
from importlib.metadata import version
from playwright.sync_api import sync_playwright
from macos_chrome_cdp import chrome_process, connect_checked_cdp, verify_seatbelt
from reference_browser import local_site
from review_103_evidence import console_diagnostic
from review_capture import capture_segments
from shelf_survey_browser import inspect_survey

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "browser-review" / "layout-release"
SITE = ROOT / "site"


def main():
    assert version("playwright") == "1.63.0"
    OUT.mkdir(parents=True, exist_ok=False)
    record = {
        "status": "STARTED", "manual_visual_review": "NOT TESTED",
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": hashlib.sha256((ROOT / "guides/store-layout-fixed-counts.md").read_bytes()).hexdigest(),
        "widths": [], "errors": [],
    }

    def snapshot(page, out, name, locator=None):
        if locator is not None:
            locator.scroll_into_view_if_needed()
        page.screenshot(path=str(out / (name + ".png")), full_page=False)

    def fit(page):
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), page.url

    try:
        record["runner_image"] = {key: os.environ.get(key) for key in ("ImageOS", "ImageVersion", "RUNNER_OS", "RUNNER_ARCH")}
        info = plistlib.loads(Path("/Applications/Google Chrome.app/Contents/Info.plist").read_bytes())
        record["chrome_bundle"] = {key: info.get(key) for key in ("CFBundleIdentifier", "CFBundleShortVersionString", "CFBundleVersion")}
        print("Distribution metadata:", json.dumps({"runner_image": record["runner_image"], "chrome_bundle": record["chrome_bundle"]}), flush=True)
        with chrome_process() as (endpoint, pid), local_site(SITE) as base, sync_playwright() as pw:
            os.environ.update(LAB_CDP_URL=endpoint, LAB_CHROME_PID=str(pid))
            browser = connect_checked_cdp(pw)
            record["engine"] = browser.version
            for width in (360, 1440):
                page = browser.new_page(viewport={"width": width, "height": 900}, reduced_motion="reduce")
                page.on("pageerror", lambda error: record["errors"].append(str(error)))
                assert page.goto(base + "/index.html").ok
                verify_seatbelt(browser)
                fit(page)
                assert page.locator("[data-paper]:visible").count() == 114
                page.get_by_role("searchbox").fill("2609.04518")
                assert page.locator("[data-paper]:visible").count() == 1
                snapshot(page, OUT, f"search-{width}")
                snapshot(page, OUT, f"search-result-{width}", page.locator("[data-paper]:visible").first)
                page.get_by_role("button", name="条件を消去").click()
                assert page.locator("[data-paper]:visible").count() == 114
                page.locator('a[href="guides/index.html"]').first.click()
                assert page.url.endswith("/guides/index.html")
                page.locator("[data-layout-guide-link]").click()
                assert page.url.endswith("/guides/store-layout-fixed-counts.html")
                page.wait_for_function('document.fonts.status === "loaded"')
                verify_seatbelt(browser)
                fit(page)
                assert "346,165" in page.locator(".guide-body").inner_text()
                assert "346,156" in page.locator(".guide-body").inner_text()
                tables = []
                for i, table in enumerate(page.locator(".guide-body table").all()):
                    table.scroll_into_view_if_needed()
                    size = table.evaluate("e => ({width:e.clientWidth, scrollWidth:e.scrollWidth, overflow:getComputedStyle(e).overflowX})")
                    assert size["width"] > 0
                    snapshot(page, OUT, f"layout-{width}-table-{i}-left")
                    if size["scrollWidth"] > size["width"] + 1:
                        assert size["overflow"] == "auto"
                        table.evaluate("e => e.scrollLeft=e.scrollWidth")
                        assert table.evaluate("e => e.scrollLeft > 0")
                        snapshot(page, OUT, f"layout-{width}-table-{i}-right")
                        table.evaluate("e => e.scrollLeft=0")
                    tables.append(size)
                assert len(tables) >= 5
                for i, formula in enumerate(page.locator(".guide-body code").all()):
                    box = formula.bounding_box()
                    assert box and box["width"] > 0 and box["height"] > 0
                svg = page.locator(".guide-body svg")
                assert svg.count() == 1
                assert svg.get_attribute("aria-label")
                assert svg.evaluate("""e => {
                    const v=e.viewBox.baseVal;
                    return [...e.querySelectorAll('text')].every(t => {
                        const b=t.getBBox(); return b.width>0 && b.height>0 && b.x>=0 && b.y>=0 && b.x+b.width<=v.width+1 && b.y+b.height<=v.height+1;
                    });
                }""")
                snapshot(page, OUT, f"layout-{width}-svg", svg)
                capture_segments(page, OUT / f"layout-{width}.png")
                page.locator('.guide-body a[href="shelf-decisions.html#store-location"]').click()
                assert "/guides/shelf-decisions.html" in page.url
                page.locator('.guide-body a[href="store-layout-fixed-counts.html"]').first.click()
                assert page.url.endswith("/guides/store-layout-fixed-counts.html")
                # Existing survey checks exercise related Lab navigation and MathML geometry.
                inspect_survey(page, base, OUT, width, snapshot)
                assert page.goto(base + "/papers/sid-ope-hierarchy.html").ok
                verify_seatbelt(browser)
                fit(page)
                panel = page.locator('[data-interactive="explorer"]')
                assert panel.count() == 1
                data = json.loads(panel.locator("[data-results]").text_content())
                slider = panel.get_by_role("slider")
                slider.focus()
                slider.press("End")
                assert int(slider.input_value()) == len(data["frames"]) - 1
                values = panel.locator(".bar-label strong").all_text_contents()
                assert [None if v == "推定不能" else float(v.replace(",", "")) for v in values] == [
                    None if b["value"] is None else round(b["value"], 4) for b in data["frames"][-1]["bars"]
                ]
                snapshot(page, OUT, f"sid-ope-{width}-end", panel)
                panel.get_by_role("button", name="初期条件に戻す", exact=True).click()
                assert int(slider.input_value()) == data["default"]
                snapshot(page, OUT, f"sid-ope-{width}-reset", panel)
                record["widths"].append({"width": width, "tables": tables, "navigation": "PASS", "search": "PASS", "slider": "PASS", "sandbox": "CONFIRMED"})
                page.close()
            assert not record["errors"], record["errors"]
            browser.close()
        record["status"] = "AUTOMATED PASS"
    except BaseException as error:
        record["status"] = "FAIL"
        record["failure"] = console_diagnostic(error)
        print("Protected browser failure:", json.dumps(record["failure"]), flush=True)
        raise
    finally:
        (OUT / "result.json").write_text(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

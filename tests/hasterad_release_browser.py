"""Focused real-browser assertions for the HASTERAD synthetic explorer."""

from math import isclose


def inspect_hasterad(page, base, out, width, snapshot):
    """Exercise the existing explorer with native keyboard and click events."""
    url = base + "/papers/hasterad-retail-substitution.html"
    response = page.goto(url)
    assert response is not None and response.ok and page.url == url
    page.wait_for_function('document.fonts.status === "loaded"')
    panel = page.locator('[data-paper-id="hasterad-retail-substitution"][data-ready="true"]')
    panel.wait_for(state="visible")
    assert panel.count() == 1
    slider = panel.get_by_role("slider")
    assert slider.is_enabled()

    def check(expected):
        shown = [float(value.replace(",", "")) for value in panel.locator(".bar-label strong").all_text_contents()]
        assert shown == expected
        assert isclose(sum(shown[::2]), 100.0, abs_tol=0.0011)
        assert isclose(sum(shown[1::2]), 100.0, abs_tol=0.0011)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        return shown

    baseline = [20.0] * 10
    without_a1 = [0.0, 0.0, 25.0, 32.038, 25.0, 22.654, 25.0, 22.654, 25.0, 22.654]
    assert slider.input_value() == "0"
    check(baseline)
    assert "全4商品" in panel.locator(".explorer-note").inner_text()

    slider.focus()
    slider.press("ArrowRight")
    assert slider.input_value() == "1"
    changed = check(without_a1)
    assert "A1を外す" in panel.locator(".explorer-note").inner_text()
    snapshot(page, out, f"hasterad-{width}-without-a1", panel)

    reset = panel.get_by_role("button", name="初期条件に戻す", exact=True)
    reset.click()
    assert slider.input_value() == "0"
    check(baseline)
    assert "全4商品" in panel.locator(".explorer-note").inner_text()

    figure = page.locator("#figure-retained-a2-probability")
    assert figure.count() == 1 and figure.is_visible()
    assert "25%" in figure.inner_text() and "32.0%" in figure.inner_text()
    assert figure.evaluate("e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && b.left >= 0 && b.right <= innerWidth + 1; }")
    snapshot(page, out, f"hasterad-{width}-equations", figure)
    return {"width": width, "slider": "PASS", "reset": "PASS", "figure": "PASS",
            "probabilities_after_removing_a1": changed}

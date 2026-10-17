"""Assertions for independently calculated percentages after CSSOM serialization."""
import math


def assert_percent_width(locator, expected):
    # CSSOM exposes a serialized CSS number, not the original JS double.
    # Ask this browser to serialize our independently calculated expectation.
    # Exact comparison adds no arbitrary absolute/relative tolerance and does
    # not read application state or its arithmetic to generate the expectation.
    assert math.isfinite(expected) and expected >= 0, expected
    measured = locator.evaluate("""(e, expected) => {
        const probe = document.createElement('div');
        probe.style.width = `${expected}%`;
        return {actual: e.style.width, expected: probe.style.width};
    }""", expected)
    assert measured['expected'].endswith('%'), measured
    assert measured['actual'] == measured['expected'], measured

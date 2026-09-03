"""Interactive Research Library generator.

Source of truth is papers/*/lab.yaml plus markdown/json artifacts.
HTML under site/ is generated — do not edit it by hand.
"""

from paper_lab.models import Lab, load_all_labs, load_lab

__version__ = "0.1.0"
__all__ = ["Lab", "load_all_labs", "load_lab", "__version__"]

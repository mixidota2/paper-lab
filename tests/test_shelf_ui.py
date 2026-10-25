"""DOM substitution smoke; deliberately not a browser or visual assertion."""
from pathlib import Path
import subprocess

def test_shelf_ui_source_branches():
    script = Path(__file__).with_name("shelf_ui_source_smoke.js")
    subprocess.run(["node", str(script)], check=True, capture_output=True, text=True)

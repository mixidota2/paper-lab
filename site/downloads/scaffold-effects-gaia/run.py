"""Run the deterministic teaching experiment; no paper model is trained."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("scaffold-effects-gaia")

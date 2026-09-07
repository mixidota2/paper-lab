from pathlib import Path; import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); from _toy_common import run_lab
run_lab("harness-bench")

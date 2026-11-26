"""販促予定のずれを変える合成例を実行する。論文のモデルは学習しない。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("apollopfn")

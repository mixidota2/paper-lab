"""8期の架空の需要と在庫から費用を計算する。論文の予測モデルは実行しない。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("contextual-deconvolution")

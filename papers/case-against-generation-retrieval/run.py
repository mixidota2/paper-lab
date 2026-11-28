"""人工の16候補で、枝の平均点を使って探索範囲を絞る例を動かす。論文のモデルは学習しない。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("case-against-generation-retrieval")

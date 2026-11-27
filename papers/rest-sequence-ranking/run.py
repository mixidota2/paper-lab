"""固定した人工データで、履歴を使う予測に届く勾配を比べる。論文のモデルは学習しない。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("rest-sequence-ranking")

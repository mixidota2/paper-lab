"""枝を選ぶ段数と到達率を比べる。論文のモデルは学習させない。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("tgr")

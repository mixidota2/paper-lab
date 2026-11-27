"""人工例の警告を基準値ごとに数える。原論文の言語モデルは学習させない。"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _toy_common import run_lab

if __name__ == "__main__":
    run_lab("forecast-critic")

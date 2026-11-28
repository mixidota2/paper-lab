"""配布するJavaScriptで64条件を計算し、教材の結果を作り直す。"""
from pathlib import Path
import subprocess
if __name__ == '__main__':
    subprocess.run(['node', 'test.cjs'], cwd=Path(__file__).resolve().parent, check=True)

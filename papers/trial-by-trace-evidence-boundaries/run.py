"""Regenerate deterministic teaching fixtures using the distributed JS implementation."""
from pathlib import Path
import subprocess
if __name__ == '__main__':
    subprocess.run(['node', 'test.cjs'], cwd=Path(__file__).resolve().parent, check=True)

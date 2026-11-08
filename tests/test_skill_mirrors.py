"""Keep Cursor compatibility copies identical to the authored skills."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_skill_mirrors_match():
    source = ROOT / 'skills'
    mirror = ROOT / '.cursor/skills'
    def files(root):
        return {p.relative_to(root): p for p in root.rglob('*')
                if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    authored, copies = files(source), files(mirror)
    assert authored, 'Expected repository skill files'
    assert authored.keys() == copies.keys(), 'Skill mirror file set differs'
    for path in authored:
        assert authored[path].read_bytes() == copies[path].read_bytes(), f'Skill mirror differs: {path}'

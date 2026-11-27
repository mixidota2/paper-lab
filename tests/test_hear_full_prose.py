"""Only the two HEAR reader-display constants change in the shared renderer."""
import ast
from pathlib import Path
import pytest
from prose_preservation import before_sim2real_all_full_prose, before_hear_full_prose

ROOT = Path(__file__).resolve().parents[1]


def test_shared_renderer_scope_and_old_bytes():
    path = 'paper_lab/batch08.py'
    current = before_sim2real_all_full_prose(ROOT, path, (ROOT / path).read_bytes())
    prior = before_hear_full_prose(ROOT, path, current)
    assert prior != current
    def outside_hear(raw):
        doc = ast.parse(raw)
        matches = [n for n in doc.body if isinstance(n, ast.Assign) and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name) and n.targets[0].id in {'HEAR', 'HEAR_JS'}]
        assert [n.targets[0].id for n in matches] == ['HEAR', 'HEAR_JS']
        for n in matches:
            assert isinstance(n.value, ast.Constant)
            n.value.value = n.targets[0].id
        return ast.dump(doc)
    assert outside_hear(current) == outside_hear(prior)
    with pytest.raises(AssertionError):
        before_hear_full_prose(ROOT, path, current + b'\n')

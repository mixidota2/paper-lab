import ast
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import yaml

from prose_preservation import before_agenttether_full_prose


ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'papers/agenttether-repair/'


def pair(name):
    p = PREFIX + name
    new = (ROOT / p).read_bytes()
    return before_agenttether_full_prose(ROOT, p, new), new


def test_agenttether_paper_summary_is_unchanged():
    before, after = map(yaml.safe_load, pair('lab.yaml'))
    assert before['sections']['overview'] == after['sections']['overview']
    assert before['sections']['method'] == after['sections']['method']
    assert before['verification'] == after['verification']
    assert '13件' in after['sections']['evidence'] and 'p=0.021' in after['sections']['evidence']
    assert '173回' in after['sections']['evidence'] and '13回目' in after['sections']['evidence']
    assert '4、8、12手順目' in after['sections']['results']


def test_agenttether_standalone_replay_and_figures_keep_the_same_mechanisms(tmp_path):
    def norm(raw):
        node = ast.parse(raw)
        assert isinstance(node.body.pop(0), ast.Expr)
        return ast.dump(node, include_attributes=False)
    old, new = pair('run.py')
    assert norm(old) == norm(new)
    (tmp_path / 'run.py').write_bytes(new)
    subprocess.run([sys.executable, '-S', 'run.py'], cwd=tmp_path, check=True)
    original_result = (ROOT / (PREFIX+'results.json')).read_bytes()
    assert (tmp_path / 'results.json').read_bytes() == original_result
    data = json.loads(original_result)
    assert tuple(data['localization'].values()) == (1,5,4,1,3)
    assert data['adherence_proxy']['checkpoints']['fires'] == [4,8,12]
    assert data['guards'] == dict(no_evidence=False, cooldown=False, complete=False, after_write=False, loop_after_write=True)
    for name in ('ctg','guards'):
        old,new = map(ET.fromstring, pair(f'figures/{name}.svg'))
        assert [(e.tag,e.attrib) for e in old.iter()] == [(e.tag,e.attrib) for e in new.iter()]

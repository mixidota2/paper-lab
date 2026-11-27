from pathlib import Path

import pytest
import yaml

from prose_preservation import before_overview_figure_relocations

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('slug,destination,title',[
    ('agentx-kuaishou','evidence','374案のうち、各段階に進んだ件数'),
    ('genpage-netflix-homepage','problem','GenPageはどの作業をまとめて行うか'),
])
def test_remove_lab_diagram_from_paper_only_overview(slug,destination,title):
    path=f'papers/{slug}/lab.yaml'
    new=(ROOT/path).read_bytes()
    old=before_overview_figure_relocations(ROOT,path,new)
    with pytest.raises(AssertionError):
        before_overview_figure_relocations(ROOT,path,new+b' ')
    a,b=map(yaml.safe_load,(old,new))
    assert a['sections']['overview'].split('<figure')[0].rstrip()==b['sections']['overview']
    assert '<figure' not in b['sections']['overview']
    assert {n for n in a['sections'] if a['sections'][n]!=b['sections'][n]}=={'overview',destination}
    assert b['sections'][destination].count('<figure')==a['sections'][destination].count('<figure')+1
    assert title in b['sections'][destination]
    assert {n for n in set(a)|set(b) if a.get(n)!=b.get(n)}=={'sections'}

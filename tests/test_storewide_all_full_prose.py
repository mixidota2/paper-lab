"""Retain the paper scope and exact computational output across the prose revision."""
import ast
import json
from pathlib import Path
import sys
import subprocess
import xml.etree.ElementTree as ET

import pytest
import yaml

from prose_preservation import before_storewide_all_full_prose

ROOT=Path(__file__).resolve().parents[1]
REL='papers/storewide-shelf-decomposition/'

def pair(name):
 p=REL+name
 a=(ROOT/p).read_bytes()
 return before_storewide_all_full_prose(ROOT,p,a),a


def test_scientific_overview_and_equation_bytes():
 old,new=map(yaml.safe_load,pair('lab.yaml'))
 for k in ('id','doi','status','urls','authors','title','verification'):
  assert old[k]==new[k]
 s=new['sections']['overview']
 assert all(w in s for w in ('18条件','16条件','0.10〜0.29秒','前半の計算は入っていません','売上や利益を報告していません'))
 assert all(w not in s for w in ('Lab','教材','操作','150.780593'))
 for before,after in zip(old['teaching_figures'],new['teaching_figures'],strict=True):
  assert before['source']==after['source'] and before['locator']==after['locator']
  for b,a in zip(before.get('steps',[]),after.get('steps',[]),strict=True):
   assert a['formula']==b['formula'] and a['formula_mathml']==b['formula_mathml']
   assert ET.fromstring(a['formula_mathml']).tag.endswith('math')


def test_only_note_changed_in_numeric_sources_and_regeneration(tmp_path):
 a,b=map(json.loads,pair('results.json'))
 assert a.pop('note')!=b.pop('note') and a==b
 old,new=pair('model.js')
 assert old.split(b'\n',1)[1]==new.split(b'\n',1)[1]
 def calc(src):
  node=ast.parse(src)
  [word]=[n for n in ast.walk(node) if isinstance(n,ast.keyword) and n.arg=='note']
  assert isinstance(word.value,ast.Constant)
  word.value.value=''
  return ast.dump(node)
 assert calc(pair('run.py')[0])==calc(pair('run.py')[1])
 entry=tmp_path/'run.py'; entry.write_bytes(pair('run.py')[1])
 subprocess.run([sys.executable,str(entry)],check=True,capture_output=True)
 assert (tmp_path/'results.json').read_bytes()==pair('results.json')[1]


def test_full_source_has_an_exact_prior_for_each_reader_file():
 names={'README.md','experiment.md','implementation.md','interactive.html','interactive.js','lab.yaml','mapping.md','method.md','model.js','results.json','run.py','validation.md'}
 r=json.loads((ROOT/'tests/storewide_all_full_prose_hashes.json').read_text())['files']
 assert set(r)=={REL+x for x in names}
 for name in names:
  before,new=pair(name)
  assert before!=new
  with pytest.raises(AssertionError):
   before_storewide_all_full_prose(ROOT,REL+name,new+b'\n')

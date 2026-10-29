"""Offline tests for no-install native diagnostic orchestration."""
from pathlib import Path
import ast
import io
import pytest
import chrome_restore_probe as p

class Fake:
 def __init__(self,fail=None):self.fail=fail;self.calls=[]
 def call(self,key):
  self.calls.append(key)
  if self.fail==key:raise RuntimeError('injected '+key)
 def preconditions(self,a,s):self.call('preconditions')
 def snapshot(self,a):self.call('snapshot');return 'fingerprint'
 def verify(self,a):self.call('verify-'+str(a))
 def quarantine_equivalent(self,a,b):self.call('quarantine')
 def copy(self,a,b):self.call('copy')
 def equivalent(self,a,b):self.call('equivalent')
 def rename(self,*a):pytest.fail('rename forbidden')


def test_probe_is_not_install_or_browser_gate():
 b=Fake();e=[];p.probe(b,'vendor','original','stage',e)
 assert b.calls.count('snapshot')==2
 assert 'copy' in b.calls
 assert e[-1]['stage']=='original-untouched-after-probe'
 assert all(x['status']=='PASS' for x in e)


def test_precondition_failure_stops_native_copy():
 b=Fake('preconditions');e=[];p.probe(b,'vendor','original','stage',e)
 assert b.calls==['preconditions'] and e[0]['status']=='FAIL'


def test_failed_source_verification_stops_copy():
 b=Fake('verify-vendor');e=[];p.probe(b,'vendor','original','stage',e)
 assert 'copy' not in b.calls


def test_failed_original_stays_failed_not_reclassified():
 b=Fake('verify-original');e=[];p.probe(b,'vendor','original','stage',e)
 assert next(x for x in e if x['stage']=='original-strict-signature-and-Gatekeeper')['status']=='FAIL'
 assert 'copy' in b.calls


def test_missing_quarantine_never_causes_install():
 b=Fake('quarantine');e=[];p.probe(b,'vendor','original','stage',e)
 assert sum(x['status']=='FAIL' for x in e)==2
 assert 'copy' in b.calls # isolated metadata-copy observation only


def test_probe_rename_is_structurally_disabled():
 with pytest.raises(p.restore.RestoreStopped,match='forbidden'):p.ProbeNative(Path('/tmp'),[]).rename('a','b')
 source=Path(p.__file__).read_text();tree=ast.parse(source)
 assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['restore','chrome_process','verify_distribution','setxattr','removexattr','chmod','chown'] for n in ast.walk(tree))
 assert '--version' not in source

class Response(io.BytesIO):
 status=200
 def geturl(self):return 'https://dl.google.com/official.dmg'
class Opener:
 def __init__(self,response):self.response=response
 def open(self,url,timeout):
  assert url==p.restore.URL and timeout==30
  return self.response

def test_acquisition_records_exact_artifact_without_execution(tmp_path):
 import hashlib
 result=p.acquire(tmp_path/'vendor.dmg',Opener(Response(b'artifact bytes')))
 assert result['sha256']==hashlib.sha256(b'artifact bytes').hexdigest()
 assert result['bytes']==14 and result['effective_url']=='https://dl.google.com/official.dmg'


def test_off_host_effective_url_is_rejected(tmp_path):
 class Bad(Response):
  def geturl(self):return 'https://unexpected.example/a.dmg'
 with pytest.raises(p.restore.RestoreStopped):p.acquire(tmp_path/'vendor.dmg',Opener(Bad(b'never accepted')))

"""Dependency restoration transaction tests; never starts a browser or network."""
from pathlib import Path
import pytest
import chrome_restore as m

class Fake:
 def __init__(self, fail=None): self.fail=fail; self.calls=[]; self.mark={}
 def checkpoint(self,n):
  self.calls.append(n)
  if n==self.fail: raise m.RestoreStopped(n)
 def journal(self,record): pass
 def preconditions(self,app,source): self.checkpoint('paths')
 def identity(self,p):
  s=p.lstat();return (s.st_dev,s.st_ino)
 def assert_idle(self): self.checkpoint('idle')
 def snapshot(self,p): return (p/'payload').read_bytes()
 def verify(self,p):
  phase='source' if p.name=='vendor.app' else 'staged' if 'stage' in str(p) else 'selected'
  for check in ['identity','signature','assessment']: self.checkpoint(phase+'-'+check)
 def quarantine_equivalent(self,a,b): self.checkpoint('quarantine')
 def copy(self,a,b):
  self.checkpoint('copy'); b.mkdir(parents=True); (b/'payload').write_bytes((a/'payload').read_bytes())
 def equivalent(self,a,b):
  self.checkpoint('metadata')
  if self.snapshot(a)!=self.snapshot(b): raise m.RestoreStopped('copy bytes changed')
 def rename(self,a,b):
  phase='swap' if 'stage' in str(a) else 'backup' if a.name=='Google Chrome.app' else 'rollback'
  self.checkpoint(phase)
  if b.exists(): raise m.RestoreStopped('destination exists')
  a.rename(b)

def setup(tmp):
 app=tmp/'Google Chrome.app';app.mkdir();(app/'payload').write_bytes(b'original')
 src=tmp/'vendor.app';src.mkdir();(src/'payload').write_bytes(b'vendor')
 return app,src

@pytest.mark.parametrize('failure',['paths','source-identity','source-signature','source-assessment','quarantine','copy','metadata','staged-identity','staged-signature','staged-assessment','backup'])
def test_pre_swap_failures_preserve_original(tmp_path,failure):
 app,src=setup(tmp_path); b=Fake(failure)
 with pytest.raises(m.RestoreStopped): m.restore(b,app,src)
 assert (app/'payload').read_bytes()==b'original'
 assert 'swap' not in b.calls
 assert all('launch' not in x for x in b.calls)

@pytest.mark.parametrize('failure',['swap','selected-identity','selected-signature','selected-assessment'])
def test_post_backup_failure_rolls_back_without_deleting_candidate(tmp_path,failure):
 app,src=setup(tmp_path); b=Fake(failure)
 with pytest.raises(m.RestoreStopped): m.restore(b,app,src)
 assert (app/'payload').read_bytes()==b'original'
 assert any((p/'payload').is_file() and (p/'payload').read_bytes()==b'vendor' for p in tmp_path.rglob('*') if p!=src and p!=app)

def test_success_keeps_original_and_never_launches(tmp_path):
 app,src=setup(tmp_path); b=Fake(); out=m.restore(b,app,src)
 assert (app/'payload').read_bytes()==b'vendor'
 assert (Path(out['backup'])/'payload').read_bytes()==b'original'
 assert b.calls.index('staged-assessment')<b.calls.index('backup')<b.calls.index('swap')
 assert b.calls[-1]=='selected-assessment'
 assert out['browser_test_status']=='NOT TESTED'

def test_missing_source_is_failure_not_reinstall(tmp_path):
 app,src=setup(tmp_path);(src/'payload').unlink()
 with pytest.raises((m.RestoreStopped,FileNotFoundError)): m.restore(Fake(),app,src)
 assert (app/'payload').read_bytes()==b'original'

@pytest.mark.parametrize('mode',['signature','missing-identity','wrong-identity','anchor','assessment'])
def test_native_vendor_checks_fail_closed(tmp_path,monkeypatch,mode):
 from types import SimpleNamespace
 bundle=tmp_path/'vendor.app';bundle.mkdir()
 n=m.Native(tmp_path,[]);calls=[]
 monkeypatch.setattr(n,'acl_map',lambda paths:{p:() for p in paths})
 good='Identifier=com.google.Chrome\nTeamIdentifier=EQHXZ8M8AV\nAuthority=Developer ID Application: Google LLC (EQHXZ8M8AV)\n'
 def command(args,timeout=30):
  calls.append(args)
  if mode=='signature' and '--deep' in args: raise m.RestoreStopped('bad signature')
  if mode=='anchor' and '-R=anchor apple generic' in args: raise m.RestoreStopped('bad anchor')
  if mode=='assessment' and '--assess' in args: raise m.RestoreStopped('Gatekeeper rejected')
  identity='' if mode=='missing-identity' else good.replace('com.google.Chrome','untrusted.fake') if mode=='wrong-identity' else good
  return SimpleNamespace(stdout=b'',stderr=identity.encode())
 monkeypatch.setattr(n,'command',command)
 with pytest.raises(m.RestoreStopped): n.verify(bundle)
 assert all('Contents/MacOS' not in ' '.join(c) for c in calls)
 if mode in ('signature','missing-identity','wrong-identity'): assert not any('--assess' in c for c in calls)


def test_quarantine_cannot_disappear(tmp_path,monkeypatch):
 app,src=setup(tmp_path);n=m.Native(tmp_path,[])
 monkeypatch.setattr(n,'attributes',lambda p:{'com.apple.quarantine':'hash'} if p==app else {})
 with pytest.raises(m.RestoreStopped,match='quarantine'): n.quarantine_equivalent(app,src)


def test_source_symlink_escape_rejected(tmp_path,monkeypatch):
 app,src=setup(tmp_path);(src/'outside').symlink_to(app)
 n=m.Native(tmp_path,[]);monkeypatch.setattr(n,'acl_map',lambda paths:{p:() for p in paths})
 with pytest.raises(m.RestoreStopped,match='symlink'): n.verify(src)


def test_native_rename_collision_never_calls_system(tmp_path,monkeypatch):
 app,src=setup(tmp_path);n=m.Native(tmp_path,[])
 monkeypatch.setattr(m.ctypes,'CDLL',lambda *a,**k:pytest.fail('must not call system'))
 with pytest.raises(m.RestoreStopped,match='collision'): n.rename(app,src)
 assert (app/'payload').read_bytes()==b'original'
 assert (src/'payload').read_bytes()==b'vendor'


def test_backup_verification_detects_metadata_change(tmp_path):
 app,src=setup(tmp_path)
 class AlteredBackup(Fake):
  def snapshot(self,p):
   value=super().snapshot(p)
   return b'changed metadata' if 'original-' in p.name else value
 b=AlteredBackup()
 with pytest.raises(m.RestoreStopped,match='backup verification'): m.restore(b,app,src)
 assert (app/'payload').read_bytes()==b'original'
 assert 'swap' not in b.calls


def test_rollback_failure_retains_both_bundles(tmp_path):
 app,src=setup(tmp_path)
 class BlockedRollback(Fake):
  def rename(self,a,b):
   if 'original-' in a.name: raise m.RestoreStopped('ordinary permission denied')
   return super().rename(a,b)
 with pytest.raises(m.RestoreStopped,match='rollback stopped'): m.restore(BlockedRollback('selected-signature'),app,src)
 assert any((p/'payload').is_file() and (p/'payload').read_bytes()==b'original' for p in tmp_path.iterdir())
 assert any((p/'payload').is_file() and (p/'payload').read_bytes()==b'vendor' for p in tmp_path.iterdir())


@pytest.mark.parametrize('url',['http://dl.google.com/chrome.dmg','https://evil.example/chrome.dmg'])
def test_vendor_redirect_not_allowed(url):
 with pytest.raises(m.RestoreStopped,match='redirect'): m.VendorRedirect().redirect_request(None,None,302,'',{},url)


def test_no_security_or_browser_invocation_in_native_copy(tmp_path,monkeypatch):
 app,src=setup(tmp_path);n=m.Native(tmp_path,[]);calls=[]
 monkeypatch.setattr(n,'command',lambda args,**kw:calls.append(args))
 n.copy(src,tmp_path/'stage-container'/'Google Chrome.app')
 assert calls==[['/usr/bin/ditto','--rsrc','--extattr','--acl','--qtn',str(src),str(tmp_path/'stage-container'/'Google Chrome.app')]]

def test_darwin_attribute_reader_is_bounded_read_only(tmp_path,monkeypatch):
 from types import SimpleNamespace
 import ctypes,hashlib
 n=m.Native(tmp_path,[]);calls=[]
 values={b'com.apple.quarantine':b'preserve-this-value'}
 names=b'com.apple.quarantine\0'
 class F:
  def __init__(self,fn):self.fn=fn
  def __call__(self,*a):return self.fn(*a)
 def listing(path,buf,size,options):
  calls.append(('list',options))
  if buf is not None:ctypes.memmove(buf,names,len(names))
  return len(names)
 def reading(path,name,buf,size,position,options):
  calls.append(('get',options));assert position==0
  value=values[name]
  if buf is not None:ctypes.memmove(buf,value,len(value))
  return len(value)
 monkeypatch.setattr(m.ctypes,'CDLL',lambda *a,**kw:SimpleNamespace(listxattr=F(listing),getxattr=F(reading)))
 assert n.attributes(tmp_path)=={'com.apple.quarantine':hashlib.sha256(values[b'com.apple.quarantine']).hexdigest()}
 assert all(option==1 for _,option in calls)
 assert n.evidence==[]

def test_parent_acl_parser_preserves_entries(tmp_path,monkeypatch):
 from types import SimpleNamespace
 a=tmp_path/'a';b=tmp_path/'b'
 n=m.Native(tmp_path,[])
 output=f'drwxr-xr-x+ 1 user group 0 today {a}\n 0: everyone deny delete\ndrwxr-xr-x 1 user group 0 today {b}\n'
 monkeypatch.setattr(n,'command',lambda *a,**kw:SimpleNamespace(stdout=output.encode()))
 assert n.acl_map([a,b])=={a:('0: everyone deny delete',),b:()}


def test_unexpected_selected_object_is_not_moved_by_rollback(tmp_path):
 app,src=setup(tmp_path)
 class ConcurrentReplacement(Fake):
  def verify(self,p):
   if p==app and (app/'payload').read_bytes()==b'vendor':
    app.rename(tmp_path/'concurrent-retained-vendor.app')
    app.mkdir();(app/'payload').write_bytes(b'someone-else')
    raise m.RestoreStopped('concurrent replacement')
   super().verify(p)
 with pytest.raises(m.RestoreStopped,match='unexpected selected app'):m.restore(ConcurrentReplacement(),app,src)
 assert (app/'payload').read_bytes()==b'someone-else'
 assert any((p/'payload').is_file() and (p/'payload').read_bytes()==b'original' for p in tmp_path.iterdir())


@pytest.mark.parametrize('target',['original','source','stage'])
def test_changed_inputs_stop_before_backup(tmp_path,target):
 app,src=setup(tmp_path)
 class ChangeBeforeSwap(Fake):
  def verify(self,p):
   super().verify(p)
   if 'stage' in str(p):
    where=app if target=='original' else src if target=='source' else p
    (where/'payload').write_bytes(b'changed')
 b=ChangeBeforeSwap()
 # Source is additionally compared before swap by the implementation.
 with pytest.raises(m.RestoreStopped):m.restore(b,app,src)
 assert 'backup' not in b.calls


def test_selected_metadata_failure_has_rollback_armed(tmp_path):
 app,src=setup(tmp_path)
 class BadSelected(Fake):
  def equivalent(self,a,b):
   if b==app:raise m.RestoreStopped('selected metadata')
   super().equivalent(a,b)
 with pytest.raises(m.RestoreStopped):m.restore(BadSelected(),app,src)
 assert (app/'payload').read_bytes()==b'original'


def test_staging_container_collision_does_not_copy(tmp_path,monkeypatch):
 n=m.Native(tmp_path,[]);stage=tmp_path/'container'/'Google Chrome.app';stage.parent.mkdir()
 monkeypatch.setattr(n,'command',lambda *a,**kw:pytest.fail('copy forbidden'))
 with pytest.raises(FileExistsError):n.copy(tmp_path/'vendor.app',stage)


def test_helper_has_no_protected_verifier_or_application_execution():
 import ast
 source=Path(m.__file__).read_text();tree=ast.parse(source)
 assert 'selected_original_verifier' not in source
 assert 'verify_distribution(' not in source
 assert '--version' not in source
 assert not any(isinstance(x,ast.Attribute) and x.attr in ['setxattr','removexattr','chmod','chown','unlink','rmtree'] for x in ast.walk(tree))
 assert 'chrome_process(' not in source

@pytest.mark.parametrize('path,uid,gid,mode,acl',[
 ('/Applications',0,80,0o777,()),
 ('/Applications',0,0,0o775,()),
 ('/Applications',12345,80,0o755,()),
 ('/',0,80,0o775,()),
 ('/Applications',0,80,0o775,('0: everyone allow write',)),
])
def test_parent_policy_rejects_weakened_permissions(path,uid,gid,mode,acl):
 with pytest.raises(m.RestoreStopped):m.validate_parent_policy(Path(path),uid,gid,mode,acl,501)

def test_original_application_parent_policy_is_preserved():
 m.validate_parent_policy(Path('/Applications'),0,80,0o775,('0: everyone deny delete',),501)
 m.validate_parent_policy(Path('/'),0,0,0o755,(),501)

@pytest.mark.parametrize('after',['backup','swap'])
def test_interrupted_committed_rename_is_reconciled(tmp_path,after):
 app,src=setup(tmp_path)
 class InterruptAfterRename(Fake):
  def rename(self,a,b):
   phase='swap' if 'stage' in str(a) else 'backup' if a==app else 'rollback'
   super().rename(a,b)
   if phase==after:raise KeyboardInterrupt('after committed rename')
 with pytest.raises(KeyboardInterrupt):m.restore(InterruptAfterRename(),app,src)
 assert (app/'payload').read_bytes()==b'original'

def test_equivalent_concurrent_replacement_cannot_pass(tmp_path):
 app,src=setup(tmp_path)
 class EquivalentReplacement(Fake):
  def verify(self,p):
   super().verify(p)
   if p==app:
    app.rename(tmp_path/'retained-candidate.app')
    app.mkdir();(app/'payload').write_bytes(b'vendor')
 with pytest.raises(m.RestoreStopped,match='unexpected selected app'):m.restore(EquivalentReplacement(),app,src)
 assert any((p/'payload').is_file() and (p/'payload').read_bytes()==b'original' for p in tmp_path.iterdir())

def test_native_root_symlink_rejected(tmp_path):
 app,src=setup(tmp_path);link=tmp_path/'link.app';link.symlink_to(src)
 with pytest.raises(m.RestoreStopped,match='root symlink'):m.Native(tmp_path,[]).verify(link)

@pytest.mark.parametrize('override', [None, {}, {'Writable': True}, {'WritableMedia': True}, {'WritableVolume': True}, {'WritableVolume': 0}, {'WritableVolume': 'false'}, {'WritableVolume': None}, {'ReadOnlyVolume': True}])
def test_native_readonly_contract_from_diskutil(tmp_path, monkeypatch, override):
 import plistlib
 from types import SimpleNamespace
 app=tmp_path/'selected.app';app.mkdir()
 mount=tmp_path/'mount';mount.mkdir();source=mount/'Google Chrome.app';source.mkdir()
 n=m.Native(mount,[])
 monkeypatch.setattr(m,'APP',app)
 monkeypatch.setattr(m.platform,'system',lambda:'Darwin')
 monkeypatch.setattr(m.os,'getuid',lambda:501)
 monkeypatch.setattr(n,'assert_idle',lambda:None)
 info={'Writable':False,'WritableMedia':False,'WritableVolume':False}
 if override is not None:
  if not override or 'ReadOnlyVolume' in override:info=override
  else:info.update(override)
 calls=[]
 def command(args):
  calls.append(args)
  if args[0]=='/usr/sbin/diskutil':return SimpleNamespace(stdout=plistlib.dumps(info) if None not in info.values() else plistlib.dumps({k:v for k,v in info.items() if v is not None}))
  assert args==['/usr/bin/ditto','--help']
  return SimpleNamespace(stdout=b'--rsrc --extattr --acl --qtn')
 monkeypatch.setattr(n,'command',command)
 if override is None:n.preconditions(app,source)
 else:
  with pytest.raises(m.RestoreStopped,match='vendor mount not read-only'):n.preconditions(app,source)
  assert len(calls)==1

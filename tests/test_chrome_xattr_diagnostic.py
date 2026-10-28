"""Read-only diagnostic tests: no Chrome launch or attribute mutation."""
import ctypes
import errno
import stat
from types import SimpleNamespace
import json
import os
from pathlib import Path
import subprocess
import pytest
import review_103_evidence as m
import macos_chrome_cdp as chrome

VERIFY=['/usr/bin/codesign','--verify','--deep','--strict','--verbose=2','/Applications/Google Chrome.app']

@pytest.fixture
def bundle(tmp_path,monkeypatch):
 p=tmp_path/'Google Chrome.app';p.mkdir()
 monkeypatch.setattr(m,'XATTR_BUNDLE_COMPONENTS',p.resolve().parts[1:])
 return p


def test_names_only_no_values_or_mutation(bundle,monkeypatch):
 (bundle/'Contents').mkdir();f=bundle/'Contents'/'resource';f.write_bytes(b'unchanged')
 calls=[]
 def names(fd):
  assert isinstance(fd,int);calls.append(fd)
  return ['com.apple.FinderInfo','com.apple.ResourceFork','secret-attribute-name']
 monkeypatch.setattr(m,'darwin_xattr_reader',lambda: names)
 def forbidden(*args,**kwargs):raise AssertionError('Mutation or attribute value read')
 for name in ['getxattr','setxattr','removexattr','chmod','chown','unlink','rename']:
  monkeypatch.setattr(m.os,name,forbidden,raising=False)
 r=m.chrome_xattr_names();text=json.dumps(r)
 assert calls and r['visited']==3
 assert {x['path'] for x in r['records']}=={'.','Contents','Contents/resource'}
 assert all(x['names']==['com.apple.FinderInfo','com.apple.ResourceFork'] for x in r['records'])
 assert 'secret-attribute-name' not in text and str(bundle) not in text
 assert r['unlisted_names']==3
 assert f.read_bytes()==b'unchanged'


def test_bounds(bundle,monkeypatch):
 for i in range(40):(bundle/('x'*200+str(i))).touch()
 monkeypatch.setattr(m,'darwin_xattr_reader',lambda: lambda fd:list(m.XATTR_NAMES))
 r=m.chrome_xattr_names()
 assert len(r['records'])==16 and r['limited']
 assert len(json.dumps(r,ensure_ascii=True).encode())<8192
 monkeypatch.setattr(m,'XATTR_MAX_PATHS',4)
 r=m.chrome_xattr_names();assert r['visited']==4 and r['limited']
 monkeypatch.setattr(m,'XATTR_MAX_SECONDS',0)
 r=m.chrome_xattr_names();assert r['visited']==0 and r['limited']


def test_escaping_names_and_external_symlinks_not_opened(bundle,tmp_path,monkeypatch):
 outside=tmp_path/'outside';outside.mkdir();(outside/'do-not-read').touch()
 (bundle/'external').symlink_to(outside,target_is_directory=True)
 (bundle/'file-link').symlink_to(outside/'do-not-read')
 for name in ['bad\nname','bad"name','secret-file','x'*241]: (bundle/name).touch()
 seen=[]
 def names(fd):seen.append(os.fstat(fd).st_ino);return ['com.apple.quarantine']
 monkeypatch.setattr(m,'darwin_xattr_reader',lambda: names)
 r=m.chrome_xattr_names()
 assert seen==[bundle.stat().st_ino]
 assert r['records']==[{'path':'.','names':['com.apple.quarantine']}]
 assert r['omitted']==6


def test_bundle_component_symlink_rejected(bundle,tmp_path,monkeypatch):
 alias=tmp_path/'alias';alias.symlink_to(bundle,target_is_directory=True)
 monkeypatch.setattr(m,'XATTR_BUNDLE_COMPONENTS',alias.parts[1:])
 monkeypatch.setattr(m,'darwin_xattr_reader',lambda: lambda fd:pytest.fail('Must not inspect symlink target'))
 with pytest.raises(OSError):m.chrome_xattr_names()


def test_attribute_errors_omit_exception_text(bundle,monkeypatch):
 def fail(fd):raise OSError('SECRET_VALUE unrelated/private/path')
 monkeypatch.setattr(m,'darwin_xattr_reader',lambda: fail)
 r=m.chrome_xattr_names()
 assert r['errors']==1 and r['records']==[]
 assert 'SECRET' not in json.dumps(r)


@pytest.mark.parametrize('kind',['oserror','valueerror','runtimeerror'])
def test_diagnostic_errors_preserve_original_failure(monkeypatch,kind):
 error=subprocess.CalledProcessError(1,VERIFY,stderr='original signature failure')
 def fail():raise {'oserror':OSError,'valueerror':ValueError,'runtimeerror':RuntimeError}[kind]('SECRET')
 monkeypatch.setattr(m,'chrome_xattr_names',fail)
 result=m.console_diagnostic(error)
 assert result['type']=='CalledProcessError' and result['returncode']==1
 assert result['stderr']['text']=='original signature failure'
 assert result['chrome_xattr_names']=={'status':'unavailable'}
 assert error.cmd==VERIFY and error.returncode==1 and error.stderr=='original signature failure'
 assert 'SECRET' not in json.dumps(result)


@pytest.mark.parametrize('error',[subprocess.TimeoutExpired(VERIFY,30),subprocess.CalledProcessError(0,VERIFY),subprocess.CalledProcessError(1,VERIFY+['extra']),subprocess.CalledProcessError(1,['/usr/bin/codesign','-dv','--verbose=4','/Applications/Google Chrome.app']),ValueError('arbitrary')])
def test_only_strict_nonzero_failure_triggers(error,monkeypatch):
 monkeypatch.setattr(m,'chrome_xattr_names',lambda:pytest.fail('Unexpected diagnostic'))
 assert 'chrome_xattr_names' not in m.console_diagnostic(error)


def test_failure_preserved_no_chrome_launch(monkeypatch):
 error=subprocess.CalledProcessError(1,VERIFY,stderr='original')
 def fail():raise error
 monkeypatch.setattr(chrome,'verify_distribution',fail)
 monkeypatch.setattr(chrome.subprocess,'Popen',lambda *a,**kw:pytest.fail('Browser must not launch'))
 with pytest.raises(subprocess.CalledProcessError) as caught:
  with chrome.chrome_process():pytest.fail('Must not yield browser')
 assert caught.value is error


def test_original_failure_report_remains_nonpassing(tmp_path,monkeypatch):
 monkeypatch.setattr(m,'chrome_xattr_names',lambda:{'records':[]})
 e=m.RunEvidence(tmp_path,{'required_cases':['must-run'],'semantic_groups':[]})
 error=subprocess.CalledProcessError(1,VERIFY,stderr='original')
 interruption={**e.diagnostic(error),'phase':'startup','kind':'interruption'}
 report=e.finalize(False,interruption)
 assert report['status']!='PASS' and not report['execution_completed']
 assert report['interruption']['console']['returncode']==1


def fake_darwin(monkeypatch, payload=b'', result=None, error=0):
 calls=[]
 class Function:
  def __call__(self,fd,buffer,size,options):
   calls.append((fd,size,options))
   ctypes.memmove(buffer,payload,min(len(payload),size))
   ctypes.set_errno(error)
   return len(payload) if result is None else result
 function=Function()
 def load(path,**kwargs):
  assert path=='/usr/lib/libSystem.B.dylib' and kwargs=={'use_errno':True}
  return SimpleNamespace(flistxattr=function)
 monkeypatch.setattr(m.sys,'platform','darwin')
 monkeypatch.setattr(m.ctypes,'CDLL',load)
 return function,calls


def test_darwin_fd_contract_without_python_xattr_apis(monkeypatch):
 for name in ('listxattr','getxattr','setxattr','removexattr'):
  monkeypatch.delattr(m.os,name,raising=False)
 function,calls=fake_darwin(monkeypatch,b'com.apple.FinderInfo\0other\0')
 assert m.darwin_xattr_reader()(42)==['com.apple.FinderInfo','other']
 assert calls==[(42,8192,0)]
 assert function.argtypes==[ctypes.c_int,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int]
 assert function.restype is ctypes.c_ssize_t


@pytest.mark.parametrize('payload,result,error',[
 (b'',0,0),(b'',-1,errno.ENOTSUP),(b'',-1,errno.ERANGE),
 (b'',8193,0),(b'not-terminated',None,0),(b'\xff\0',None,0)])
def test_adapter_empty_errors_and_bounds_no_retry(monkeypatch,payload,result,error):
 _,calls=fake_darwin(monkeypatch,payload,result,error)
 reader=m.darwin_xattr_reader()
 if result==0:assert reader(42)==[]
 else:
  with pytest.raises((OSError,UnicodeError)):reader(42)
 assert calls==[(42,8192,0)]


@pytest.mark.parametrize('failure',['platform','library','symbol','unsupported'])
def test_missing_unsupported_interface_preserves_signature(bundle,monkeypatch,failure):
 for name in ('listxattr','getxattr','setxattr','removexattr'):
  monkeypatch.delattr(m.os,name,raising=False)
 fake_darwin(monkeypatch,result=-1,error=errno.ENOTSUP)
 if failure=='platform':monkeypatch.setattr(m.sys,'platform','not-darwin')
 if failure=='library':
  def fail(*a,**kw):raise OSError('SECRET library failure')
  monkeypatch.setattr(m.ctypes,'CDLL',fail)
 if failure=='symbol':monkeypatch.setattr(m.ctypes,'CDLL',lambda *a,**kw:SimpleNamespace())
 original=subprocess.CalledProcessError(1,VERIFY,stderr='original')
 result=m.console_diagnostic(original)
 assert result['returncode']==1 and result['stderr']['text']=='original'
 assert original.cmd==VERIFY and original.returncode==1
 assert 'SECRET' not in json.dumps(result)
 if failure=='unsupported':assert result['chrome_xattr_names']['errors']==1
 else:assert result['chrome_xattr_names']=={'status':'unavailable'}


def test_type_change_after_open_not_inspected(bundle,monkeypatch):
 target=bundle/'regular';target.touch();inode=target.stat().st_ino
 real_fstat=os.fstat;seen=[]
 def changed(fd):
  info=real_fstat(fd)
  return SimpleNamespace(st_mode=stat.S_IFIFO) if info.st_ino==inode else info
 monkeypatch.setattr(m.os,'fstat',changed)
 monkeypatch.setattr(m,'darwin_xattr_reader',lambda:lambda fd:seen.append(real_fstat(fd).st_ino) or [])
 result=m.chrome_xattr_names()
 assert seen==[bundle.stat().st_ino] and result['omitted']==1

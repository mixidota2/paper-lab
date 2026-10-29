"""Fail-closed official dependency restoration; no browser launch or security edits.

Not wired into CI. Native execution requires explicit review of this candidate.
Only main() acquires vendor content; restore() is injectable for offline tests.
"""
from pathlib import Path
import ctypes
import hashlib
import json
import os
import platform
import re
import time
import plistlib
import stat
import subprocess
import tempfile
import urllib.request
from urllib.parse import urlparse
import uuid

APP=Path('/Applications/Google Chrome.app')
URL='https://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg'
TEAM='EQHXZ8M8AV'
class RestoreStopped(RuntimeError): pass


def restore(backend, app, source):
    """Preserve original, verify candidate, rename into the exact selected path."""
    token=uuid.uuid4().hex
    stage=app.parent/('Chrome-stage-'+token)/'Google Chrome.app'
    backup=app.parent/('Chrome-original-'+token+'.app')
    failed=app.parent/('Chrome-failed-'+token+'.app')

    backend.preconditions(app,source)
    original_identity=backend.identity(app)
    original=backend.snapshot(app)
    source_before=backend.snapshot(source)
    backend.verify(source)
    backend.quarantine_equivalent(app,source)
    backend.copy(source,stage)
    staged_identity=backend.identity(stage)
    staged_snapshot=backend.snapshot(stage)
    backend.equivalent(source,stage)
    if backend.snapshot(source)!=source_before: raise RestoreStopped('vendor source changed')
    backend.verify(stage)
    backend.quarantine_equivalent(app,stage)
    backend.assert_idle()
    if backend.snapshot(source)!=source_before: raise RestoreStopped('vendor source changed before swap')
    if backend.identity(app)!=original_identity or backend.snapshot(app)!=original: raise RestoreStopped('selected bundle changed concurrently')
    if backend.identity(stage)!=staged_identity or backend.snapshot(stage)!=staged_snapshot: raise RestoreStopped('staging changed concurrently')
    backend.journal({'phase':'before-backup','selected':str(app),'stage':str(stage),'backup':str(backup),'failed':str(failed),'original_identity':original_identity,'staged_identity':staged_identity})
    try:
        backend.rename(app,backup)
        backend.journal({'phase':'backed-up'})
        if backend.identity(backup)!=original_identity or backend.snapshot(backup)!=original: raise RestoreStopped('backup verification failed')
        backend.rename(stage,app)
        backend.journal({'phase':'installed'})
        if backend.identity(app)!=staged_identity: raise RestoreStopped('unexpected installed identity')
        backend.equivalent(source,app)
        backend.verify(app)
        if backend.identity(app)!=staged_identity: raise RestoreStopped('selected identity changed during verification')
        backend.journal({'phase':'verified; browser NOT TESTED'})
    except BaseException as error:
        # Reconcile locations rather than trusting a flag: a signal may arrive
        # after a successful native rename but before Python records its return.
        def identity_or_none(path):
            try: return backend.identity(path)
            except FileNotFoundError: return None
        try:
            backup_now=identity_or_none(backup);selected_now=identity_or_none(app)
            if backup_now is not None:
                if backup_now!=original_identity: raise RestoreStopped('unexpected backup; do not move it')
                if selected_now==staged_identity:
                    backend.rename(app,failed)
                elif selected_now is not None:
                    raise RestoreStopped('unexpected selected app; do not move it')
                backend.rename(backup,app)
                if backend.snapshot(app)!=original: raise RestoreStopped('rollback differs')
                backend.journal({'phase':'rolled-back; candidates retained'})
            elif selected_now!=original_identity:
                raise RestoreStopped('unreconciled original location; retain all paths')
        except BaseException as rollback:
            raise RestoreStopped('rollback stopped; retain all paths: '+str(rollback)) from error
        raise
    return {'status':'RESTORED / browser tests pending','selected':str(app),
            'backup':str(backup),'browser_test_status':'NOT TESTED'}


def validate_parent_policy(path,uid,gid,mode,acl,current_uid):
    if uid not in (0,current_uid) or mode&stat.S_IWOTH:
        raise RestoreStopped('parent ownership/other-write mismatch')
    if mode&stat.S_IWGRP and not (path==Path('/Applications') and uid==0 and gid==80):
        raise RestoreStopped('parent group-write mismatch')
    if any(' deny ' not in (' '+entry+' ') for entry in acl):
        raise RestoreStopped('unreviewed parent ACL grant')


class Native:
    def __init__(self, mount, evidence, journal_path=None):
        self.mount=mount; self.evidence=evidence; self.journal_path=journal_path
    def journal(self,record):
        if self.journal_path is None: raise RestoreStopped('durable transaction journal unavailable')
        with self.journal_path.open('a') as handle:
            handle.write(json.dumps(record)+'\n');handle.flush();os.fsync(handle.fileno())
    def command(self,args,timeout=30):
        # No shell, installer, application invocation, sudo or attribute writes.
        r=subprocess.run(args,stdin=subprocess.DEVNULL,capture_output=True,timeout=timeout,check=False,env={**os.environ,'LC_ALL':'C'})
        self.evidence.append({'command':args,'returncode':r.returncode,
                              'stdout':r.stdout.decode(errors='replace')[:16000],
                              'stderr':r.stderr.decode(errors='replace')[:16000]})
        if args == ['/usr/bin/ditto', '--help']:
            usage = (r.stdout + r.stderr).decode(errors='replace')
            if r.returncode not in (0, 1) or not all(x in usage for x in ('Usage: ditto', '--rsrc', '--extattr', '--acl', '--qtn')):
                raise RestoreStopped('native preservation options not established')
        elif r.returncode: raise RestoreStopped('command failed: '+repr(args))
        return r
    def identity(self,path):
        value=path.lstat();return (value.st_dev,value.st_ino)
    def assert_idle(self):
        parents=list(APP.parents);acls=self.acl_map(parents)
        for path in parents:
            if path.resolve(strict=True)!=path: raise RestoreStopped('parent path alias')
            info=path.stat()
            validate_parent_policy(path,info.st_uid,info.st_gid,info.st_mode,acls[path],os.getuid())
        processes=self.command(['/bin/ps','-axo','command=']).stdout.decode(errors='replace')
        if '/Applications/Google Chrome.app/Contents/' in processes: raise RestoreStopped('selected Chrome process exists')
    def preconditions(self,app,source):
        if platform.system()!='Darwin' or os.getuid()==0: raise RestoreStopped('requires non-root macOS')
        if app!=APP or app.is_symlink() or app.resolve()!=app: raise RestoreStopped('selected path mismatch')
        if source!=self.mount/'Google Chrome.app' or source.is_symlink(): raise RestoreStopped('vendor path mismatch')
        if not app.is_dir() or not source.is_dir(): raise RestoreStopped('missing bundle')
        if not os.access(app.parent,os.W_OK): raise RestoreStopped('ordinary parent write unavailable')
        # No running browser may observe a partial installation transition.
        self.assert_idle()
        info=plistlib.loads(self.command(['/usr/sbin/diskutil','info','-plist',str(self.mount)]).stdout)
        if not all(info.get(key) is False for key in ('Writable', 'WritableMedia', 'WritableVolume')):
            raise RestoreStopped('vendor mount not read-only')
        helpresult=self.command(['/usr/bin/ditto','--help'])
        helptext=(helpresult.stdout + helpresult.stderr).decode(errors='replace')
        # Current utility must advertise preservation, not just remembered semantics.
        if not all(x in helptext for x in ['--rsrc','--extattr','--acl','--qtn']):
            raise RestoreStopped('native preservation options not established')
    def acl_map(self,paths):
        result={}
        for offset in range(0,len(paths),100):
            batch=paths[offset:offset+100]; current=None
            out=self.command(['/bin/ls','-lde',*map(str,batch)]).stdout.decode(errors='strict')
            for line in out.splitlines():
                if re.match(r'\s*\d+:',line):
                    if current is None: raise RestoreStopped('ACL without path')
                    result[current].append(line.strip())
                else:
                    matches=[p for p in batch if line.endswith(' '+str(p)) or (' '+str(p)+' -> ') in line]
                    if len(matches)!=1: raise RestoreStopped('unrecognized ACL output')
                    current=matches[0];result[current]=[]
            if any(p not in result for p in batch): raise RestoreStopped('missing ACL path')
        return {p:tuple(v) for p,v in result.items()}
    def attributes(self,path):
        # Darwin ABI from Apple xnu bsd/sys/xattr.h. Read only, NOFOLLOW=1;
        # never load setxattr/removexattr or NOSECURITY options.
        lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
        listing=lib.listxattr;reading=lib.getxattr
        listing.argtypes=(ctypes.c_char_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int)
        reading.argtypes=(ctypes.c_char_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_int)
        listing.restype=reading.restype=ctypes.c_ssize_t
        encoded=os.fsencode(path);size=listing(encoded,None,0,1)
        if not 0<=size<=65536: raise RestoreStopped('attribute names unavailable or over limit')
        buf=ctypes.create_string_buffer(max(1,size))
        if listing(encoded,buf,size,1)!=size: raise RestoreStopped('attribute list changed')
        names=bytes(buf.raw[:size]).split(b'\0');result={}
        for name in filter(None,names):
            amount=reading(encoded,name,None,0,0,1)
            if not 0<=amount<=1048576: raise RestoreStopped('attribute value unavailable or over limit')
            value=ctypes.create_string_buffer(max(1,amount))
            if reading(encoded,name,value,amount,0,1)!=amount: raise RestoreStopped('attribute changed')
            result[name.decode('utf-8')]=hashlib.sha256(bytes(value.raw[:amount])).hexdigest()
        return result
    def snapshot(self,root):
        records=[];hardlinks={}
        paths=[root,*sorted(root.rglob('*'))];acls=self.acl_map(paths)
        for p in paths:
            s=p.lstat(); rel=str(p.relative_to(root)); target=None
            if p.is_symlink():
                target=os.readlink(p)
                if not p.resolve(strict=True).is_relative_to(root.resolve()): raise RestoreStopped('symlink escapes bundle')
                digest=None
            elif p.is_file(): digest=hashlib.sha256(p.read_bytes()).hexdigest()
            elif p.is_dir(): digest=None
            else: raise RestoreStopped('unsupported special file')
            attrs=self.attributes(p)
            linked=None
            if p.is_file() and not p.is_symlink():
                key=(s.st_dev,s.st_ino);linked=hardlinks.setdefault(key,rel)
            records.append((rel,stat.S_IMODE(s.st_mode),s.st_uid,s.st_gid,getattr(s,'st_flags',0),
                            target,digest,attrs,acls[p],s.st_mtime_ns,linked))
        return records
    def equivalent(self,source,target):
        a=self.snapshot(source);b=self.snapshot(target)
        # UID/GID may legitimately become the current installer; all content,
        # modes, flags, xattrs (including quarantine), links and ACLs must match.
        normalize=lambda rows:[tuple(v for i,v in enumerate(r) if i not in (2,3)) for r in rows]
        if normalize(a)!=normalize(b): raise RestoreStopped('copy metadata/content mismatch')
    def quarantine_equivalent(self,original,candidate):
        # Do not use an unquarantined download to avoid a quarantined installed app.
        old=any('com.apple.quarantine' in self.attributes(p) for p in [original,*original.rglob('*')])
        new='com.apple.quarantine' in self.attributes(candidate)
        if old and not new: raise RestoreStopped('quarantine retention policy unavailable')
    def verify(self,bundle):
        if bundle.is_symlink(): raise RestoreStopped('bundle root symlink')
        paths=[bundle,*sorted(bundle.rglob('*'))];acls=self.acl_map(paths)
        for p in paths:
            if not p.resolve(strict=True).is_relative_to(bundle.resolve()): raise RestoreStopped('bundle symlink escape')
            s=p.stat()
            if s.st_uid not in (0,os.getuid()) or s.st_mode&(stat.S_IWGRP|stat.S_IWOTH):
                raise RestoreStopped('bundle ownership/mode mismatch')
            if any(' deny ' not in (' '+a+' ') for a in acls[p]):
                raise RestoreStopped('unreviewed ACL grant')
        self.command(['/usr/bin/codesign','--verify','--deep','--strict','--verbose=2',str(bundle)])
        identity=self.command(['/usr/bin/codesign','-dv','--verbose=4',str(bundle)]).stderr.decode(errors='replace').splitlines()
        if ('Identifier=com.google.Chrome' not in identity or 'TeamIdentifier='+TEAM not in identity
            or 'Authority=Developer ID Application: Google LLC ('+TEAM+')' not in identity):
            raise RestoreStopped('vendor identity mismatch')
        self.command(['/usr/bin/codesign','--verify','-R=anchor apple generic',str(bundle)])
        self.command(['/usr/sbin/spctl','--assess','--type','execute','--verbose=4',str(bundle)])
    def copy(self,source,stage):
        if stage.exists() or stage.is_symlink(): raise RestoreStopped('staging collision')
        stage.parent.mkdir(mode=0o700)  # private exclusive container on same filesystem
        if stage.exists() or stage.is_symlink(): raise RestoreStopped('staging child collision')
        self.command(['/usr/bin/ditto','--rsrc','--extattr','--acl','--qtn',str(source),str(stage)],timeout=60)
    def rename(self,source,target):
        if target.exists() or target.is_symlink(): raise RestoreStopped('rename collision')
        # Apple's renamex_np RENAME_EXCL=4, bsd/sys/stdio.h; unlike mv -n,
        # an unexpected destination directory cannot turn this into nesting.
        # No fallback to overwriting rename if this facility is unavailable.
        library=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
        rename=library.renamex_np
        rename.argtypes=(ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint)
        rename.restype=ctypes.c_int
        if rename(os.fsencode(source),os.fsencode(target),4)!=0:
            raise RestoreStopped('exclusive rename failed errno='+str(ctypes.get_errno()))
        # No fallible postcondition here: caller journals the committed rename
        # immediately, then validates backup/selected contents with rollback armed.


class VendorRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        parsed=urlparse(newurl)
        if parsed.scheme!='https' or parsed.hostname!='dl.google.com':
            raise RestoreStopped('unexpected vendor redirect')
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def main():
    # Deliberately not a general path/URL install CLI. Only this official source
    # and the original selected path can reach restore(). No CI wiring yet.
    if platform.system()!='Darwin' or os.getuid()==0: raise RestoreStopped('requires non-root macOS')
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    temp=Path(tempfile.mkdtemp(prefix='paper-lab-vendor-',dir=os.environ.get('RUNNER_TEMP')))
    dmg=temp/'vendor.dmg';mount=temp/'mount';mount.mkdir()
    evidence=[];backend=Native(mount,evidence,out/'transaction.jsonl');attached=False;result={'status':'STOPPED'}
    try:
        opener=urllib.request.build_opener(VendorRedirect())
        with opener.open(URL,timeout=60) as response, dmg.open('xb') as f:
            if response.status!=200: raise RestoreStopped('vendor HTTP status')
            total=0;started=time.monotonic()
            while chunk:=response.read(1024*1024):
                total+=len(chunk)
                if time.monotonic()-started>60: raise RestoreStopped('vendor total download deadline')
                if total>512*1024*1024: raise RestoreStopped('vendor size limit')
                f.write(chunk)
        evidence.append({'vendor_url':URL,'bytes':total,'sha256':hashlib.sha256(dmg.read_bytes()).hexdigest()})
        backend.command(['/usr/bin/hdiutil','verify',str(dmg)],timeout=30)
        backend.command(['/usr/bin/hdiutil','attach','-readonly','-nobrowse','-noautoopen','-plist','-mountpoint',str(mount),str(dmg)],timeout=30);attached=True
        result=restore(backend,APP,mount/'Google Chrome.app')
    except Exception as error:
        result={'status':'STOPPED','reason':str(error),'temporary_directory_retained':str(temp)}
        raise
    finally:
        if attached:
            try: backend.command(['/usr/bin/hdiutil','detach',str(mount)])
            except Exception as error: result['detach_error']=str(error)
        (out/'restore.json').write_text(json.dumps({'result':result,'evidence':evidence},indent=2))

if __name__=='__main__': main()

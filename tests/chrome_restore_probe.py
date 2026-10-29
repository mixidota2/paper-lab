"""Native prerequisite observation only: no installation, rename or app launch."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import tempfile
import time
import urllib.request
import chrome_restore as restore

class ProbeNative(restore.Native):
    def rename(self,*args):
        raise restore.RestoreStopped('installation/rename forbidden in probe')


def observe(evidence,name,operation):
    print(json.dumps({'stage':name,'status':'STARTED / not complete'}),flush=True)
    started=time.monotonic()
    try:
        value=operation()
    except Exception as error:
        evidence.append({'stage':name,'status':'FAIL','seconds':time.monotonic()-started,'reason':str(error)})
        return False,None
    evidence.append({'stage':name,'status':'PASS','seconds':time.monotonic()-started})
    return True,value


def acquire(path,opener=None):
    opener=opener or urllib.request.build_opener(restore.VendorRedirect())
    start=time.monotonic();total=0
    with opener.open(restore.URL,timeout=30) as response,path.open('xb') as output:
        if response.status!=200: raise restore.RestoreStopped('vendor HTTP status')
        effective=response.geturl()
        parsed=restore.urlparse(effective)
        if parsed.scheme!='https' or parsed.hostname!='dl.google.com': raise restore.RestoreStopped('vendor URL not allowed')
        while chunk:=response.read(1024*1024):
            total+=len(chunk)
            if total>512*1024*1024 or time.monotonic()-start>60: raise restore.RestoreStopped('vendor acquisition limit')
            output.write(chunk)
    return {'requested_url':restore.URL,'effective_url':effective,'bytes':total,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def probe(backend,source,app,stage,evidence):
    # No install even when every result is PASS. Old-bundle verification failure
    # is recorded independently and never reclassified by a new artifact result.
    ok,_=observe(evidence,'same-original-path-and-native-copy-prerequisites',lambda:backend.preconditions(app,source))
    if not ok:return
    _,old=observe(evidence,'original-content-and-metadata-fingerprint',lambda:backend.snapshot(app))
    observe(evidence,'original-strict-signature-and-Gatekeeper',lambda:backend.verify(app))
    ok,_=observe(evidence,'vendor-strict-signature-and-Gatekeeper',lambda:backend.verify(source))
    if not ok:return
    # Missing original-to-vendor quarantine guard makes installation impossible,
    # but a no-launch/no-install copy observation remains safe and independent.
    observe(evidence,'original-to-vendor-quarantine-retention-policy',lambda:backend.quarantine_equivalent(app,source))
    ok,_=observe(evidence,'native-copy-to-RUNNER_TEMP-only',lambda:backend.copy(source,stage))
    if not ok:return
    observe(evidence,'source-to-copy-content-and-metadata-equality',lambda:backend.equivalent(source,stage))
    observe(evidence,'copied-bundle-strict-signature-and-Gatekeeper',lambda:backend.verify(stage))
    observe(evidence,'original-to-copy-quarantine-retention-policy',lambda:backend.quarantine_equivalent(app,stage))
    def original_unchanged():
        if old is None or backend.snapshot(app)!=old:raise restore.RestoreStopped('original fingerprint unavailable or changed')
    observe(evidence,'original-untouched-after-probe',original_unchanged)


class ProgressList(list):
    def __init__(self): super().__init__();self.checkpoint=lambda:None
    def append(self,value):
        super().append(value);self.checkpoint()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    if platform.system()!='Darwin' or os.getuid()==0:raise restore.RestoreStopped('requires non-root macOS')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    temp=Path(tempfile.mkdtemp(prefix='paper-lab-native-probe-',dir=os.environ.get('RUNNER_TEMP')))
    mount=temp/'mount';mount.mkdir();dmg=temp/'vendor.dmg';stage=temp/'copy'/'Google Chrome.app'
    commands=ProgressList();observations=ProgressList();backend=ProbeNative(mount,commands);attached=False
    report={'classification':'DIAGNOSTIC ONLY / NOT A LAB GATE','browser':'NOT STARTED','installation':'NOT ATTEMPTED','observations':observations,'commands':commands,'temporary_directory_retained':str(temp)}
    started=time.monotonic()
    def checkpoint():
        report['elapsed_seconds']=time.monotonic()-started
        (out/'probe.json').write_text(json.dumps(report,indent=2))
    commands.checkpoint=observations.checkpoint=checkpoint
    report['prerequisites']='IN PROGRESS / never a gate result';checkpoint()
    try:
        report['acquisition']=acquire(dmg)
        backend.command(['/usr/bin/hdiutil','verify',str(dmg)])
        backend.command(['/usr/bin/hdiutil','attach','-readonly','-nobrowse','-noautoopen','-plist','-mountpoint',str(mount),str(dmg)]);attached=True
        probe(backend,mount/'Google Chrome.app',restore.APP,stage,observations)
    except BaseException as error:
        report['stopped_reason']=str(error)
        raise
    finally:
        if attached:
            try:backend.command(['/usr/bin/hdiutil','detach',str(mount)])
            except Exception as error:report['detach_error']=str(error)
        else:report['attachment_outcome']='not confirmed; do not detach an unverified mount'
        report['elapsed_seconds']=time.monotonic()-started
        report['prerequisites']='FAIL/UNCONFIRMED' if any(x['status']!='PASS' for x in observations) or not observations or 'stopped_reason' in report else 'OBSERVED; still NOT INSTALLED or browser-tested'
        (out/'probe.json').write_text(json.dumps(report,indent=2))
    if report['prerequisites']=='FAIL/UNCONFIRMED':raise SystemExit(2)

if __name__=='__main__':main()

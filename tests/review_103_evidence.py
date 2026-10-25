"""One durable outcome for completed assertions versus interrupted browser runs."""
from html import escape
import json
from pathlib import Path
import subprocess
import sys
import traceback


class ProtectionStop(RuntimeError):
    """Abort without attempting more interactions or a weaker browser route."""


def console_diagnostic(error):
    """Allowlisted facts only; arbitrary exception text stays in the artifact."""
    category = type(error).__name__
    known = {'CalledProcessError', 'TimeoutExpired', 'AssertionError',
             'ProtectionStop', 'KeyboardInterrupt', 'RuntimeError', 'OSError'}
    summary = {'type': category if category in known else 'Exception',
               'message': 'Failure details retained in report.json'}
    commands = [
        ['/usr/bin/codesign', '--verify', '--deep', '--strict', '--verbose=2',
         '/Applications/Google Chrome.app'],
        ['/usr/bin/codesign', '-dv', '--verbose=4', '/Applications/Google Chrome.app'],
        ['/usr/bin/codesign', '--verify', '-R=anchor apple generic',
         '/Applications/Google Chrome.app'],
    ]
    if isinstance(error, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
        if error.cmd in commands:
            summary['message'] = str(error)  # Exact fixed command; no arbitrary arguments.
            if isinstance(error, subprocess.CalledProcessError):
                summary['returncode'] = error.returncode
            # Never dump stderr: return only recognized literal reason phrases.
            stderr = error.stderr or ''
            if isinstance(stderr, bytes):
                stderr = stderr.decode('utf-8', errors='replace')
            reasons = ['a sealed resource is missing or invalid',
                       'code object is not signed at all',
                       'invalid signature', 'resource envelope is obsolete',
                       'code failed to satisfy specified code requirement(s)',
                       'CSSMERR_TP_CERT_REVOKED', 'CSSMERR_TP_CERT_EXPIRED',
                       'bundle format is ambiguous', 'unsealed contents present',
                       'main executable failed strict validation',
                       'file added', 'file modified', 'file missing']
            summary['recognized_stderr_reasons'] = [x for x in reasons if x in stderr]
    return summary


class RunEvidence:
    def __init__(self,out,plan):
        self.out=Path(out);self.page=None;self.current=None
        self.report={'preflight':plan,'phase':'startup','browser':'NOT STARTED','status':'RUNNING',
            'cases':[],'events':[],'action_checks':[],'external_links':[],
            'manual_screenshot_review':'NOT TESTED','screen_records':[]}
        self.persist()

    def persist(self):
        (self.out/'report.json').write_text(json.dumps(self.report,ensure_ascii=False,indent=2))

    def event(self,kind,message,page=None):
        p=page or self.page
        self.report['events'].append({'kind':kind,'message':str(message),'case':self.current,
            'page':getattr(p,'url',None)})

    def diagnostic(self,error,page=None):
        p=page or self.page
        return {'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc(),
                'case':self.current,'page':getattr(p,'url',None),
                'console':console_diagnostic(error)}

    def capture_failure(self,page=None,error=None):
        p=page or self.page
        if page is not None:self.page=page
        item={'case':self.current,'page':getattr(p,'url',None),'status':'NOT CAPTURED'}
        if error is not None:item['error']=self.diagnostic(error,p)
        try:
            if p is None or p.is_closed():raise RuntimeError('No live page available at failure')
            name=f'failure-{len(self.report["screen_records"]):03d}.png'
            p.screenshot(path=str(self.out/name),full_page=False,timeout=5000)
            item.update(status='CAPTURED current viewport',file=name)
        except Exception as e:item['capture_error']={'type':type(e).__name__,'message':str(e)}
        self.report['screen_records'].append(item);self.persist()

    def case(self,name,fn,fatal=False):
        self.current=name
        try:
            fn();self.report['cases'].append({'name':name,'status':'PASS','page':getattr(self.page,'url',None)})
        except ProtectionStop as error:
            self.report["interrupted_case"]=self.diagnostic(error)
            raise
        except Exception as e:
            self.report['cases'].append({'name':name,'status':'FAIL',**self.diagnostic(e)})
            self.capture_failure(error=e)
            if fatal:raise
        except BaseException as error:
            self.report["interrupted_case"]=self.diagnostic(error)
            raise
        finally:self.persist();self.current=None

    def finalize(self,completed,interruption=None):
        self.report['execution_completed']=completed
        if interruption is not None:
            self.report.update(status='STOPPED',interruption=interruption)
            if self.report['browser']!='NOT STARTED':self.report['browser']='INTERRUPTED'
            (self.out/'stopped.json').write_text(json.dumps(interruption,ensure_ascii=False,indent=2))
        elif completed:
            self.report['browser']='EXECUTED'
            self.report['status']='AWAITING AUTOMATIC VALIDATION'
        else:self.report['status']='STOPPED'
        from review_103_report import validation
        self.report.update(validation(self.report,self.report['preflight']))
        if self.report['status']!='STOPPED':
            self.report['status']='AUTOMATED PASS / publication pending' if self.report['automatic_status']=='PASS' else 'FAIL'
        self.persist()
        if interruption is not None:
            # Emit exactly the bounded fields also saved in stopped/report.json.
            # Logging must not change a stopped run into a successful one.
            summary = interruption.get('console', {'type': 'Interruption',
                'message': 'Failure details retained in report.json'})
            try:
                print('LAB_REVIEW_STOP '+json.dumps(summary), file=sys.stderr, flush=True)
            except OSError:
                pass  # Durable evidence and the existing failure result remain.
        links=''.join(f'<li><a href="{escape(str(p.relative_to(self.out)))}">{escape(str(p.relative_to(self.out)))}</a></li>' for p in sorted(self.out.rglob('*.png')))
        (self.out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>103 Lab review evidence</title><h1>原寸の画面記録</h1><p>状態：'+escape(self.report['status'])+'</p><p>目視確認は未実施です。<a href="report.json">ケース・エラー・画面記録</a></p><ul>'+links+'</ul>')
        return self.report

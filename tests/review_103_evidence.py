"""One durable outcome for completed assertions versus interrupted browser runs."""
import ast
import ctypes
import errno
import hashlib
from html import escape
import json
import os
import stat
import time
from pathlib import Path
import re
import subprocess
import sys
import traceback
import unicodedata


class ProtectionStop(RuntimeError):
    """Abort without attempting more interactions or a weaker browser route."""


STDERR_INPUT_LIMIT = 8192
STDERR_TEXT_LIMIT = 2048


def bounded_stderr(raw):
    """Bound parsing/output; byte length is bytes or UTF-8 length for text."""
    if raw is None:
        return {'present': False, 'byte_length': None, 'truncated': False, 'text': None}
    if isinstance(raw, bytes):
        size = len(raw)
        prefix = raw[:STDERR_INPUT_LIMIT]
    else:
        # Count without allocating a second unbounded copy of captured text.
        size = sum(len(raw[i:i+STDERR_INPUT_LIMIT].encode('utf-8', errors='replace'))
                   for i in range(0, len(raw), STDERR_INPUT_LIMIT))
        prefix = raw[:STDERR_INPUT_LIMIT].encode('utf-8', errors='replace')[:STDERR_INPUT_LIMIT]
    text = prefix.decode('utf-8', errors='replace')
    # Remove terminal escape strings/sequences before redaction, including OSC links.
    text = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\|$)', '', text)
    text = re.sub(r'\x1b[P^_][\s\S]*?(?:\x1b\\|$)', '', text)
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]|\x1b[@-_]', '', text)
    text = ''.join(' ' if c == '\t' else c for c in text
                   if c in '\n\t' or unicodedata.category(c) not in ('Cc', 'Cf'))

    def redact_url(match):
        url = match.group()
        url = re.sub(r'(?<=://)[^/?#]*@', '[REDACTED]@', url)
        return re.split(r'[?#]', url, maxsplit=1)[0] + ('?[REDACTED]' if re.search(r'[?#]', url) else '')

    text = re.sub(r'''(?i)\b[a-z][a-z0-9+.-]*://[^\s<>"']+''', redact_url, text)
    text = re.sub(r'''(?i)(\b(?:bearer|basic)\s+)(?:"[^"]*(?:"|$)|'[^']*(?:'|$)|[^\s,;]+)''', r'\1[REDACTED]', text)
    text = re.sub(
        r'''(?i)(\b[\w.-]*(?:token|password|passwd|pwd|secret|credential|api[_-]?key|access[_-]?key(?:[_-]?id)?|key|signature|sig|authorization|auth|session|cookie)(?:[_-][\w.-]+)*["']?\s*[:=]\s*)(?:"[^"]*(?:"|$)|'[^']*(?:'|$)|[^\s,;]+)''',
        r'\1[REDACTED]', text)
    text = re.sub(r'(?i)(/(?:Users|home)/)[^/\r\n]+', r'\1[USER]', text)
    text = re.sub(r'(?i)([A-Z]:\\Users\\)[^\\\r\n]+', r'\1[USER]', text)
    text = re.sub(r'~[^/\r\n]*/', '~[USER]/', text)
    text = re.sub(r'''/private/[^\s<>"']+''', '[PRIVATE_PATH]', text)
    encoded = text.encode('utf-8')
    return {'present': True, 'byte_length': size,
            'truncated': size > STDERR_INPUT_LIMIT or len(encoded) > STDERR_TEXT_LIMIT,
            'text': encoded[:STDERR_TEXT_LIMIT].decode('utf-8', errors='ignore')}


XATTR_BUNDLE_COMPONENTS = ('Applications', 'Google Chrome.app')
XATTR_NAMES = frozenset({'com.apple.FinderInfo', 'com.apple.ResourceFork',
                         'com.apple.quarantine', 'com.apple.provenance'})
XATTR_MAX_PATHS = 1024
XATTR_MAX_RECORDS = 16
XATTR_MAX_SECONDS = 3
XATTR_NAME_BYTES = 8192


def darwin_xattr_reader():
    """Apple flistxattr(2): bounded NUL-separated names on an already-open fd.

    https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/flistxattr.2.html
    No size-growth retry, values, path-based lookup, or non-Darwin fallback.
    """
    if sys.platform != 'darwin':
        raise OSError(errno.ENOTSUP, 'Darwin names interface unavailable')
    library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    function = library.flistxattr
    function.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
    function.restype = ctypes.c_ssize_t

    def names(fd):
        buffer = ctypes.create_string_buffer(XATTR_NAME_BYTES)
        size = function(fd, buffer, XATTR_NAME_BYTES, 0)
        if size < 0:
            raise OSError(ctypes.get_errno(), 'Attribute names unavailable')
        if size > XATTR_NAME_BYTES:
            raise OSError(errno.ERANGE, 'Attribute names exceed bound')
        if size == 0:
            return []
        raw = buffer.raw[:size]
        if not raw.endswith(b'\0'):
            raise OSError(errno.EINVAL, 'Malformed attribute names')
        return raw[:-1].decode('utf-8', errors='strict').split('\0')

    return names


def chrome_xattr_names():
    """Bounded read-only names, never values; every open rejects symlinks."""
    result = {'records': [], 'visited': 0, 'errors': 0, 'omitted': 0,
              'unlisted_names': 0, 'limited': False}
    names_for_fd = darwin_xattr_reader()
    deadline = time.monotonic() + XATTR_MAX_SECONDS
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK

    def visit(fd, relative, depth):
        if result['visited'] >= XATTR_MAX_PATHS or time.monotonic() >= deadline:
            result['limited'] = True
            return
        result['visited'] += 1
        mode = os.fstat(fd).st_mode
        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
            result['omitted'] += 1
            return
        try:
            names = names_for_fd(fd)
            allowed = sorted(XATTR_NAMES.intersection(names))
            result['unlisted_names'] += min(64, sum(n not in XATTR_NAMES for n in names))
            if allowed:
                if len(result['records']) < XATTR_MAX_RECORDS:
                    result['records'].append({'path': relative or '.', 'names': allowed})
                else:
                    result['omitted'] += 1
                    result['limited'] = True
        except OSError:
            result['errors'] += 1
        if not stat.S_ISDIR(mode):
            return
        if depth >= 32:
            result['limited'] = True
            return
        try:
            with os.scandir(fd) as entries:
                for entry in entries:
                    if result['visited'] >= XATTR_MAX_PATHS or time.monotonic() >= deadline:
                        result['limited'] = True
                        break
                    name = entry.name
                    path = relative + '/' + name if relative else name
                    # Reject control/escape characters, oversized or sensitive names.
                    if (name in ('.', '..') or len(path) > 240 or
                        not re.fullmatch(r'[A-Za-z0-9 _().+/-]+', path) or
                        re.search(r'(?i)token|password|secret|credential|api[_-]?key', path)):
                        result['omitted'] += 1
                        result['limited'] = True
                        continue
                    child = None
                    try:
                        mode = entry.stat(follow_symlinks=False).st_mode
                        if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                            result['omitted'] += 1
                            continue
                        child = os.open(name, flags, dir_fd=fd)
                        visit(child, path, depth + 1)
                    except OSError:
                        result['errors'] += 1
                    finally:
                        if child is not None:
                            os.close(child)
        except OSError:
            result['errors'] += 1

    root = None
    try:
        root = os.open('/', flags | os.O_DIRECTORY)
        for component in XATTR_BUNDLE_COMPONENTS:
            child = os.open(component, flags | os.O_DIRECTORY, dir_fd=root)
            os.close(root)
            root = child
        visit(root, '', 0)
    finally:
        if root is not None:
            os.close(root)
    return result


def console_diagnostic(error):
    """Allowlisted facts only; arbitrary exception text stays in the artifact."""
    category = type(error).__name__
    known = {'CalledProcessError', 'TimeoutExpired', 'AssertionError',
             'ProtectionStop', 'KeyboardInterrupt', 'RuntimeError', 'OSError'}
    summary = {'type': category if category in known else 'Exception',
               'message': 'Exception type only; message and stderr omitted from console'}
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
            # Only these exact commands may expose bounded, sanitized stderr.
            summary['stderr'] = bounded_stderr(error.stderr)
            stderr = summary['stderr']['text'] or ''
            reasons = ['a sealed resource is missing or invalid',
                       'code object is not signed at all',
                       'invalid signature', 'resource envelope is obsolete',
                       'code failed to satisfy specified code requirement(s)',
                       'CSSMERR_TP_CERT_REVOKED', 'CSSMERR_TP_CERT_EXPIRED',
                       'bundle format is ambiguous', 'unsealed contents present',
                       'main executable failed strict validation',
                       'file added', 'file modified', 'file missing']
            summary['recognized_stderr_reasons'] = [x for x in reasons if x in stderr]
            if (isinstance(error, subprocess.CalledProcessError) and
                error.returncode != 0 and error.cmd == commands[0]):
                try:
                    summary['chrome_xattr_names'] = chrome_xattr_names()
                except Exception:
                    # Diagnostic failure must never replace the original failure.
                    summary['chrome_xattr_names'] = {'status': 'unavailable'}
    return summary


DIAGNOSTIC_LIMIT = 12
CASE_EXCEPTION_TYPES = frozenset({
    'AssertionError', 'KeyError', 'ValueError', 'TypeError', 'IndexError',
    'AttributeError', 'TimeoutError', 'RuntimeError', 'OSError',
    'CalledProcessError', 'TimeoutExpired', 'ProtectionStop', 'KeyboardInterrupt',
})
DIAGNOSTIC_SOURCES = frozenset({
    'featurearc_review.py', 'episem_review.py', 'trace_review.py', 'catalog_expectations.py', 'wrapped_review.py',
    'shelf_survey_browser.py', 'review_103_report.py', 'review_103_external.py',
    'review_103.py', 'review_103_capture.py', 'review_103_evidence.py',
    'reference_browser.py', 'macos_chrome_cdp.py', 'macos_cdp_review.py',
})


def planned_identifier(value, allowed):
    return (value if isinstance(value, str) and value in allowed
            and re.fullmatch(r'[a-z0-9-]{1,120}', value) else 'UNKNOWN')


def case_diagnostic(error, name, plan):
    """No exception text, URLs, paths or arbitrary runtime function names."""
    result = {'case': planned_identifier(name, plan.get('required_cases', [])),
              'type': type(error).__name__ if type(error).__name__ in CASE_EXCEPTION_TYPES else 'Exception',
              'source': None}
    root = Path(__file__).resolve().parent
    tb = error.__traceback__
    while tb is not None:
        code = tb.tb_frame.f_code
        path = Path(code.co_filename)
        if path.name in DIAGNOSTIC_SOURCES and path == root / path.name:
            try:
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() == plan.get('source_hashes', {}).get(path.name):
                    tree = ast.parse(raw)
                    functions = [n for n in ast.walk(tree)
                                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                                 and n.name == code.co_name and n.lineno <= tb.tb_lineno <= n.end_lineno
                                 and re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]{0,79}', n.name)]
                    if functions:
                        result['source'] = {'file': path.name, 'line': tb.tb_lineno,
                                            'function': functions[0].name}
            except (OSError, SyntaxError, ValueError):
                pass
        tb = tb.tb_next
    return result


def summary_failure(case, plan):
    safe = case.get('safe_case', {})
    result = {'case': planned_identifier(case.get('name'), plan.get('required_cases', [])),
              'type': safe.get('type') if safe.get('type') in CASE_EXCEPTION_TYPES else 'Exception',
              'source': None}
    source = safe.get('source')
    if isinstance(source, dict) and source.get('file') in DIAGNOSTIC_SOURCES:
        path = Path(__file__).resolve().parent / source['file']
        try:
            raw = path.read_bytes()
            line = source.get('line')
            if (hashlib.sha256(raw).hexdigest() == plan.get('source_hashes', {}).get(path.name)
                    and type(line) is int):
                for node in ast.walk(ast.parse(raw)):
                    if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and node.name == source.get('function')
                            and re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]{0,79}', node.name)
                            and node.lineno <= line <= node.end_lineno):
                        result['source'] = {'file': path.name, 'line': line, 'function': node.name}
                        break
        except (OSError, SyntaxError, ValueError):
            pass
    return result


def case_summary(report, plan):
    """Bounded diagnostic view only; never used to determine acceptance."""
    cases = report.get('cases', [])
    failed = [c for c in cases if c.get('status') != 'PASS']
    expected = plan.get('required_cases', [])
    recorded = {c.get('name') for c in cases}
    missing_cases = [n for n in expected if n not in recorded]
    groups = {(a.get('slug'), a.get('width')) for a in report.get('action_checks', [])
              if a.get('status', '').startswith('CONFIRMED:')}
    missing_groups = [g for g in plan.get('semantic_groups', []) if tuple(g) not in groups]
    slugs = {g[0] for g in plan.get('semantic_groups', [])}
    return {'failed_count': len(failed),
            'failed': [summary_failure(c, plan) for c in failed[:DIAGNOSTIC_LIMIT]],
            'missing_case_count': len(missing_cases),
            'missing_cases': [planned_identifier(n, expected) for n in missing_cases[:DIAGNOSTIC_LIMIT]],
            'missing_semantic_count': len(missing_groups),
            'missing_semantic': [[planned_identifier(g[0], slugs),
                                  g[1] if type(g[1]) is int and g[1] in (360,390,768,1440) else None]
                                 for g in missing_groups[:DIAGNOSTIC_LIMIT]],
            'truncated': any(len(xs) > DIAGNOSTIC_LIMIT for xs in (failed, missing_cases, missing_groups))}


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
        started=time.monotonic()
        self.report['current_case_timing']={'case':planned_identifier(name,self.report['preflight'].get('required_cases',[])),
                                            'started_monotonic_s':started}
        self.persist()
        try:
            fn();self.report['cases'].append({'name':name,'status':'PASS','page':getattr(self.page,'url',None)})
        except ProtectionStop as error:
            self.report["interrupted_case"]=self.diagnostic(error)
            raise
        except Exception as e:
            self.report['cases'].append({'name':name,'status':'FAIL','safe_case':case_diagnostic(e,name,self.report['preflight']),**self.diagnostic(e)})
            self.capture_failure(error=e)
            if fatal:raise
        except BaseException as error:
            self.report["interrupted_case"]=self.diagnostic(error)
            raise
        finally:
            timing={**self.report['current_case_timing'], 'elapsed_s':max(0,time.monotonic()-started)}
            # At most one timing per planned identifier; no arbitrary DOM content.
            if name in self.report['preflight'].get('required_cases',[]):
                self.report.setdefault('case_timings',{})[name]=timing
            self.report['current_case_timing']=None
            self.persist();self.current=None

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
                'message': 'Exception details omitted from console'})
            try:
                print('LAB_REVIEW_STOP '+json.dumps(summary), file=sys.stderr, flush=True)
            except (OSError, ValueError):
                pass  # Durable evidence and the existing failure result remain.
        if interruption is None:
            try:
                print('LAB_REVIEW_CASES '+json.dumps(case_summary(self.report, self.report['preflight'])),
                      file=sys.stderr, flush=True)
            except (OSError, ValueError):
                pass  # Diagnostic transport cannot alter the gate outcome.
        links=''.join(f'<li><a href="{escape(str(p.relative_to(self.out)))}">{escape(str(p.relative_to(self.out)))}</a></li>' for p in sorted(self.out.rglob('*.png')))
        (self.out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>103 Lab review evidence</title><h1>原寸の画面記録</h1><p>状態：'+escape(self.report['status'])+'</p><p>目視確認は未実施です。<a href="report.json">ケース・エラー・画面記録</a></p><ul>'+links+'</ul>')
        return self.report

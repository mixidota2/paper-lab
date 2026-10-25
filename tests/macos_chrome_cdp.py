"""Existing signed macOS Chrome, minimal direct launch, loopback-only CDP.

No Playwright launch flags, persistent profile, sandbox edits or elevated access.
"""
from contextlib import contextmanager
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import socket
import stat
import subprocess
import tempfile
import time
from urllib.parse import urlparse

APP = Path('/Applications/Google Chrome.app')
CHROME = APP / 'Contents/MacOS/Google Chrome'


def command(args):
    return subprocess.run(args, text=True, capture_output=True, check=True, timeout=30)


def verify_distribution():
    assert platform.system() == 'Darwin' and os.getuid() != 0
    # Existing administrator-owned /Applications can be group-writable by admin;
    # the application itself must have no group/other-write bits anywhere.
    paths = sorted({APP, *APP.parents, *APP.rglob('*')})
    for path in paths:
        target = path.resolve(strict=True)
        info = target.stat()
        assert info.st_uid in (0, os.getuid()), ('Unexpected owner', str(path))
        assert not info.st_mode & stat.S_IWOTH, ('Other-writable path', str(path))
        if info.st_mode & stat.S_IWGRP:
            assert path == Path('/Applications') and info.st_uid == 0 and info.st_gid == 80, ('Group-writable app path', str(path))
        if path in (APP, CHROME, *APP.parents):
            print('Chrome path:', str(path), 'resolved:', str(target), 'uid/gid:',
                  info.st_uid, info.st_gid, 'mode:', oct(stat.S_IMODE(info.st_mode)), flush=True)
    # Inspect ACLs on bundle contents and parents in bounded argument batches.
    acl_count = 0
    for offset in range(0, len(paths), 100):
        listing = command(['/bin/ls', '-lde', *map(str, paths[offset:offset + 100])]).stdout
        for line in listing.splitlines():
            if re.match(r'\s*\d+:', line):
                acl_count += 1
                # Deny entries preserve protections; unknown allow entries stop.
                assert ' deny ' in line, 'Application ACL grants require review'
    print('Chrome ACL inspection: paths', len(paths), 'deny entries', acl_count, flush=True)
    result = command(['/usr/bin/codesign', '--verify', '--deep', '--strict', '--verbose=2', str(APP)])
    print('Signature verification:', result.stderr.strip(), flush=True)
    signature = command(['/usr/bin/codesign', '-dv', '--verbose=4', str(APP)]).stderr
    identity = [line for line in signature.splitlines() if line.startswith(('Identifier=', 'Authority=', 'TeamIdentifier='))]
    print('Signature identity:', json.dumps(identity), flush=True)
    assert 'Identifier=com.google.Chrome' in identity
    assert any(line.startswith('Authority=Developer ID Application: Google LLC (') for line in identity)
    command(['/usr/bin/codesign', '--verify', '-R=anchor apple generic', str(APP)])
    print('Chrome version:', command([str(CHROME), '--version']).stdout.strip(), flush=True)
    print('Chrome executable sha256:', hashlib.sha256(CHROME.read_bytes()).hexdigest(), flush=True)


def verify_socket(pid, port):
    result = command(['/usr/sbin/lsof', '-nP', '-a', '-p', str(pid), '-iTCP', '-sTCP:LISTEN', '-Fn'])
    endpoints = [line[1:] for line in result.stdout.splitlines() if line.startswith('n')]
    assert endpoints == [f'127.0.0.1:{port}'], ('Unexpected listening sockets', endpoints)
    print('Verified CDP listener:', pid, endpoints, flush=True)


def connect_checked_cdp(pw):
    endpoint = os.environ['LAB_CDP_URL']
    url = urlparse(endpoint)
    assert url.scheme == 'http' and url.hostname == '127.0.0.1' and url.port
    verify_socket(int(os.environ['LAB_CHROME_PID']), url.port)
    browser = pw.chromium.connect_over_cdp(endpoint, no_defaults=True, is_local=True, timeout=15000)
    print('Connected engine: macOS Google Chrome', browser.version, 'CDP/no_defaults=True', flush=True)
    return browser


def verify_seatbelt(browser):
    session = browser.new_browser_cdp_session()
    try:
        processes = session.send('SystemInfo.getProcessInfo')['processInfo']
    finally:
        session.detach()
    library = ctypes.CDLL('/usr/lib/libsandbox.1.dylib', use_errno=True)
    check = library.sandbox_check
    check.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int)
    check.restype = ctypes.c_int
    renderers = [p for p in processes if p['type'] == 'renderer']
    assert renderers, 'No renderer process observed'
    for process in renderers:
        os.kill(int(process['id']), 0)  # Confirm the CDP-reported renderer is alive.
        identity = command(['/bin/ps', '-p', str(process['id']), '-o', 'uid=,comm=']).stdout.strip()
        assert identity.split(maxsplit=1)[0] == str(os.getuid()), identity
        assert 'Google Chrome Helper (Renderer)' in identity, identity
        ctypes.set_errno(0)
        result = check(int(process['id']), None, 0)
        print('Renderer Seatbelt:', process['id'], result, 'errno:', ctypes.get_errno(), flush=True)
        assert result == 1, 'Renderer sandbox is not confirmed'
        os.kill(int(process['id']), 0)


@contextmanager
def chrome_process():
    verify_distribution()
    process = None
    port = None
    with tempfile.TemporaryDirectory(prefix='paper-lab-chrome-') as directory:
        profile = Path(directory) / 'profile'
        profile.mkdir(mode=0o700)
        stderr_path = Path(directory) / 'chrome-stderr.txt'
        args = [str(CHROME), '--headless', '--remote-debugging-address=127.0.0.1',
                '--remote-debugging-port=0', f'--user-data-dir={profile}',
                '--no-first-run', '--no-default-browser-check', 'about:blank']
        print('Direct Chrome argv:', json.dumps(args), flush=True)
        try:
            with stderr_path.open('w') as stderr:
                process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=stderr, start_new_session=True)
                active = profile / 'DevToolsActivePort'
                deadline = time.monotonic() + 30
                while not active.exists():
                    assert process.poll() is None, 'Chrome exited before creating its temporary CDP endpoint'
                    assert time.monotonic() < deadline, 'Temporary CDP endpoint not observed'
                    time.sleep(.1)
                port = int(active.read_text().splitlines()[0])
                verify_socket(process.pid, port)  # No CDP client before socket verification.
                yield f'http://127.0.0.1:{port}', process.pid
        finally:
            if process is not None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
                if port is not None:
                    with socket.socket() as probe:
                        probe.settimeout(1)
                        assert probe.connect_ex(('127.0.0.1', port)) != 0, 'Temporary CDP listener remains open'
                print('Chrome process group ended; CDP listener closed', flush=True)
    assert not Path(directory).exists()
    print('Temporary Chrome profile removed', flush=True)

"""Run only Playwright's pinned Firefox with unchanged, observed sandbox settings."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat

import playwright
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def diagnose_timeout(page):
    """Observe only this test's descendants and allowlisted diagnostic DOM fields."""
    statuses = {}
    for entry in Path('/proc').iterdir():
        if entry.name.isdecimal():
            try:
                fields = dict(line.split(':', 1) for line in (entry / 'status').read_text().splitlines())
                statuses[int(entry.name)] = {k: fields[k].strip() for k in
                    ('Name', 'PPid', 'Uid', 'NoNewPrivs', 'Seccomp', 'Seccomp_filters') if k in fields}
            except (OSError, ValueError):
                pass  # Processes can exit while the read-only snapshot is taken.
    descendants = {os.getpid()}
    while True:
        expanded = descendants | {pid for pid, row in statuses.items()
                                  if int(row['PPid']) in descendants}
        if expanded == descendants:
            break
        descendants = expanded
    for pid in sorted(descendants):
        row = statuses.get(pid, {})
        namespaces = {}
        for kind in ('user', 'pid', 'net', 'mnt'):
            try:
                namespaces[kind] = os.readlink(f'/proc/{pid}/ns/{kind}')
            except OSError:
                namespaces[kind] = 'NOT OBSERVED'
        try:
            # Emit only a role marker, never full command lines or environment.
            content = b'-contentproc' in Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
        except OSError:
            content = None
        print('Firefox test process:', json.dumps({'pid': pid, 'content_process': content,
              'status': row, 'namespaces': namespaces}), flush=True)
    for name in ('/proc/sys/kernel/apparmor_restrict_unprivileged_userns',
                 '/sys/module/apparmor/parameters/enabled'):
        try:
            print('OS sandbox setting:', name, Path(name).read_text().strip(), flush=True)
        except OSError:
            print('OS sandbox setting:', name, 'NOT OBSERVED', flush=True)
    try:
        print('Diagnostic page URL:', page.url, flush=True)
        fields = page.evaluate('''() => ({url: location.href, documentURI: document.documentURI,
            readyState: document.readyState, sandboxRows: document.querySelectorAll('#sandbox-tbody tr').length,
            bodyChildren: document.body?.children.length ?? null})''')
        print('Diagnostic DOM:', json.dumps(fields), flush=True)
        target = Path('firefox-diagnostics')
        target.mkdir(exist_ok=True)
        if fields['sandboxRows']:
            page.locator('#sandbox-tbody').screenshot(path=str(target / 'sandbox-table.png'), timeout=5000)
        elif fields['url'] == 'about:blank':
            page.screenshot(path=str(target / 'navigation-still-blank.png'), timeout=5000)
        else:
            print('Screenshot NOT OBSERVED: no isolated sandbox section; full diagnostic page withheld', flush=True)
    except Exception as exc:
        print('Diagnostic DOM/screenshot NOT OBSERVED:', type(exc).__name__, flush=True)


def launch_checked_firefox(pw):
    assert os.getuid() != 0, 'Firefox must run as the existing non-root user'
    # Check presence only; never log arbitrary environment values.
    forbidden = [key for key in os.environ if
                 (key.startswith('MOZ_DISABLE_') and 'SANDBOX' in key) or
                 key in ('MOZ_SANDBOX_DISABLE', 'MOZ_SANDBOX_LEVEL',
                         'PLAYWRIGHT_DOWNLOAD_HOST', 'PLAYWRIGHT_FIREFOX_DOWNLOAD_HOST')]
    assert not forbidden, 'Sandbox/distribution override present'
    executable = Path(pw.firefox.executable_path).resolve(strict=True)
    root = executable.parent
    package = Path(playwright.__file__).parent / 'driver/package'
    catalog = json.loads((package / 'browsers.json').read_text())
    version = next(item for item in catalog['browsers'] if item['name'] == 'firefox')
    print('Playwright Firefox distribution:', json.dumps(version), flush=True)
    print('Firefox executable:', executable, flush=True)
    # Include libraries, configuration and all parents; do not repair permissions.
    paths = {executable, *executable.parents, *root.rglob('*')}
    for path in sorted(paths):
        target = path.resolve(strict=True)
        info = target.stat()
        if path in executable.parents or path == executable:
            print('Firefox path metadata:', str(path), info.st_uid,
                  oct(stat.S_IMODE(info.st_mode)), flush=True)
        assert info.st_uid in (0, os.getuid()), ('Unexpected owner', str(path))
        assert not info.st_mode & (stat.S_IWGRP | stat.S_IWOTH), ('Writable browser path', str(path))
        if path.suffix in ('.js', '.cfg') and path.is_file():
            text = path.read_text(errors='replace')
            assert not re.search(r'["\']security\.sandbox\.content\.level["\']\s*,\s*(?:0|false)\s*\)', text), ('Weakened sandbox preference', str(path))
    print('Firefox executable sha256:', hashlib.sha256(executable.read_bytes()).hexdigest(), flush=True)
    # No custom arguments, environment or firefox_user_prefs; retain defaults.
    browser = pw.firefox.launch()
    try:
        print('Engine: Firefox/Gecko; actual version:', browser.version, flush=True)
        page = browser.new_page()
        # Internal pages need not emit the normal web-page load lifecycle.
        # Wait for navigation commit, then require the actual sandbox table.
        try:
            page.goto('about:support', wait_until='commit')
        except PlaywrightTimeoutError:
            diagnose_timeout(page)
            raise  # Diagnostics never turn a navigation timeout into a pass.
        page.locator('#sandbox-tbody tr').first.wait_for()
        status = page.locator('#sandbox-tbody tr').evaluate_all('''rows =>
            Object.fromEntries(rows.map(row => [
                row.querySelector('th').getAttribute('data-l10n-id'),
                row.querySelector('td').textContent.trim()]))''')
        print('Firefox sandbox section only:', json.dumps(status, sort_keys=True), flush=True)
        assert status.get('has-seccomp-bpf') == 'true', status
        assert status.get('has-seccomp-tsync') == 'true', status
        assert status.get('has-user-namespaces') == 'true', status
        assert status.get('can-sandbox-content') == 'true', status
        configured = int(status['content-sandbox-level'])
        effective = int(status['effective-content-sandbox-level'])
        assert configured > 0 and effective >= configured, status
        page.close()
        return browser
    except BaseException:
        browser.close()
        raise


if __name__ == '__main__':
    with sync_playwright() as pw:
        launch_checked_firefox(pw).close()

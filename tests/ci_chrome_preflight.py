"""Read-only checks for the runner's existing official Chrome and sandbox.

Uses Playwright's supported branded channel, without installing a browser or
modifying OS policy. A failed check stops CI; there is no fallback launch.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from playwright.sync_api import sync_playwright


def main():
    assert os.getuid() != 0, 'Run the browser as the existing non-root runner user'
    assert os.environ.get('CHROME_CHANNEL') == 'chrome'
    chrome = Path('/opt/google/chrome/chrome')
    info = chrome.stat()
    assert info.st_uid == 0 and not info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
    print(subprocess.check_output([str(chrome), '--version'], text=True).strip())
    # Record only public OS sandbox configuration, never the general environment.
    for name in ('/etc/apparmor.d/chrome',
                 '/proc/sys/kernel/apparmor_restrict_unprivileged_userns',
                 '/sys/module/apparmor/parameters/enabled'):
        path = Path(name)
        if path.is_file():
            data = path.read_bytes()
            print(name, 'sha256=' + hashlib.sha256(data).hexdigest())
            if name.startswith(('/proc/', '/sys/')):
                print('value=' + data.decode().strip())
        else:
            print(name, 'NOT OBSERVED')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome', chromium_sandbox=True)
        print('Engine: Google Chrome (Chromium), version:', browser.version)
        page = browser.new_page()
        page.goto('chrome://sandbox')
        # Chromium publishes these renderer-status flags via WebUI strings.js.
        # sandboxGood requires a first-layer sandbox, PID/network namespaces,
        # and seccomp-BPF; see sandbox_internals_ui.cc in Chromium's source.
        status = page.evaluate('''async () => {
            const {loadTimeData} = await import('chrome://resources/js/load_time_data.js');
            return Object.fromEntries(['suid', 'userNs', 'pidNs', 'netNs',
                'seccompBpf', 'seccompTsync', 'sandboxGood'].map(
                    key => [key, loadTimeData.getBoolean(key)]));
        }''')
        print('Chrome renderer sandbox status:', json.dumps(status, sort_keys=True))
        assert status['sandboxGood'], status
        browser.close()


if __name__ == '__main__':
    main()

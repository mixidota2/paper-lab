"""Read-only verification of the published PR4 merge, using protected macOS Chrome."""
import concurrent.futures
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request
import urllib.error

from macos_chrome_cdp import chrome_process
from macos_cdp_review import compatibility
from ci_p0_browser import inspect as inspect_p0
from reference_browser import inspect as inspect_reference

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
BASE = 'https://mixidota2.github.io/paper-lab'
TARGET = '3b7cbce3255ae29257e36241656f53dee1cbe4c2'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src') and value:
                self.links.add(value)


def verify_deployed_files():
    # These files, including this script's dependencies, must be unchanged since merge.
    for directory in ('papers', 'paper_lab'):
        subprocess.run(['git', 'diff', '--exit-code', TARGET, '--', directory], cwd=ROOT, check=True)
    pages = sorted((SITE / 'papers').glob('*.html'))
    assert len(pages) == 100
    paths = {p.relative_to(SITE).as_posix() for p in pages}
    paths.add('index.html')
    external = set()
    missing = []
    # Both URLs already occur in the pre-PR4 baseline 5e4c379 mapping.md/site HTML.
    known_missing = {
        ('papers/diff-projection-feasible-multi-echelon-inventory.html', 'constrained-deep-inventory-fbsde.html'),
        ('papers/diff-projection-feasible-multi-echelon-inventory.html', 'deepstock-policy-regularized-inventory-drl.html'),
    }
    for p in [SITE / 'index.html', *pages]:
        parser = Links()
        parser.feed(p.read_text())
        origin = BASE + '/' + p.relative_to(SITE).as_posix()
        for value in parser.links:
            link = urllib.parse.urlsplit(urllib.parse.urljoin(origin, value))
            if link.scheme not in ('https', 'http'):
                continue
            if link.netloc == 'mixidota2.github.io' and link.path.startswith('/paper-lab/'):
                rel = urllib.parse.unquote(link.path.removeprefix('/paper-lab/')) or 'index.html'
                if rel.endswith('/'):
                    rel += 'index.html'
                if not (SITE / rel).is_file():
                    source = p.relative_to(SITE).as_posix()
                    assert (source, rel) in known_missing, (source, rel)
                    try:
                        with urllib.request.urlopen(BASE + '/' + rel, timeout=30) as response:
                            status = response.status
                    except urllib.error.HTTPError as error:
                        status = error.code
                    missing.append({'source': source, 'path': rel, 'http_status': status,
                                    'status': 'KNOWN BASELINE LINK DEFECT; not accepted as valid'})
                    continue
                paths.add(rel)
            else:
                external.add(urllib.parse.urlunsplit(link))

    def check(rel):
        expected = (SITE / rel).read_bytes()
        req = urllib.request.Request(BASE + '/' + urllib.parse.quote(rel), headers={'User-Agent': 'paper-lab-publication-verification'})
        with urllib.request.urlopen(req, timeout=30) as response:
            actual = response.read()
            assert response.status == 200
            assert response.url.startswith(BASE + '/')
        digest = hashlib.sha256(actual).hexdigest()
        assert actual == expected, f'Deployed content mismatch: {rel}'
        return {'path': rel, 'bytes': len(actual), 'sha256': digest}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        checked = list(pool.map(check, sorted(paths)))
    out = ROOT / 'browser-review'
    out.mkdir(exist_ok=True)
    report = {'target_commit': TARGET, 'base_url': BASE, 'html_pages': 100, 'exact_matches': checked,
              'external_link_targets_present': sorted(external),
              'external_destinations_fetched': False, 'sitewide_link_health': 'PARTIAL',
              'known_baseline_link_defects': missing,
              'limitation': 'VN2 auxiliary controls crop is not acceptance evidence; use viewport tiles.'}
    (out / 'publication.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('OBSERVED known baseline link defects (not passing links):', json.dumps(missing), flush=True)
    print('PASS: live bytes match target build:', len(checked), 'files;100Lab pages;local links/images/downloads/assets', flush=True)


def main():
    verify_deployed_files()
    with chrome_process() as (endpoint, pid):
        os.environ.update(LAB_CDP_URL=endpoint, LAB_CHROME_PID=str(pid), LAB_BROWSER='macos-cdp')
        compatibility()
        inspect_p0(BASE)
        print('PASS: PUBLIC P0 controls/360/1440/noJS360', flush=True)
        inspect_reference(BASE)
        print('PASS: PUBLIC reference inputs/export/import/counterexamples/360/1440', flush=True)


if __name__ == '__main__':
    main()

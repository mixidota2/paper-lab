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

from playwright.sync_api import sync_playwright
from macos_chrome_cdp import chrome_process, connect_checked_cdp, verify_seatbelt
from macos_cdp_review import compatibility

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
BASE = 'https://mixidota2.github.io/paper-lab'
TARGET = '92b23c658f26ea3d92ea431cd1b576967dd177ce'


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
                assert (SITE / rel).is_file(), rel
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
              'external_destinations_fetched': False,
              'limitation': 'VN2 auxiliary controls crop is not acceptance evidence; use viewport tiles.'}
    (out / 'publication.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('PASS: live bytes match target build:', len(checked), 'files;100Lab pages;local links/images/downloads/assets', flush=True)


def main():
    verify_deployed_files()
    with chrome_process() as (endpoint, pid):
        os.environ.update(LAB_CDP_URL=endpoint, LAB_CHROME_PID=str(pid), LAB_BROWSER='macos-cdp')
        compatibility()
        with sync_playwright() as pw:
            browser = connect_checked_cdp(pw)
            try:
                for width in (360, 1440):
                    page = browser.new_page(viewport={'width': width, 'height': 900})
                    for label, slug, title in (
                        ('Constrained FBSDE', 'constrained-deep-inventory-fbsde', 'Constrained Deep Inventory Management'),
                        ('DeepStock', 'deepstock-policy-regularized-inventory-drl', 'DeepStock'),
                    ):
                        response = page.goto(BASE + '/papers/diff-projection-feasible-multi-echelon-inventory.html')
                        assert response.ok
                        verify_seatbelt(browser)
                        link = page.get_by_role('link', name=label, exact=True)
                        assert link.get_attribute('href') == slug + '.html'
                        with page.expect_navigation() as navigation:
                            link.click()
                        assert navigation.value.ok
                        assert page.url == BASE + '/papers/' + slug + '.html'
                        assert title in page.title()
                        assert page.locator('h1').is_visible()
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                        verify_seatbelt(browser)
                        page.screenshot(path=str(ROOT / 'browser-review' / f'{slug}-{width}.png'))
                        print('PASS: PUBLIC corrected link', width, label, page.url, flush=True)
                    page.close()
            finally:
                browser.close()


if __name__ == '__main__':
    main()

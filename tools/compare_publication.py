#!/usr/bin/env python3
"""Compare a pinned local Lab build with its public Pages bytes. Read-only GETs."""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime
import hashlib
from html.parser import HTMLParser
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

BASE = 'https://mixidota2.github.io/paper-lab/'
MAX_FILE_BYTES = 16 * 1024 * 1024
SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('Invalid artifact path')
    parts = value.split('/')
    if any(part in ('', '.', '..') for part in parts) or ':' in parts[0]:
        raise ValueError('Artifact path is not a relative normalized path')
    return value


def validate_source_id(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256 or any(ord(c) < 32 for c in value):
        raise ValueError('A nonempty source identifier is required')
    return value


def site_root(site):
    site = pathlib.Path(site)
    if site.is_symlink() or not site.is_dir():
        raise ValueError('Site must be a real directory, not a symlink')
    return site.resolve()


def make_manifest(site, source_id):
    root = site_root(site)
    validate_source_id(source_id)
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not valid build artifacts')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError('Build contains a non-regular file')
        relative = safe_path(path.relative_to(root).as_posix())
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('Build artifact exceeds size limit')
        raw = path.read_bytes()
        files.append({'path': relative, 'size': len(raw), 'sha256': sha256(raw)})
    if not files or not any(f['path'] == 'index.html' for f in files):
        raise ValueError('Build must include index.html and cannot be empty')
    return {'schema_version': 1, 'source_id': source_id, 'file_count': len(files), 'files': files}


def outside_site(path, root):
    path = pathlib.Path(path)
    if path.is_symlink():
        raise ValueError('Evidence output must not be a symlink')
    path = path.resolve()
    if path == root or root in path.parents:
        raise ValueError('Evidence output must be outside the expected build')
    return path


def write_manifest(site, source_id, output):
    manifest = make_manifest(site, source_id)
    output = outside_site(output, site_root(site))
    raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    with output.open('xb') as stream:
        stream.write(raw)
    return sha256(raw)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_manifest(path, digest):
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        raise ValueError('Expected manifest SHA-256 must be 64 lowercase hex characters')
    raw = pathlib.Path(path).read_bytes()
    if sha256(raw) != digest:
        raise ValueError('Manifest bytes differ from the pinned SHA-256')
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or set(value) != {'schema_version', 'source_id', 'file_count', 'files'}:
        raise ValueError('Invalid manifest shape')
    if type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('Unsupported manifest schema')
    validate_source_id(value['source_id'])
    if type(value['file_count']) is not int or not isinstance(value['files'], list) or value['file_count'] != len(value['files']):
        raise ValueError('Manifest file count differs')
    paths = []
    for item in value['files']:
        if not isinstance(item, dict) or set(item) != {'path', 'size', 'sha256'}:
            raise ValueError('Invalid manifest file')
        paths.append(safe_path(item['path']))
        if type(item['size']) is not int or not 0 <= item['size'] <= MAX_FILE_BYTES:
            raise ValueError('Invalid artifact size')
        if not isinstance(item['sha256'], str) or not SHA256.fullmatch(item['sha256']):
            raise ValueError('Invalid artifact SHA-256')
    if paths != sorted(set(paths)) or 'index.html' not in paths:
        raise ValueError('Manifest paths must be unique, sorted, and include index.html')
    return value


def allowed_url(url):
    if not isinstance(url, str) or any(ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError('Invalid URL')
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname != 'mixidota2.github.io'
            or parsed.port not in (None, 443) or parsed.username is not None
            or parsed.password is not None or parsed.fragment):
        raise ValueError('Request leaves the authorized HTTPS origin')
    decoded = parsed.path
    for _ in range(6):
        if not decoded.startswith('/paper-lab/') or '\\' in decoded or any(part in ('.', '..') for part in decoded.split('/')):
            raise ValueError('Request leaves the authorized project path')
        if any(ord(c) < 32 or ord(c) == 127 for c in decoded):
            raise ValueError('Invalid URL path')
        expanded = urllib.parse.unquote(decoded)
        if expanded == decoded:
            break
        decoded = expanded
    else:
        raise ValueError('Excessive path encoding')
    return url


class ProjectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        allowed_url(request.full_url)
        allowed_url(newurl)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def fetch(url, expected_size, timeout):
    allowed_url(url)
    request = urllib.request.Request(url, headers={
        'User-Agent': 'paper-lab-publication-check/1.0',
        'Accept-Encoding': 'identity', 'Cache-Control': 'no-cache',
    })
    with urllib.request.build_opener(ProjectRedirect).open(request, timeout=timeout) as response:
        allowed_url(response.url)
        if response.status != 200:
            raise ValueError('HTTP status is not 200')
        if response.headers.get('Content-Encoding', 'identity').lower() not in ('', 'identity'):
            raise ValueError('Unexpected content encoding; raw bytes cannot be compared')
        raw = response.read(expected_size + 1)
        return raw, {'http_status': response.status, 'final_url': response.url,
                     'content_type': response.headers.get('Content-Type'),
                     'etag': response.headers.get('ETag'),
                     'last_modified': response.headers.get('Last-Modified')}


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.base_href = False
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            self.ids.add(values['id'])
        if tag == 'a' and 'name' in values:
            self.ids.add(values['name'])
        if tag == 'base' and 'href' in values:
            self.base_href = True
        for key in ('href', 'src'):
            if values.get(key):
                self.links.append(values[key])


def local_links(site, manifest):
    known = {entry['path'] for entry in manifest['files']}
    documents = {}
    issues = []
    references = 0
    external = 0
    for name in sorted(known):
        if name.endswith(('.html', '.htm')):
            parser = Links()
            parser.feed((site / name).read_text(encoding='utf-8'))
            documents[name] = parser
    for name, doc in documents.items():
        if doc.base_href:
            issues.append({'from': name, 'error': 'HTML base element is not supported'})
            continue
        page_url = BASE + urllib.parse.quote(name, safe='/')
        for href in doc.links:
            resolved = urllib.parse.urljoin(page_url, href)
            parsed = urllib.parse.urlsplit(resolved)
            if parsed.scheme not in ('http', 'https') or parsed.hostname != 'mixidota2.github.io' or not parsed.path.startswith('/paper-lab/'):
                external += 1
                continue
            try:
                allowed_url(urllib.parse.urlunsplit(parsed._replace(fragment='')))
            except ValueError as exc:
                issues.append({'from': name, 'href': href, 'error': str(exc)})
                continue
            path = urllib.parse.unquote(parsed.path[len('/paper-lab/'):])
            if not path or path.endswith('/'):
                path += 'index.html'
            references += 1
            if path not in known:
                issues.append({'from': name, 'href': href, 'error': 'Local target is absent from build', 'target': path})
            elif parsed.fragment and path in documents and urllib.parse.unquote(parsed.fragment) not in documents[path].ids:
                issues.append({'from': name, 'href': href, 'error': 'Local fragment is absent', 'target': path})
    return {'html_files': len(documents), 'internal_references': references,
            'external_references_not_fetched': external, 'issues': issues}


def check(site, manifest_path, expected_manifest_sha256, out, *, fetcher=fetch, workers=4, timeout=20):
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('Workers must be between 1 and 8')
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 60:
        raise ValueError('Timeout must be greater than 0 and no more than 60 seconds')
    manifest = load_manifest(manifest_path, expected_manifest_sha256)
    root = site_root(site)
    if make_manifest(root, manifest['source_id']) != manifest:
        raise ValueError('Local build differs from the pinned manifest')
    out = outside_site(out, root)
    if out.exists():
        raise ValueError('Evidence output already exists')
    link_result = local_links(root, manifest)
    out.mkdir(parents=True, exist_ok=False)
    report = {'status': 'running', 'started_at': now(), 'source_id': manifest['source_id'],
              'manifest_sha256': expected_manifest_sha256, 'base_url': BASE,
              'expected_files': len(manifest['files']), 'files': [], 'links': link_result,
              'remote_file_inventory_exhaustive': False, 'published_or_updated': False,
              'scope': 'Exact expected-file bytes and expected-build internal links. Does not prove no extra stale public files, source-commit provenance, or simultaneous CDN state.'}
    def save():
        temporary = out / 'result.json.tmp'
        temporary.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        temporary.replace(out / 'result.json')
    def one(entry):
        url = BASE + urllib.parse.quote(entry['path'], safe='/')
        record = {'path': entry['path'], 'url': url, 'started_at': now(),
                  'expected_sha256': entry['sha256'], 'expected_size': entry['size']}
        try:
            raw, receipt = fetcher(url, entry['size'], timeout)
            if not isinstance(raw, bytes) or not isinstance(receipt, dict):
                raise ValueError('Fetcher returned an invalid response')
            if type(receipt.get('http_status')) is not int or receipt['http_status'] != 200:
                raise ValueError('Successful HTTP receipt missing')
            allowed_url(receipt.get('final_url'))
            if len(raw) > entry['size'] + 1:
                raise ValueError('Fetcher exceeded the bounded response size')
            record.update(receipt=receipt, observed_size=len(raw), observed_sha256=sha256(raw))
            record['status'] = 'match' if len(raw) == entry['size'] and sha256(raw) == entry['sha256'] else 'mismatch'
            destination = out / 'received' / entry['path']
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        except Exception as exc:
            record.update(status='fetch_failed', error=type(exc).__name__ + ': ' + str(exc))
        record['finished_at'] = now()
        return record
    save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(one, entry) for entry in manifest['files']]
        for future in concurrent.futures.as_completed(futures):
            report['files'].append(future.result())
            if len(report['files']) % 20 == 0:
                save()
    report['files'].sort(key=lambda item: item['path'])
    counts = {status: sum(item['status'] == status for item in report['files']) for status in ('match', 'mismatch', 'fetch_failed')}
    report['counts'] = counts
    report['finished_at'] = now()
    try:
        report['expected_build_unchanged'] = make_manifest(root, manifest['source_id']) == manifest
    except (ValueError, OSError) as exc:
        report['expected_build_unchanged'] = False
        report['expected_build_error'] = str(exc)
    report['status'] = 'matched_expected_files_and_links' if (counts['match'] == manifest['file_count'] and not link_result['issues'] and report['expected_build_unchanged']) else 'review_required_or_failed'
    save()
    return 0 if report['status'] == 'matched_expected_files_and_links' else 3


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    make = sub.add_parser('make')
    make.add_argument('--site', required=True, type=pathlib.Path)
    make.add_argument('--source-id', required=True)
    make.add_argument('--out', required=True, type=pathlib.Path)
    compare = sub.add_parser('check')
    for name in ('site', 'manifest', 'out'):
        compare.add_argument('--' + name, required=True, type=pathlib.Path)
    compare.add_argument('--manifest-sha256', required=True)
    compare.add_argument('--workers', type=int, default=4)
    compare.add_argument('--timeout', type=float, default=20)
    args = parser.parse_args(argv)
    try:
        if args.command == 'make':
            print(write_manifest(args.site, args.source_id, args.out))
            return 0
        code = check(args.site, args.manifest, args.manifest_sha256, args.out, workers=args.workers, timeout=args.timeout)
        print(json.dumps({'exit_code': code, 'result': str(args.out / 'result.json')}))
        return code
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

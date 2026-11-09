"""Offline contract and adversarial tests. Run: python -m unittest -v test_publication.

All direct checks use a fake fetcher; socket connection is prohibited as a backstop.
"""
import copy
import hashlib
import io
from email.message import Message
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import unquote, urlsplit
import urllib.request
import urllib.response

from tools import compare_publication as subject

BASE = 'https://mixidota2.github.io/paper-lab/'


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.site = self.root / 'site'
        self.site.mkdir()
        self.files = {
            'index.html': b'<!doctype html><a href="guide/">Guide</a><img src="asset.bin"><a href="#top" id="top">Top</a>',
            'guide/index.html': b'<!doctype html><a href="../index.html#top">Home</a>',
            'asset.bin': bytes(range(256)),
            'search.json': b'{"title":"Lab"}',
        }
        for name, data in self.files.items():
            p = self.site / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        self.manifest = self.root / 'manifest.json'
        self.digest = subject.write_manifest(self.site, 'test-source', self.manifest)
        self.out = self.root / 'report'
        self.calls = []
        self.addCleanup(patch.stopall)
        patch('socket.create_connection', side_effect=AssertionError('Real network forbidden')).start()
        patch.object(socket.socket, 'connect', side_effect=AssertionError('Real network forbidden')).start()

    def fake(self, url, expected_size, timeout):
        self.assertTrue(url.startswith(BASE), url)
        self.calls.append(url)
        name = unquote(urlsplit(url).path[len('/paper-lab/'):])
        return self.files[name], {'http_status': 200, 'final_url': url}

    def check(self, fetcher=None, **kwargs):
        return subject.check(self.site, self.manifest, self.digest, self.out,
                             fetcher=fetcher or self.fake, **kwargs)

    def assert_report(self):
        self.assertTrue(self.out.is_dir())
        reports = list(self.out.rglob('*.json'))
        self.assertTrue(reports, 'A persisted JSON result is required')
        return [json.loads(p.read_text()) for p in reports]

    def rewrite_manifest(self, obj):
        self.manifest.write_text(json.dumps(obj))
        self.digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()

    def test_happy_path_checks_every_file_and_saves_report(self):
        self.assertEqual(self.check(), 0)
        self.assertEqual(len(self.calls), len(self.files))
        self.assert_report()
        self.assertEqual(self.digest, hashlib.sha256(self.manifest.read_bytes()).hexdigest())

    def test_binary_single_byte_change_fails(self):
        self.files['asset.bin'] = self.files['asset.bin'][:-1] + b'X'
        self.assertEqual(self.check(), 3)
        self.assertEqual(len(self.calls), len(self.files))
        self.assert_report()

    def test_truncated_file_fails(self):
        self.files['asset.bin'] = b''
        self.assertEqual(self.check(), 3)
        self.assert_report()

    def test_one_failure_does_not_stop_other_files(self):
        for kind in ('404', 'timeout', 'missing'):
            with self.subTest(kind=kind):
                self.out = self.root / ('report-' + kind)
                self.calls = []
                def fail(url, expected_size, timeout):
                    data, receipt = self.fake(url, expected_size, timeout)
                    if url.endswith('asset.bin'):
                        if kind == '404':
                            raise HTTPError(url, 404, 'Not Found', None, None)
                        if kind == 'timeout':
                            raise TimeoutError('deadline exceeded')
                        raise OSError('missing response')
                    return data, receipt
                self.assertEqual(self.check(fail), 3)
                self.assertEqual(len(self.calls), len(self.files))
                self.assert_report()

    def test_status_and_final_url_are_verified(self):
        for field, value in [('http_status', 404), ('final_url', 'https://evil.example/paper-lab/index.html'),
                             ('final_url', 'http://mixidota2.github.io/paper-lab/index.html')]:
            with self.subTest(field=field, value=value):
                self.out = self.root / ('r' + str(len(list(self.root.iterdir()))))
                def wrong(url, expected_size, timeout):
                    data, receipt = self.fake(url, expected_size, timeout)
                    receipt[field] = value
                    return data, receipt
                self.assertEqual(self.check(wrong), 3)
                self.assert_report()

    def test_manifest_digest_is_pinned_before_fetch(self):
        self.manifest.write_bytes(self.manifest.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            self.check()
        self.assertFalse(self.calls)

    def test_expected_directory_must_match_manifest(self):
        for kind in ('changed', 'missing', 'extra'):
            with self.subTest(kind=kind):
                p = self.site / 'search.json'
                if kind == 'changed':
                    p.write_bytes(b'changed')
                elif kind == 'missing':
                    p.unlink()
                else:
                    p.write_bytes(self.files['search.json'])
                    (self.site / 'extra').write_bytes(b'x')
                with self.assertRaises(ValueError):
                    self.check()
                self.assertFalse(self.calls)
                p.write_bytes(self.files['search.json'])

    def test_empty_site_rejected(self):
        empty = self.root / 'empty'
        empty.mkdir()
        with self.assertRaises(ValueError):
            subject.make_manifest(empty, 'test-source')

    def test_symlink_file_rejected(self):
        (self.site / 'escape').symlink_to(self.manifest)
        with self.assertRaises(ValueError):
            subject.make_manifest(self.site, 'test-source')
        with self.assertRaises(ValueError):
            self.check()

    def test_symlink_directory_rejected(self):
        (self.site / 'escape').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            subject.make_manifest(self.site, 'test-source')

    def test_existing_output_is_not_overwritten(self):
        self.out.mkdir()
        keep = self.out / 'keep'
        keep.write_text('keep')
        with self.assertRaises(ValueError):
            self.check()
        self.assertEqual(keep.read_text(), 'keep')
        self.assertFalse(self.calls)

    def test_dangling_output_symlink_is_rejected(self):
        target = self.root / 'new-target'
        self.out.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.check()
        self.assertFalse(self.calls)
        self.assertFalse(target.exists())

    def test_same_project_redirect_can_match_bytes(self):
        def redirected(url, expected_size, timeout):
            data, receipt = self.fake(url, expected_size, timeout)
            receipt['final_url'] = BASE + 'canonical/' + url.rsplit('/', 1)[-1]
            return data, receipt
        self.assertEqual(self.check(redirected), 0)
        self.assert_report()

    def test_output_inside_site_is_rejected_before_fetch(self):
        self.out = self.site / 'report'
        with self.assertRaises(ValueError):
            self.check()
        self.assertFalse(self.calls)
        self.assertFalse(self.out.exists())

    def test_broken_internal_link_is_not_reported_as_success(self):
        self.files['index.html'] = b'<a href="missing.html">Missing</a>'
        (self.site / 'index.html').write_bytes(self.files['index.html'])
        # A manifest may reject invalid links early; otherwise the check must fail.
        try:
            self.digest = subject.write_manifest(self.site, 'test-source', self.root / 'broken.json')
        except ValueError:
            return
        self.manifest = self.root / 'broken.json'
        self.assertEqual(self.check(), 3)
        self.assert_report()

    def test_duplicate_json_key_rejected_even_with_matching_digest(self):
        raw = self.manifest.read_text()
        obj = json.loads(raw)
        key = next(iter(obj))
        duplicate = '{' + json.dumps(key) + ':' + json.dumps(obj[key]) + ',' + raw.lstrip()[1:]
        self.manifest.write_text(duplicate)
        self.digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            self.check()
        self.assertFalse(self.calls)

    def test_unusual_filenames_are_encoded_once(self):
        for name in ('a b.txt', '日本語.txt', '100%.txt', 'hash#part.txt', 'query?part.txt'):
            self.files[name] = b'content'
            (self.site / name).write_bytes(b'content')
        self.manifest = self.root / 'encoded.json'
        self.digest = subject.write_manifest(self.site, 'test-source', self.manifest)
        self.assertEqual(self.check(), 0)
        self.assertEqual(len(self.calls), len(self.files))
        for url in self.calls:
            parts = urlsplit(url)
            self.assertEqual(parts.query, '')
            self.assertEqual(parts.fragment, '')
            self.assertNotIn(' ', url)
            self.assertTrue(url.isascii())
        self.assertIn(BASE + '100%25.txt', self.calls)
        self.assertIn(BASE + 'hash%23part.txt', self.calls)

    def test_manifest_is_deterministic(self):
        other = self.root / 'second.json'
        digest = subject.write_manifest(self.site, 'test-source', other)
        self.assertEqual(digest, self.digest)
        self.assertEqual(other.read_bytes(), self.manifest.read_bytes())

    def test_missing_receipt_fields_fail_closed(self):
        def missing(url, expected_size, timeout):
            data, receipt = self.fake(url, expected_size, timeout)
            return data, {}
        self.assertEqual(self.check(missing), 3)
        self.assertEqual(len(self.calls), len(self.files))
        self.assert_report()

    def test_manifest_paths_and_entry_types_are_strict(self):
        original = json.loads(self.manifest.read_text())
        bad_paths = ('../escape', '/tmp/escape', 'a/../escape', 'a/./b', 'a//b',
                     'a\\b', '', 'https:evil', 'x\x00y', 'x\ny')
        for path in bad_paths:
            with self.subTest(path=path):
                obj = copy.deepcopy(original)
                obj['files'][0]['path'] = path
                self.rewrite_manifest(obj)
                with self.assertRaises(ValueError):
                    self.check()
                self.assertFalse(self.calls)
        for key, value in [('size', True), ('size', -1), ('size', 1.5),
                           ('sha256', '0' * 63), ('sha256', 'A' * 64)]:
            with self.subTest(key=key, value=value):
                obj = copy.deepcopy(original)
                obj['files'][0][key] = value
                self.rewrite_manifest(obj)
                with self.assertRaises(ValueError):
                    self.check()
                self.assertFalse(self.calls)
        obj = copy.deepcopy(original)
        obj['files'].append(copy.deepcopy(obj['files'][0]))
        obj['file_count'] += 1
        self.rewrite_manifest(obj)
        with self.assertRaises(ValueError):
            self.check()
        self.assertFalse(self.calls)

    def test_invalid_worker_and_timeout_rejected_before_fetch(self):
        for kwargs in ({'workers': 0}, {'workers': True}, {'workers': 9},
                       {'timeout': 0}, {'timeout': -1}, {'timeout': True},
                       {'timeout': float('nan')}, {'timeout': float('inf')}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    self.check(**kwargs)
                self.assertFalse(self.calls)

    def test_link_fragments_and_base_are_checked(self):
        for text in (b'<a href="guide/#absent">Broken fragment</a>',
                     b'<base href="https://evil.example/"><a href="index.html">Wrong base</a>',
                     b'<a href="%2e%2e/secret">Encoded traversal</a>'):
            with self.subTest(text=text):
                n = len(list(self.root.iterdir()))
                self.files['index.html'] = text
                (self.site / 'index.html').write_bytes(text)
                self.manifest = self.root / ('link-' + str(n) + '.json')
                self.out = self.root / ('link-report-' + str(n))
                self.digest = subject.write_manifest(self.site, 'test-source', self.manifest)
                self.assertEqual(self.check(), 3)
                self.assert_report()

    def test_real_fetch_transport_enforces_redirect_boundary(self):
        original_build_opener = urllib.request.build_opener
        targets = [BASE + 'redirected.html', 'https://evil.example/paper-lab/file',
                   'http://mixidota2.github.io/paper-lab/file',
                   'https://mixidota2.github.io/outside/file',
                   'https://mixidota2.github.io/paper-lab/%2e%2e/secret',
                   'https://mixidota2.github.io/paper-lab/%5csecret',
                   'https://user@mixidota2.github.io/paper-lab/file',
                   'https://mixidota2.github.io:444/paper-lab/file']
        for target in targets:
            with self.subTest(target=target):
                requests = []
                class Transport(urllib.request.HTTPSHandler):
                    def https_open(self, request):
                        requests.append(request.full_url)
                        headers = Message()
                        if len(requests) == 1:
                            headers['Location'] = target
                            response = urllib.response.addinfourl(io.BytesIO(b''), headers, request.full_url, 302)
                            response.msg = 'Found'
                        else:
                            response = urllib.response.addinfourl(io.BytesIO(b'ok'), headers, request.full_url, 200)
                            response.msg = 'OK'
                        return response
                def fake_opener(*handlers):
                    return original_build_opener(*handlers, Transport())
                with patch.object(subject.urllib.request, 'build_opener', side_effect=fake_opener):
                    if target == BASE + 'redirected.html':
                        data, receipt = subject.fetch(BASE + 'index.html', 2, 1)
                        self.assertEqual(data, b'ok')
                        self.assertEqual(receipt['final_url'], target)
                        self.assertEqual(requests, [BASE + 'index.html', target])
                    else:
                        with self.assertRaises(ValueError):
                            subject.fetch(BASE + 'index.html', 2, 1)
                        self.assertEqual(requests, [BASE + 'index.html'], 'Unsafe redirect was transmitted')

    def test_cli_invalid_manifest_has_input_exit_code(self):
        # Invalid digest fails before any network work. Socket guard also applies
        # in subprocess via an import/runpy wrapper, not via process inheritance.
        script = ('import socket,runpy; '
                  'socket.socket.connect=lambda *a,**k: (_ for _ in ()).throw(AssertionError("Network forbidden")); '
                  'socket.create_connection=socket.socket.connect; '
                  'runpy.run_path(' + repr(str(Path(subject.__file__))) + ',run_name="__main__")')
        result = subprocess.run([sys.executable, '-c', script, 'check', '--site', str(self.site),
                                 '--manifest', str(self.manifest), '--manifest-sha256', '0' * 64,
                                 '--out', str(self.out), '--workers', '2', '--timeout', '1'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()

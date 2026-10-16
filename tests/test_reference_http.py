"""Test the temporary HTTP server lifecycle without launching a browser."""
import importlib.util
from pathlib import Path
from urllib.request import urlopen
import pytest

spec=importlib.util.spec_from_file_location('reference_browser',Path(__file__).with_name('reference_browser.py'))
browser=importlib.util.module_from_spec(spec);spec.loader.exec_module(browser)

@pytest.mark.parametrize('fail',[False,True])
def test_http_serves_relative_assets_and_stops(tmp_path,fail):
    (tmp_path/'page.html').write_text('<script src="model.js"></script>')
    (tmp_path/'model.js').write_text('/* local asset */')
    try:
        with browser.local_site(tmp_path) as base:
            assert base.startswith('http://127.0.0.1:')
            assert b'model.js' in urlopen(base+'/page.html',timeout=2).read()
            assert urlopen(base+'/model.js',timeout=2).read()==b'/* local asset */'
            if fail: raise ValueError('simulated assertion failure')
    except ValueError:
        assert fail
    with pytest.raises(OSError):urlopen(base+'/page.html',timeout=1)

"""Collect the standalone lab's numerical tests in the normal pytest suite."""
import importlib.util
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / 'papers/trace-verifier-brittleness'
spec = importlib.util.spec_from_file_location('trace_lab_run', LAB / 'run.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
TestTraceNumerics = lab.Checks


def test_generated_artifacts_match_source(tmp_path, monkeypatch):
    monkeypatch.setattr(lab, 'ROOT', tmp_path)
    lab.render()
    for name in ['results.json', 'experiment.md']:
        assert (tmp_path / name).read_bytes() == (LAB / name).read_bytes()

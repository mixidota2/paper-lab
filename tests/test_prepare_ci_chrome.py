"""A rejected distribution must never replace the runner's installed browser."""
from pathlib import Path
from types import SimpleNamespace
import shutil
import subprocess
import pytest
import prepare_ci_chrome as m


@pytest.mark.parametrize("failure_at", ["source", "staged"])
def test_rejected_source_or_staged_copy_never_replaces_existing(tmp_path, monkeypatch, failure_at):
    source = tmp_path / "source.app"
    source.mkdir()
    destination = tmp_path / "installed.app"
    destination.mkdir()
    (destination / "sentinel").write_text("original")
    staging = tmp_path / "staging"
    staging.mkdir()
    calls = []
    def verify(path):
        calls.append(path)
        if (path == source) == (failure_at == "source"):
            raise subprocess.CalledProcessError(1, ["codesign"], stderr="rejected")
        return ["valid"]
    monkeypatch.setattr(m, "verify_bundle", verify)
    def copy(args):
        assert args[:4] == ["/usr/bin/ditto", "--rsrc", "--extattr", "--acl"]
        shutil.copytree(args[4], args[5])
    monkeypatch.setattr(m, "run", copy)
    with pytest.raises(subprocess.CalledProcessError):
        m.install_bundle(source, destination, staging)
    assert (destination / "sentinel").read_text() == "original"
    assert not (staging / "preinstalled.app").exists()
    assert len(calls) == (1 if failure_at == "source" else 2)


def test_strict_signature_failure_stops_before_identity_query(monkeypatch):
    calls = []
    def fail(args):
        calls.append(args)
        raise subprocess.CalledProcessError(1, args, stderr="invalid signature")
    monkeypatch.setattr(m, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        m.verify_bundle(Path("/fixture.app"))
    assert calls == [["/usr/bin/codesign", "--verify", "--deep", "--strict", "--verbose=2", "/fixture.app"]]


@pytest.mark.parametrize("identity", [
    "Identifier=other\nAuthority=Developer ID Application: Google LLC (ABC123)\nTeamIdentifier=ABC123",
    "Identifier=com.google.Chrome\nAuthority=Developer ID Application: Someone Else (ABC123)\nTeamIdentifier=ABC123",
    "Identifier=com.google.Chrome\nAuthority=Developer ID Application: Google LLC (ABC123)\nTeamIdentifier=DIFFERENT",
])
def test_reject_other_publisher_or_mismatched_identity(monkeypatch, identity):
    monkeypatch.setattr(m, "run", lambda args: SimpleNamespace(stderr=identity))
    with pytest.raises(AssertionError):
        m.verify_bundle(Path("/fixture.app"))

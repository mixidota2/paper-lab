"""Install Google's signed DMG in the ephemeral macOS CI runner without stripping attributes.

Distribution: Google Chrome Help 95346; runner-images install-chrome.sh uses
Homebrew's google-chrome cask, which publishes the same dl.google.com DMG URL.
Never launches a browser or changes signature, ACL, ownership or sandbox policy.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import re
import subprocess
import tempfile

URL = "https://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg"
APP = Path("/Applications/Google Chrome.app")
OUT = Path("browser-review/chrome-distribution.json")


def run(args):
    return subprocess.run(args, text=True, capture_output=True, check=True, timeout=180)


def verify_bundle(app):
    run(["/usr/bin/codesign", "--verify", "--deep", "--strict", "--verbose=2", str(app)])
    run(["/usr/bin/codesign", "--verify", "-R=anchor apple generic", str(app)])
    identity = run(["/usr/bin/codesign", "-dv", "--verbose=4", str(app)]).stderr.splitlines()
    assert "Identifier=com.google.Chrome" in identity
    authority = next((re.fullmatch(r"Authority=Developer ID Application: Google LLC \(([A-Z0-9]+)\)", line)
                      for line in identity if line.startswith("Authority=Developer ID Application:")), None)
    assert authority is not None, "Google LLC Developer ID is not confirmed"
    assert "TeamIdentifier=" + authority.group(1) in identity
    return [line for line in identity if line.startswith(("Identifier=", "Authority=", "TeamIdentifier="))]


def install_bundle(source, destination, staging):
    # Verify the untouched read-only source before copying or replacing anything.
    source_identity = verify_bundle(source)
    staged = staging / "Google Chrome.app"
    assert not staged.exists()
    run(["/usr/bin/ditto", "--rsrc", "--extattr", "--acl", str(source), str(staged)])
    staged_identity = verify_bundle(staged)
    assert source_identity == staged_identity
    backup = staging / "preinstalled.app"
    assert not backup.exists() and destination.is_dir() and not destination.is_symlink()
    assert destination.stat().st_uid == os.getuid()
    destination.rename(backup)
    staged.rename(destination)
    installed_identity = verify_bundle(destination)
    assert installed_identity == source_identity
    return {"identity": installed_identity, "preinstalled_preserved": True,
            "executable_sha256": hashlib.sha256((destination / "Contents/MacOS/Google Chrome").read_bytes()).hexdigest()}


def main():
    assert platform.system() == "Darwin" and os.getuid() != 0
    assert os.environ.get("GITHUB_ACTIONS") == "true"
    assert os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    record = {"status": "STARTED", "url": URL, "attribute_policy": "preserve all; no stripping",
              "source": "Google HTTPS DMG; verify strict signature, Apple anchor and Google LLC identity"}
    try:
        with tempfile.TemporaryDirectory(prefix="lab-google-download-") as directory:
            temp = Path(directory)
            dmg = temp / "googlechrome.dmg"
            response = run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--proto", "=https",
                            "--tlsv1.2", "--output", str(dmg), "--write-out", "%{http_code}\n%{url_effective}", URL])
            assert response.stdout.splitlines() == ["200", URL], "Unexpected HTTP status or origin"
            record["dmg_sha256"] = hashlib.sha256(dmg.read_bytes()).hexdigest()
            mount = temp / "mounted"
            mount.mkdir()
            attached = False
            try:
                run(["/usr/bin/hdiutil", "attach", "-readonly", "-nobrowse", "-mountpoint", str(mount), str(dmg)])
                attached = True
                source = mount / "Google Chrome.app"
                info = plistlib.loads((source / "Contents/Info.plist").read_bytes())
                record["version"] = info["CFBundleShortVersionString"]
                # Retain the old bundle unmodified until this ephemeral runner ends.
                staging = Path(tempfile.mkdtemp(prefix="lab-chrome-staging-", dir="/Applications"))
                record.update(install_bundle(source, APP, staging))
            finally:
                if attached:
                    run(["/usr/bin/hdiutil", "detach", str(mount)])
        record["status"] = "INSTALLED; launcher protection checks still required"
    except BaseException as error:
        record["status"] = "FAIL"
        record["failure_type"] = type(error).__name__
        if isinstance(error, subprocess.CalledProcessError):
            # Fixed distribution/signature commands only, no general environment.
            from review_103_evidence import bounded_stderr
            record["returncode"] = error.returncode
            record["stderr"] = bounded_stderr(error.stderr)
        raise
    finally:
        OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2))
        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()

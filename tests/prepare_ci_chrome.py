"""Install Google's signed universal PKG in the ephemeral macOS CI runner without stripping attributes.

Distribution: Google Chrome Enterprise Help 9020580 recommends Universal PKG.
The dl.google.com URL is also documented by Microsoft's Intune Chrome sample.
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

URL = "https://dl.google.com/chrome/mac/universal/stable/gcem/GoogleChrome.pkg"
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


def verify_package(package):
    result = run(["/usr/sbin/pkgutil", "--check-signature", str(package)]).stdout
    from review_103_evidence import bounded_stderr
    print("Installer signature diagnostic:", json.dumps(bounded_stderr(result)), flush=True)
    assert "Status: signed by a certificate trusted by macOS" in result
    leaf = re.search(r"1\. Developer ID Installer: Google LLC \(([A-Z0-9]+)\)", result)
    assert leaf is not None, "Google LLC installer identity is not confirmed"
    return leaf.group(1)


def install_bundle(source, destination, staging):
    # Verify the untouched extracted source before copying or replacing anything.
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
              "source": "Google HTTPS Universal PKG; verify installer signature and extracted bundle signature, Apple anchor and Google LLC identity"}
    try:
        with tempfile.TemporaryDirectory(prefix="lab-google-package-") as directory:
            temp = Path(directory)
            package = temp / "GoogleChrome.pkg"
            response = run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--proto", "=https",
                            "--tlsv1.2", "--output", str(package), "--write-out", "%{http_code}\n%{url_effective}", URL])
            assert response.stdout.splitlines() == ["200", URL], "Unexpected HTTP status or origin"
            record["package_sha256"] = hashlib.sha256(package.read_bytes()).hexdigest()
            record["installer_team"] = verify_package(package)
            expanded = temp / "expanded"
            # Apple's package tool expands signed payloads; it does not run installer scripts.
            run(["/usr/sbin/pkgutil", "--expand-full", str(package), str(expanded)])
            sources = list(expanded.rglob("Google Chrome.app"))
            assert len(sources) == 1 and sources[0].is_dir() and not sources[0].is_symlink()
            source = sources[0]
            info = plistlib.loads((source / "Contents/Info.plist").read_bytes())
            record["version"] = info["CFBundleShortVersionString"]
            identity = verify_bundle(source)
            assert "TeamIdentifier=" + record["installer_team"] in identity
            staging = Path(tempfile.mkdtemp(prefix="lab-chrome-staging-", dir="/Applications"))
            record.update(install_bundle(source, APP, staging))
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

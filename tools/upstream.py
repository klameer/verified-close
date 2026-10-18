"""Upstream provenance: check the imported files against the pinned upstream commit.

Usage:
  python tools/upstream.py check             verify unmodified files still match UPSTREAM.json (no network)
  python tools/upstream.py diff [--ref main]   fetch upstream finance/ (gh CLI) and report what changed
                                               upstream since the pin, file by file. Read-only.

UPSTREAM.json pins the commit and records, for every imported file, whether it is
unmodified (sha256 must equal upstream's) or modified (must carry the Modified file notice).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / "UPSTREAM.json").read_text(encoding="utf-8"))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check() -> int:
    bad = []
    for f in PIN["files"]:
        local = ROOT / f["local"]
        if not local.exists():
            bad.append(f"missing: {f['local']}")
        elif f["status"] == "unmodified" and sha(local.read_bytes()) != f["upstream_sha256"]:
            bad.append(f"changed but recorded unmodified: {f['local']}")
        elif f["status"] == "modified" and "**Modified file**" not in local.read_text(encoding="utf-8"):
            bad.append(f"modified without the notice: {f['local']}")
    for b in bad:
        print("FAIL", b)
    print(f"upstream check: {len(PIN['files']) - len(bad)}/{len(PIN['files'])} files as recorded "
          f"(pin {PIN['repo']}@{PIN['commit'][:12]})")
    return 1 if bad else 0


def diff(ref: str) -> int:
    changed = 0
    for f in PIN["files"]:
        raw = subprocess.run(["gh", "api", f"repos/{PIN['repo']}/contents/{f['upstream']}?ref={ref}",
                              "-H", "Accept: application/vnd.github.raw"],
                             capture_output=True, check=True).stdout
        moved = sha(raw) != f["upstream_sha256"]
        changed += moved
        print(f"{'CHANGED' if moved else 'same   '}  {f['upstream']}  ({f['status']} here)")
    print(f"{changed} upstream file(s) changed since {PIN['commit'][:12]}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit(check() if cmd == "check" else diff(sys.argv[3] if "--ref" in sys.argv else "main"))

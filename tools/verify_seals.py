"""Check a published close against its own close log: every sealed file, re-hashed.

Usage: python tools/verify_seals.py [showcase/may-26]

Reads filed/close-log.jsonl and, for every file a sign-off sealed, finds the
published copy by name and compares its sha256 with the one in the log.
Exit 1 if any file is missing or differs.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(folder: str = "showcase/may-26") -> int:
    base = ROOT / folder
    published = {p.name: p for p in base.rglob("*") if p.is_file()}
    bad = checked = 0
    for line in (base / "filed" / "close-log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        sealed = [{"file": record["result_file"], "sha256": record["result_sha256"]}]
        sealed += record.get("sealed_files", [])
        for item in sealed:
            name = item["file"].rsplit("/", 1)[-1]
            path = published.get(name)
            got = hashlib.sha256(path.read_bytes()).hexdigest() if path else None
            ok = got == item["sha256"]
            bad += not ok
            checked += 1
            print(f"{'OK  ' if ok else 'FAIL'} {record['step']:<9} {item['sha256'][:12]}  {name}"
                  + ("" if path else "  (not published)"))
    print(f"{checked - bad}/{checked} sealed files verified against the close log")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))

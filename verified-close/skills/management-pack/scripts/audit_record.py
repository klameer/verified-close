"""Append one signed record to the close log. Stdlib only.

Called by the sign_step scripts, never by hand. Each record seals what the
reviewer signed: the sha256 of the result file (the figures) and of every
other file signed with it (the filed copy, the commentary). closecfg's
require_seal() re-hashes them before any later step may use the figures,
and the audit binder prints them.

Every scripted skill ships an identical copy of this file.
"""
import datetime
import json
from pathlib import Path

from closecfg import sha256


def _rel(close, path: Path) -> str:
    return Path(path).resolve().relative_to(close.root).as_posix()


def append(close, step: str, result_path: Path, reviewer: str, note: str = "",
           also_sealed: list[Path] = ()) -> dict:
    raw = Path(result_path).read_bytes()
    try:
        summary = {k: v for k, v in json.loads(raw).items()
                   if isinstance(v, (str, int, float)) and k != "matches"}
    except (UnicodeDecodeError, json.JSONDecodeError):
        summary = {"file": Path(result_path).name, "bytes": len(raw)}
    record = {
        "step": step,
        "period": close.period,
        "signed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "reviewer": reviewer,
        "result_file": _rel(close, result_path),
        "result_sha256": sha256(result_path),
        "sealed_files": [{"file": _rel(close, p), "sha256": sha256(p)} for p in also_sealed],
        "summary": summary,
    }
    if note:
        record["note"] = note
    with open(close.log_path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record) + "\n")
    print(f"close log: {step} signed by {reviewer}, sealed sha256 {record['result_sha256'][:12]}"
          + (f" (+{len(also_sealed)} file(s))" if also_sealed else "")
          + (f"; decision: {note}" if note else ""))
    return record

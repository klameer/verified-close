"""Close out the period: verify every seal and filing, then build and file the audit binder.

Usage: close_out.py <close.toml>

Refuses unless all three steps are signed and every sealed file still hashes
to its sign-off value (a signed copy missing from the filing folder or
edited after signing stops here), and refuses a second close-out. Then
binder.py builds the PDF, the close-out is recorded in the close log with
the binder's sha256, and the binder and the log are filed alongside the
signed outputs.
"""
import datetime
import json
import shutil
import sys
from pathlib import Path

from closecfg import Close, run_stage, sha256, stop

HERE = Path(__file__).resolve().parent


def main(toml: str) -> None:
    close = Close(toml)
    if "closeout" in close.records():
        stop(f"{close.period} is already closed out: the binder is in the filing folder.")
    close.require_signed("step1", "step2", "step3")  # seals re-hashed, filings must exist
    print("seals verified: every signed file hashes to its sign-off value")
    binder = close.work("audit") / f"Close Binder - {close.period}.pdf"
    run_stage(HERE / "binder.py", close.log_path, close.work("step1") / "reconciliation.json",
              close.work("step2") / "variance.json", close.period, binder,
              close.entity, close.footer(), label="CLOSE-OUT")
    filed = close.file_into(binder)
    record = {"step": "closeout", "period": close.period,
              "signed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "reviewer": close.records()["step3"]["reviewer"],
              "result_file": filed.relative_to(close.root).as_posix(),
              "result_sha256": sha256(filed)}
    with open(close.log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    shutil.copyfile(close.log_path, close.folder("filing") / "close-log.jsonl")
    close.confirm_filed([binder.name, "close-log.jsonl"])
    print(f"close log: close-out recorded, binder sealed sha256 {record['result_sha256'][:12]}")
    print(f"{close.period} closed out.")


if __name__ == "__main__":
    main(*sys.argv[1:2])

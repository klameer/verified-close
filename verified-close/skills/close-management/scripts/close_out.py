"""Close out the period: verify every seal and filing, then build and file the audit binder.

Usage: close_out.py <close.toml>

Refuses unless all three steps are signed and every sealed file still hashes
to its sign-off value (a signed copy missing from the filing folder or
edited after signing stops here). Then binder.py builds the PDF, and the
binder and the close log are filed alongside the signed outputs.
"""
import shutil
import sys
from pathlib import Path

from closecfg import Close, run_stage

HERE = Path(__file__).resolve().parent


def main(toml: str) -> None:
    close = Close(toml)
    close.require_signed("step1", "step2", "step3")  # seals re-hashed, filings must exist
    print("seals verified: every signed file hashes to its sign-off value")
    binder = close.work("audit") / f"Close Binder - {close.period}.pdf"
    run_stage(HERE / "binder.py", close.log_path, close.work("step1") / "reconciliation.json",
              close.work("step2") / "variance.json", close.period, binder,
              close.entity, close.footer(), label="CLOSE-OUT")
    close.file_into(binder)
    shutil.copyfile(close.log_path, close.folder("filing") / "close-log.jsonl")
    close.confirm_filed([binder.name, "close-log.jsonl"])
    print(f"{close.period} closed out.")


if __name__ == "__main__":
    main(*sys.argv[1:2])

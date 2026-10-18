"""Sign step 3 after the reviewer has read the DRAFT pack: re-check, sign, seal, file.

Usage: sign_step3.py <close.toml> <initials> ["<decision note>"]

Re-runs the pack checks, writes the signed copy (the title slide's DRAFT
status line becomes "SIGNED <initials> <date>"), seals the filed copy and
the commentary in the close log, and confirms both filings landed.
"""
import sys
from pathlib import Path

import audit_record
from closecfg import Close, run_stage, stop

HERE = Path(__file__).resolve().parent


def main(toml: str, initials: str, note: str = "") -> None:
    close = Close(toml)
    close.require_signed("step1", "step2")
    close.require_unsigned("step3")
    w = close.work("step3")
    pack = w / f"Management Pack - {close.period}.pptx"
    if not pack.exists():
        stop("step 3 has not been run for this period: nothing to sign")
    rec = close.work("step1") / "reconciliation.json"
    var = close.work("step2") / "variance.json"
    run_stage(HERE / "checks.py", pack, rec, var, w / "commentary.txt",
              label="SIGN-OFF (checks re-run on the files as they stand)")

    signed = f"Management Pack - {close.period} SIGNED {initials}.pptx"
    run_stage(HERE / "sign_pack.py", pack, initials, w / signed, label="SIGN-OFF")
    filed = close.file_into(w / signed)
    audit_record.append(close, "step3", filed, initials, note,
                        also_sealed=[w / "commentary.txt"])
    close.confirm_filed([f"Management Pack - {close.period} DRAFT.pptx", signed])


if __name__ == "__main__":
    main(*sys.argv[1:4])

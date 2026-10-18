"""Sign step 2 after the reviewer has read the DRAFT: re-check, stamp, seal, file.

Usage: sign_step2.py <close.toml> <initials> ["<decision note>"]

Re-runs the checks on the files as they stand now, writes the signed copy
(the reviewer and date replace nothing but the blank status row), seals the
figures, the signed copy and the commentary in the close log, and confirms
both filings landed.
"""
import datetime
import shutil
import sys
from pathlib import Path

import openpyxl

import audit_record
from closecfg import Close, run_stage, stop

HERE = Path(__file__).resolve().parent


def main(toml: str, initials: str, note: str = "") -> None:
    close = Close(toml)
    close.require_signed("step1")
    close.require_unsigned("step2")
    w = close.work("step2")
    report = w / f"Variance Report - {close.period}.xlsx"
    commentary = w / "commentary.md"
    if not (w / "variance.json").exists() or not commentary.exists():
        stop("step 2 has not been run with its commentary: nothing to sign")
    run_stage(HERE / "checks.py", w / "tb.json", w / close.file("budget"), close.period, w,
              label="SIGN-OFF (checks re-run on the files as they stand)")

    signed = f"Variance Report - {close.period} SIGNED {initials}.xlsx"
    shutil.copyfile(report, w / signed)
    wb = openpyxl.load_workbook(w / signed)
    wb["Variance"]["A3"] = (f"SIGNED {initials} {datetime.date.today().isoformat()} - "
                            "sealed in the close log")
    wb.save(w / signed)
    filed = close.file_into(w / signed)
    audit_record.append(close, "step2", w / "variance.json", initials, note,
                        also_sealed=[filed, commentary])
    close.confirm_filed([f"Variance Report - {close.period} DRAFT.xlsx", signed])


if __name__ == "__main__":
    main(*sys.argv[1:4])

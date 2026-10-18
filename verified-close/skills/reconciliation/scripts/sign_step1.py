"""Sign step 1 after the reviewer has read the DRAFT: re-check, seal, file.

Usage: sign_step1.py <close.toml> <initials> "<reviewer name>" ["<decision note>"]
  e.g. sign_step1.py close.toml KL "K. Lameer" "cheque 004182: stop and reissue"

Re-runs the checks on the files as they stand now (anything edited since
the run fails here), refuses to sign while a stale item has no recorded
decision, writes the reviewer-named copy (nothing signed ever carries a
name a DRAFT could carry), appends the sealed record to the close log and
confirms both filings landed.
"""
import json
import sys
from pathlib import Path

import audit_record
from closecfg import Close, run_stage, stop

HERE = Path(__file__).resolve().parent


def main(toml: str, initials: str, reviewer: str, note: str = "") -> None:
    close = Close(toml)
    close.require_unsigned("step1")
    w = close.work("step1")
    rec_path = w / "reconciliation.json"
    if not rec_path.exists():
        stop("step 1 has not been run for this period: nothing to sign")
    run_stage(HERE / "checks.py", w / "statement.json", w / "cashbook.json",
              w / "opening_rec.json", rec_path, label="SIGN-OFF (checks re-run on the files as they stand)")

    rec = json.load(open(rec_path, encoding="utf-8"))
    stale = [i for i in rec["closing_items"] if i["stale"]]
    if stale and not note.strip():
        stop("NOT SIGNED: decision required. Record the reviewer's decision on each stale item "
             "in the note: " + "; ".join(i["description"] for i in stale))

    base = f"Bank Reconciliation - {close.bank['account']} - {close.period}"
    signed = f"{base} SIGNED {initials}.xlsx"
    run_stage(HERE / "write_rec.py", rec_path, close.period_label, reviewer, w / signed,
              close.entity, close.bank["account"], close.bank["line"], close.footer(),
              label="SIGN-OFF")
    filed = close.file_into(w / signed)
    audit_record.append(close, "step1", rec_path, initials, note, also_sealed=[filed])
    close.confirm_filed([f"{base} DRAFT.xlsx", signed])


if __name__ == "__main__":
    main(*sys.argv[1:5])

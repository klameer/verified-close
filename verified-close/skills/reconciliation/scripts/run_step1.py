"""Step 1 of the close in one call: gather, reconcile, check, file the DRAFT.

Usage: run_step1.py <close.toml>

parse_rec -> reconcile -> checks -> write_rec (DRAFT) -> filed for review.
Each stage is its own script, run as a separate process and echoed verbatim,
so any stage can be rerun by hand. Any failure stops here with exit 1: never
present results past a failed check. Refuses to run once step 1 is signed.
"""
import json
import shutil
import sys
from pathlib import Path

from closecfg import Close, run_stage, stop

HERE = Path(__file__).resolve().parent


def run(script: str, *args) -> None:
    run_stage(HERE / script, *args, label="STEP 1")


def prior_rec(close: Close) -> Path:
    """Last month's rec: the reviewer-signed copy if there is one, else the plain one."""
    folder = close.folder("prior_filing")
    stem = f"Bank Reconciliation - {close.bank['account']} - {close.prior}"
    found = sorted(p for p in folder.glob(f"{stem}*.xlsx") if "DRAFT" not in p.name)
    signed = [p for p in found if "SIGNED" in p.name]
    if not (signed or found):
        stop(f"no prior reconciliation '{stem}*.xlsx' in {folder}")
    return (signed or found)[-1]


def summary(close: Close, rec: dict) -> None:
    rs = rec["reconciliation_statement"]
    agrees = abs(rs["derived_book_balance_gbp"] - rs["cashbook_closing_balance_gbp"]) < 0.01
    print(f"\nRECONCILIATION STATEMENT ({close.currency}, as at {close.period_label})")
    print(f"  Balance per bank statement   {rs['balance_per_bank_gbp']:>16,.2f}")
    print(f"  Less unpresented payments    {-rs['less_unpresented_payments_gbp']:>16,.2f}")
    print(f"  Add uncleared lodgements     {rs['add_uncleared_lodgements_gbp']:>16,.2f}")
    print(f"  Balance per cashbook         {rs['cashbook_closing_balance_gbp']:>16,.2f}"
          f"   {'AGREES to the penny' if agrees else 'DOES NOT AGREE'}")
    stale = [i for i in rec["closing_items"] if i["stale"]]
    if stale:
        print("\nDECISIONS FOR THE REVIEWER (the close cannot be signed without them)")
        for i in stale:
            print(f"  [STALE] {i['description']}  {i['amount_gbp']:,.2f}  - {i['reviewer_question']}")


def main(toml: str) -> None:
    close = Close(toml)
    close.require_unsigned("step1")
    w = close.work("step1")
    exports = close.folder("exports")
    shutil.copyfile(exports / close.file("statement"), w / "statement.json")
    shutil.copyfile(exports / close.file("cashbook"), w / "cashbook.json")
    prior = prior_rec(close)
    print(f"inputs: {close.file('statement')}, {close.file('cashbook')}, prior rec {prior.name}")

    run("parse_rec.py", prior, w / "opening_rec.json", close.period_end.isoformat())
    run("reconcile.py", w / "statement.json", w / "cashbook.json", w / "opening_rec.json",
        w / "reconciliation.json", close.period_end.isoformat(), close.bank["stale_days"])
    run("checks.py", w / "statement.json", w / "cashbook.json", w / "opening_rec.json",
        w / "reconciliation.json")
    draft = f"Bank Reconciliation - {close.bank['account']} - {close.period} DRAFT.xlsx"
    run("write_rec.py", w / "reconciliation.json", close.period_label, "DRAFT - pending sign-off",
        w / draft, close.entity, close.bank["account"], close.bank["line"], close.footer())
    close.file_into(w / draft)
    close.confirm_filed([draft])
    summary(close, json.load(open(w / "reconciliation.json", encoding="utf-8")))


if __name__ == "__main__":
    main(*sys.argv[1:2])

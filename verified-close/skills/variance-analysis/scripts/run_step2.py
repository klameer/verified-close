"""Step 2 of the close: variance report vs budget, computed, checked, filed as DRAFT.

Usage: run_step2.py <close.toml>

Gate: refuses to run until step 1 is signed and its seal still holds.
First call: computes and re-derives every variance (variance -> checks) and
prints the table. The commentary for the flagged lines is then written to
<work>/step2/commentary.md. Second call: rebuilds the report with that
commentary as its own sheet, re-checks, and files the DRAFT for review.
"""
import json
import shutil
import sys
from pathlib import Path

from closecfg import Close, run_stage

HERE = Path(__file__).resolve().parent


def table(close: Close, var: dict) -> None:
    print(f"\nVARIANCE VS BUDGET ({close.variance['units']}, MTD {close.period})   "
          f"flag at ±{var['flag_threshold_k']:,.0f}")
    print(f"  {'Line':<38}{'Actual':>9}{'Budget':>9}{'Var':>9}{'Var %':>8}")
    for l in var["lines"]:
        pct = "" if l["variance_pct"] is None else f"{l['variance_pct']:+.1f}%"
        print(f"  {l['line']:<38}{l['mtd_actual_k']:>9,.0f}{l['mtd_budget_k']:>9,.0f}"
              f"{l['variance_k']:>+9,.1f}{pct:>8}{'  FLAG' if l['flagged'] else ''}")
    print(f"  {'TOTAL':<38}{var['total_actual_k']:>9,.0f}{var['total_budget_k']:>9,.0f}"
          f"{var['total_variance_k']:>+9,.1f}")


def main(toml: str) -> None:
    close = Close(toml)
    close.require_signed("step1")
    close.require_unsigned("step2")
    w = close.work("step2")
    shutil.copyfile(close.folder("exports") / close.file("trial_balance"), w / "tb.json")
    budget = w / close.file("budget")
    shutil.copyfile(close.folder("templates") / close.file("budget"), budget)
    commentary = w / "commentary.md"

    args = [w / "tb.json", budget, close.period, close.variance["materiality_k"], w,
            close.entity, close.footer()]
    run_stage(HERE / "variance.py", *args, *([commentary] if commentary.exists() else []),
              label="STEP 2")
    run_stage(HERE / "checks.py", w / "tb.json", budget, close.period, w, label="STEP 2")
    var = json.load(open(w / "variance.json", encoding="utf-8"))
    table(close, var)

    if not commentary.exists():
        rel = commentary.relative_to(close.root).as_posix()
        print(f"\nNEXT: write the commentary for the {var['flagged_count']} flagged line(s) to "
              f"{rel}, then run this again to file the DRAFT.")
        return
    draft = close.draft_name("step2")
    shutil.copyfile(w / f"Variance Report - {close.period}.xlsx", w / draft)
    close.file_into(w / draft)
    close.confirm_filed([draft])
    print("DRAFT filed with the commentary sheet: ready for the reviewer.")


if __name__ == "__main__":
    main(*sys.argv[1:2])

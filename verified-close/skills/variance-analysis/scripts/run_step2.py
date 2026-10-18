"""Step 2 of the close: variance report vs budget as a P&L, computed, checked, filed as DRAFT.

Usage: run_step2.py <close.toml>

Gate: refuses to run until step 1 is signed and its seal still holds.
First call: writes the P&L grouping from close.toml [pnl], computes and
re-derives every variance and subtotal (variance -> checks) and prints the
table. The commentary for the flagged lines is then written to
<work>/step2/commentary.md. Second call: rebuilds the report with that
commentary as its own sheet, re-checks, and files the DRAFT for review.
"""
import json
import shutil
import sys
from pathlib import Path

from closecfg import Close, run_stage, stop

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from variance import GROUPS, layout  # noqa: E402  (the report's own row order)


def write_pnl(close: Close, path: Path) -> None:
    pnl = close.cfg.get("pnl")
    if not pnl or set(pnl) != set(GROUPS):
        stop(f"close.toml needs a [pnl] block with exactly these groups: {', '.join(GROUPS)}")
    path.write_text(json.dumps({g: pnl[g] for g in GROUPS}, indent=1), encoding="utf-8",
                    newline="\n")


def table(close: Close, var: dict) -> None:
    print(f"\nP&L VS BUDGET ({close.variance['units']}, MTD {close.period})   "
          f"variance = actual - budget; F/A = effect on profit; flag at ±{var['flag_threshold_k']:,.0f}")
    print(f"  {'Line':<38}{'Actual':>9}{'Budget':>9}{'Var':>9}{'Var %':>8}  F/A")
    subs = {s["name"]: s for s in var["subtotals"]}
    for kind, r in layout(var["lines"], subs):
        if kind == "line":
            pct = "" if r["variance_pct"] is None else f"{r['variance_pct']:+.1f}%"
            print(f"  {r['line']:<38}{r['mtd_actual_k']:>9,.0f}{r['mtd_budget_k']:>9,.0f}"
                  f"{r['variance_k']:>+9,.1f}{pct:>8}  {r['effect']:<3}"
                  f"{'  FLAG' if r['flagged'] else ''}")
        else:
            print(f"  {r['name'].upper():<38}{r['mtd_actual_k']:>9,.0f}{r['mtd_budget_k']:>9,.0f}"
                  f"{r['variance_k']:>+9,.1f}{'':>8}  {r['effect']}")


def main(toml: str) -> None:
    close = Close(toml)
    close.require_signed("step1")
    close.require_unsigned("step2")
    w = close.work("step2")
    shutil.copyfile(close.folder("exports") / close.file("trial_balance"), w / "tb.json")
    budget = w / close.file("budget")
    shutil.copyfile(close.folder("templates") / close.file("budget"), budget)
    write_pnl(close, w / "pnl.json")
    commentary = w / "commentary.md"

    args = [w / "tb.json", budget, close.period, close.variance["materiality_k"], w,
            close.entity, close.footer(), w / "pnl.json"]
    run_stage(HERE / "variance.py", *args, *([commentary] if commentary.exists() else []),
              label="STEP 2")
    run_stage(HERE / "checks.py", w / "tb.json", budget, close.period, w, w / "pnl.json",
              label="STEP 2")
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

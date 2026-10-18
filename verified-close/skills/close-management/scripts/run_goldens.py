"""Rerun the golden set: known answers, recomputed fresh from the raw inputs.

Usage: run_goldens.py <close.toml>

Reads the golden set named in close.toml ([files] goldens), re-executes the
reconciliation and the variance report into <work>/golden/ (independent of
any run in progress, nothing filed), and asserts each known answer. Values,
not flags: tuning materiality never breaks a golden, broken arithmetic
does. Exit 1 on any red. Rerun after ANY change to the skills.
"""
import json
import shutil
import sys
import tomllib
from pathlib import Path

from closecfg import Close, run_stage

SKILLS = Path(__file__).resolve().parents[2]
REC = SKILLS / "reconciliation" / "scripts"
VAR = SKILLS / "variance-analysis" / "scripts"


def measures(rec: dict, var: dict, cashbook: dict) -> dict:
    rs = rec["reconciliation_statement"]
    book = round(cashbook["opening_balance_gbp"]
                 + sum(e["money_in_gbp"] - e["money_out_gbp"] for e in cashbook["rows"]), 2)
    out = {
        "statement_close": rs["balance_per_bank_gbp"],
        "cashbook_close": book if book == cashbook["closing_balance_gbp"] else None,
        "rec_difference": round(rs["derived_book_balance_gbp"] - rs["cashbook_closing_balance_gbp"], 2),
        "closing_items": len(rec["closing_items"]),
        "stale_count": rec["stale_item_count"],
    }
    out |= {f"variance:{l['line']}": l["variance_k"] for l in var["lines"]}
    out |= {f"subtotal:{t['name']}": t["variance_k"] for t in var["subtotals"]}
    out |= {f"actual:{t['name']}": t["mtd_actual_k"] for t in var["subtotals"]}
    return out


def stale_item(rec: dict, want: dict) -> tuple[bool, str]:
    hits = [i for i in rec["closing_items"] if i["stale"] and want["match"] in i["description"]]
    ok = len(hits) == 1 and hits[0]["amount_gbp"] == want["amount"]
    return ok, (f"{hits[0]['description']} {hits[0]['amount_gbp']:,.2f}" if hits else "not found")


def main(toml: str) -> None:
    close = Close(toml)
    goldens = tomllib.loads((close.root / close.file("goldens")).read_text(encoding="utf-8"))
    g = close.work("golden")
    exports = close.folder("exports")
    for key, name in [("statement", "statement.json"), ("cashbook", "cashbook.json"),
                      ("trial_balance", "tb.json")]:
        shutil.copyfile(exports / close.file(key), g / name)
    budget = g / close.file("budget")
    shutil.copyfile(close.folder("templates") / close.file("budget"), budget)
    prior = sorted(p for p in close.folder("prior_filing").glob(
        f"Bank Reconciliation - {close.bank['account']} - {close.prior}*.xlsx") if "DRAFT" not in p.name)

    end = close.period_end.isoformat()
    run_stage(REC / "parse_rec.py", prior[-1], g / "opening_rec.json", end, label="GOLDENS")
    run_stage(REC / "reconcile.py", g / "statement.json", g / "cashbook.json", g / "opening_rec.json",
              g / "reconciliation.json", end, close.bank["stale_days"], label="GOLDENS")
    pnl = close.cfg["pnl"]
    (g / "pnl.json").write_text(json.dumps(pnl), encoding="utf-8")
    run_stage(VAR / "variance.py", g / "tb.json", budget, close.period,
              close.variance["materiality_k"], g, close.entity, close.footer(), g / "pnl.json",
              label="GOLDENS")

    rec = json.load(open(g / "reconciliation.json", encoding="utf-8"))
    var = json.load(open(g / "variance.json", encoding="utf-8"))
    got = measures(rec, var, json.load(open(g / "cashbook.json", encoding="utf-8")))
    red = 0
    print(f"\nGOLDEN SET - {close.entity} - {close.period}")
    for check in goldens["check"]:
        if check["metric"] == "stale_item":
            ok, detail = stale_item(rec, check["expect"])
        else:
            value = got.get(check["metric"])
            ok, detail = value == check["expect"], f"{value}"
        red += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {check['id']:<4} {check['name']}  ({detail})")
    print(f"golden set: {len(goldens['check']) - red}/{len(goldens['check'])} green")
    if red:
        sys.exit(1)


if __name__ == "__main__":
    main(*sys.argv[1:2])

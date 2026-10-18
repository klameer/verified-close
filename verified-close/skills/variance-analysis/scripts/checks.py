"""Independent tie-outs for the variance report. Exit 1 on any failure.

Usage: checks.py tb.json budget.xlsx <period> outdir/ pnl.json

Recomputes every figure from the RAW inputs (trial balance, budget workbook,
P&L grouping) and compares against both outputs, variance.json and the xlsx,
cell by cell:
  C1 every TB line sits in exactly one P&L group and appears once in both outputs
  C2 each line variance re-derives (actual - budget) and its F/A matches its group
  C3 each P&L subtotal re-derives from the raw inputs, in the json and the xlsx
  C4 flags consistent with the stated threshold
Only read_budget is shared with variance.py (the same parser); every sum here
is recomputed independently. Requires openpyxl.
"""
import json
import sys
from pathlib import Path

import openpyxl

COST_GROUPS = {"cost_of_sales", "operating_expenses", "below_ebitda"}


def fa(var: float, income: bool) -> str:
    return "" if var == 0 else ("F" if (var > 0) == income else "A")


def main(tb_path: str, budget_path: str, period: str, outdir: str, pnl_path: str) -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    from variance import read_budget  # same parser, independent recompute

    tb = json.load(open(tb_path, encoding="utf-8"))
    budgets = read_budget(budget_path, period)
    pnl = json.load(open(pnl_path, encoding="utf-8"))
    rec = json.load(open(Path(outdir) / "variance.json", encoding="utf-8"))
    failures = []

    placed = [line for group in pnl.values() for line in group]
    if sorted(placed) != sorted(tb["lines"]) or len(placed) != len(set(placed)):
        failures.append("C1 every TB line must sit in exactly one P&L group")
    group_of = {line: g for g, lines in pnl.items() for line in lines}

    json_lines = {l["line"]: l for l in rec["lines"]}
    if set(json_lines) != set(tb["lines"]):
        failures.append("C1 line sets differ between TB and variance.json")

    sums = {g: [0.0, 0.0] for g in pnl}
    for line, vals in tb["lines"].items():
        actual, budget = float(vals["mtd_actual"]), budgets[line]
        group = group_of.get(line)
        if group:
            sums[group][0] += actual
            sums[group][1] += budget
        want = round(actual - budget, 1)
        got = json_lines.get(line, {})
        if got.get("variance_k") != want:
            failures.append(f"C2 {line}: variance {got.get('variance_k')} != recomputed {want}")
        if got.get("effect") != fa(want, income=group not in COST_GROUPS):
            failures.append(f"C2 {line}: F/A {got.get('effect')!r} wrong for a {group} line")
        if got.get("flagged") != (abs(want) >= rec["flag_threshold_k"]):
            failures.append(f"C4 {line}: flag inconsistent with threshold")

    expected = {}
    for i, label in ((0, "actual"), (1, "budget")):
        rev, cos = sums["revenue"][i], sums["cost_of_sales"][i]
        opex, below = sums["operating_expenses"][i], sums["below_ebitda"][i]
        for name, value in (("Total revenue", rev), ("Gross margin", rev - cos),
                            ("Total operating expenses", opex),
                            ("EBITDA", rev - cos - opex), ("Net result", rev - cos - opex - below)):
            expected.setdefault(name, {})[label] = round(value, 1)
    json_subs = {s["name"]: s for s in rec.get("subtotals", [])}
    for name, want in expected.items():
        got = json_subs.get(name)
        var = round(want["actual"] - want["budget"], 1)
        if not got or (got["mtd_actual_k"], got["mtd_budget_k"], got["variance_k"]) != \
                (want["actual"], want["budget"], var):
            failures.append(f"C3 {name}: json subtotal does not re-derive")
        elif got["effect"] != fa(var, income=name != "Total operating expenses"):
            failures.append(f"C3 {name}: F/A wrong")

    ws = openpyxl.load_workbook(Path(outdir) / f"Variance Report - {period}.xlsx")["Variance"]
    seen_lines, seen_subs = 0, 0
    for row in ws.iter_rows(min_row=5, values_only=True):
        name = row[0]
        if name in json_lines:
            seen_lines += 1
            j = json_lines[name]
            if (row[1], row[2], row[3], row[5] or "") != (j["mtd_actual_k"], j["mtd_budget_k"],
                                                         j["variance_k"], j["effect"]):
                failures.append(f"C2 xlsx row for {name} differs from variance.json")
        elif name in expected:
            seen_subs += 1
            want = expected[name]
            if (row[1], row[2], round(row[3], 1)) != (want["actual"], want["budget"],
                                                      round(want["actual"] - want["budget"], 1)):
                failures.append(f"C3 xlsx {name} differs from the recomputed subtotal")
    if seen_lines != len(json_lines):
        failures.append(f"C1 xlsx shows {seen_lines} lines, expected {len(json_lines)}")
    if seen_subs != len(expected):
        failures.append(f"C3 xlsx shows {seen_subs} subtotals, expected {len(expected)}")

    if failures:
        print("CHECKS FAILED:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print(f"checks passed: C1 every line placed once, C2 every variance and F/A re-derived, "
          f"C3 {len(expected)} P&L subtotals re-derived, C4 flags at ±{rec['flag_threshold_k']:,.0f}k")


if __name__ == "__main__":
    main(*sys.argv[1:6])

"""Tie-outs for the built pack. Hard-fails on figure mismatches; lists any
commentary number it cannot trace to the signed sources for the reviewer.

Usage: checks.py out.pptx step1/reconciliation.json step2/variance.json commentary.txt

  C1 the four cash figures in the pack == reconciliation.json, to the penny
  C2 every variance row in the pack == variance.json (actual, budget, var)
  C3 every P&L subtotal row (revenue, gross margin, opex, EBITDA, net result) verbatim
  W1 commentary numbers not present in the signed sources are LISTED for
     the reviewer to verify against the cited document (does not fail:
     the reviewer verifies, the pack records)
Requires python-pptx.
"""
import json
import re
import sys

from pptx import Presentation


def _all_text(prs):
    chunks = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                chunks.append(shape.text_frame.text)
            if getattr(shape, "has_table", False) and shape.has_table:
                for row in shape.table.rows:
                    chunks.append("|".join(c.text for c in row.cells))
    return "\n".join(chunks)


def main(pptx_path, rec_path, var_path, commentary_path):
    rec = json.load(open(rec_path, encoding="utf-8"))
    var = json.load(open(var_path, encoding="utf-8"))
    text = _all_text(Presentation(pptx_path))
    failures = []

    rs = rec["reconciliation_statement"]
    for label, value in [("bank", rs["balance_per_bank_gbp"]),
                         ("unpresented", -rs["less_unpresented_payments_gbp"]),
                         ("uncleared", rs["add_uncleared_lodgements_gbp"]),
                         ("book", rs["cashbook_closing_balance_gbp"])]:
        if f"£{value:,.2f}" not in text:
            failures.append(f"C1 cash figure missing/mismatched: {label} £{value:,.2f}")

    for l in var["lines"]:
        row = f"{l['line']}|{l['mtd_actual_k']:,.0f}|{l['mtd_budget_k']:,.0f}|{l['variance_k']:+,.1f}"
        if row not in text:
            failures.append(f"C2 variance row not found verbatim: {l['line']}")
    for t in var["subtotals"]:
        row = f"{t['name']}|{t['mtd_actual_k']:,.0f}|{t['mtd_budget_k']:,.0f}|{t['variance_k']:+,.1f}"
        if row not in text:
            failures.append(f"C3 subtotal row not found verbatim: {t['name']}")

    known = set()
    for l in var["lines"] + var["subtotals"]:
        known |= {f"{abs(l['mtd_actual_k']):,.0f}", f"{abs(l['mtd_budget_k']):,.0f}",
                  f"{abs(l['variance_k']):,.0f}", f"{abs(l['variance_k']):,.1f}"}
        if l.get("variance_pct") is not None:
            known.add(f"{abs(l['variance_pct']):,.1f}")
    for v in [rs["balance_per_bank_gbp"], rs["less_unpresented_payments_gbp"],
              rs["add_uncleared_lodgements_gbp"], rs["cashbook_closing_balance_gbp"]] + \
             [abs(i["amount_gbp"]) for i in rec["closing_items"]]:
        known |= {f"{v:,.2f}", f"{v:,.0f}", f"{v / 1000:,.0f}", f"{v / 1000:,.1f}"}
    known.add(f"{var['flag_threshold_k']:,.0f}")

    unsourced = []
    commentary = open(commentary_path, encoding="utf-8").read()
    for num in re.findall(r"£?([\d,]+(?:\.\d+)?)(?:k|m)?", commentary):
        clean = num.strip(",")
        if not clean or float(clean.replace(",", "")) < 32:
            continue
        if clean not in known and not re.fullmatch(r"20\d\d", clean):  # years are not figures
            unsourced.append(num)

    if failures:
        print("CHECKS FAILED:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("checks passed: C1 cash figures to the penny, C2 every variance row "
          "verbatim, C3 every P&L subtotal verbatim")
    if unsourced:
        print("REVIEWER MUST VERIFY - commentary numbers not in the signed "
              "sources (check them against the cited documents):")
        for n in sorted(set(unsourced)):
            print(f" - {n}")


if __name__ == "__main__":
    main(*sys.argv[1:5])

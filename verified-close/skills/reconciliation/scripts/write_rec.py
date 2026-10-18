"""Write the bank reconciliation as a filing-ready workbook (DRAFT or signed).

Usage: write_rec.py reconciliation.json <period_label> <reviewer> out.xlsx \
                    "<entity>" "<account>" "<bank_line>" "<footer>"
  e.g. write_rec.py step1/reconciliation.json "31 May 2026" "K. Lameer" \
       "Bank Reconciliation - Operating Account - May-26 SIGNED KL.xlsx" \
       "Caldergate Distribution Group Ltd" "Operating Account" \
       "Pennine Commercial Bank plc, 99-42-07 / 00341275" "<footer text>"

Same layout as the prior-month rec, so next month's parse_rec.py reads this
file back as its opening position — the close feeds itself. Item labels
carry their book date "(28 May)" so ageing keeps working. Requires openpyxl.
"""
import json
import re
import sys
from datetime import date

import openpyxl
from openpyxl.styles import Font


def _label(item: dict) -> str:
    # A trailing "(14 Apr)" is what parse_rec.py ages items by next month —
    # append one unless the description already ends with a date paren.
    desc = item["description"]
    if not re.search(r"\(\d{1,2} \w{3}[^)]*\)\s*$", desc) and item.get("book_date"):
        d = date.fromisoformat(item["book_date"])
        desc = f"{desc} ({d.day} {d.strftime('%b')})"
    return f"  {desc}"


def _status(item: dict) -> str:
    if item["stale"]:
        return f"STALE — {item.get('age_days', '?')} days; reviewer decision recorded in close log"
    return f"Expected to clear {item['expected_clearing']}"


def main(rec_path: str, period_label: str, reviewer: str, out_path: str,
         entity: str, account: str, bank_line: str, footer: str) -> None:
    rec = json.load(open(rec_path, encoding="utf-8"))
    rs = rec["reconciliation_statement"]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bank Reconciliation"

    rows: list[tuple] = [
        (entity, None, None),
        (f"Bank reconciliation — {account} ({bank_line})", None, None),
        (f"As at {period_label}   |   Prepared: verified-close reconciliation "
         f"(AI-assisted, script-computed)   |   Reviewed: {reviewer}", None, None),
        (None, None, None),
        (f"Balance per bank statement at {period_label}", rs["balance_per_bank_gbp"], "Status"),
        (None, None, None),
        ("Less: unpresented payments", None, None),
    ]
    for item in rec["closing_items"]:
        if item["amount_gbp"] < 0:
            rows.append((_label(item), item["amount_gbp"], _status(item)))
    rows += [(None, None, None), ("Add: uncleared lodgements", None, None)]
    for item in rec["closing_items"]:
        if item["amount_gbp"] > 0:
            rows.append((_label(item), item["amount_gbp"], _status(item)))
    rows += [
        (None, None, None),
        (f"Balance per cashbook at {period_label}", rs["cashbook_closing_balance_gbp"], None),
        (f"Statement lines explained: {rec['matched']}/{rec['statement_lines']}; "
         "checks C1-C5 passed; sign-off sealed in the close log.", None, None),
        (None, None, None),
        (footer, None, None),
    ]
    for r in rows:
        ws.append(r)
    for row_idx in (1, 2):
        ws.cell(row=row_idx, column=1).font = Font(bold=True)
    ws.column_dimensions["A"].width = 62
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 46
    for row in ws.iter_rows(min_col=2, max_col=2):
        row[0].number_format = "#,##0.00"
    wb.save(out_path)
    print(f"reconciliation written: {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:9])

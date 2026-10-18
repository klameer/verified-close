"""Parse last month's bank reconciliation xlsx into opening-position JSON.

Usage: parse_rec.py "Bank Reconciliation - ... Apr-26.xlsx" opening_rec.json <period_end>

Reads the layout write_rec.py writes, so each month's signed rec is next
month's opening position. Item labels like "(14 Apr)" are dated in the
year of <period_end> (ISO), or the year before when that would be later.

Extracts: bank balance, book balance, and every reconciling item with its
signed amount (negative = unpresented payment, positive = uncleared
lodgement) and the date in its label (e.g. "(14 Apr)").
Requires openpyxl.
"""
import json
import re
import sys
from datetime import date

import openpyxl

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def _label_date(label: str, end: date) -> str | None:
    m = re.search(r"\((\d{1,2}) (\w{3})(?:[^)]*)?\)\s*$", label)
    if not m:
        return None
    d = date(end.year, MONTHS[m.group(2)], int(m.group(1)))
    return (d if d <= end else d.replace(year=end.year - 1)).isoformat()


def main(xlsx_path: str, out_path: str, period_end: str) -> None:
    ws = openpyxl.load_workbook(xlsx_path).active
    result = {"source_file": xlsx_path.split("/")[-1].split("\\")[-1],
              "as_at": None, "bank_balance_gbp": None, "book_balance_gbp": None,
              "items": []}
    end = date.fromisoformat(period_end)
    for label, value, status in ws.iter_rows(values_only=True):
        if not label:
            continue
        text = str(label).strip()
        if text.startswith("As at"):
            result["as_at"] = text.split("|")[0].replace("As at", "").strip()
        elif text.startswith("Balance per bank statement"):
            result["bank_balance_gbp"] = round(float(value), 2)
        elif text.startswith("Balance per cashbook"):
            result["book_balance_gbp"] = round(float(value), 2)
        elif str(label).startswith("  ") and isinstance(value, (int, float)):
            result["items"].append({
                "description": text,
                "amount_gbp": round(float(value), 2),
                "kind": "unpresented_payment" if value < 0 else "uncleared_lodgement",
                "item_date": _label_date(text, end),
                "status": status or "",
            })
    assert result["bank_balance_gbp"] and result["book_balance_gbp"] and result["items"]
    tie = result["bank_balance_gbp"] + sum(i["amount_gbp"] for i in result["items"])
    assert abs(tie - result["book_balance_gbp"]) < 0.01, "parsed rec does not tie"
    json.dump(result, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1)
    print(f"parsed {len(result['items'])} opening item(s); rec ties -> {out_path}")


if __name__ == "__main__":
    main(*sys.argv[1:4])

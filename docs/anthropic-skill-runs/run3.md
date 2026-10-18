# Run 3: Anthropic's reconciliation skill, unmodified (knowledge-work-plugins @ 33eeda1)

_18 model turns, 65s, API-equivalent $0.29. Paths redacted._

## Code Claude wrote and ran

### shell

```text
cd "<close folder>/02 System Exports/May-26"; wc -c *.json; cat "Bank Statement - May-26.json"; echo; cat "Cashbook - May-26.json"
```

### shell

```text
cd "<close folder>/05 Month-End/Apr-26"; python -I -c "
import openpyxl
wb=openpyxl.load_workbook('Bank Reconciliation - Operating Account - Apr-26.xlsx')
for ws in wb:
  print('##',ws.title)
  for r in ws.iter_rows():
    for c in r:
      if c.value is not None: print(c.coordinate,repr(c.value))
"
```

### shell

```text
cd "<close folder>"; cat "02 System Exports/May-26/Trial Balance - May-26.json"; cat > "$TEMP/x.py" <<'E'
import zipfile,re,sys
z=zipfile.ZipFile(sys.argv[1])
print(z.namelist())
ss=[]
if 'xl/sharedStrings.xml' in z.namelist():
    ss=[re.sub('<[^>]+>','',m) for m in re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode(),re.S)]
for n in z.namelist():
    if n.startswith('xl/worksheets/sheet'):
        print('##',n)
        for c in re.finditer(r'<c r="(\w+)"([^>]*?)(?:/>|>(.*?)</c>)',z.read(n).decode(),re.S):
            r,a,b=c.groups()
            if not b: continue
            f=re.search(r'<f>(.*?)</f>',b); v=re.search(r'<v>(.*?)</v>',b)
            val=v.group(1) if v else ''
            if 't="s"' in a: val=ss[int(val)]
            print(r,val,('='+f.group(1)) if f else '')
E
python -I "$TEMP/x.py" "05 Month-End/Apr-26/Bank Reconciliation - Operating Account - Apr-26.xlsx"
```

### write 

```text
import zipfile,re,sys
z=zipfile.ZipFile(sys.argv[1])
ss=[]
if 'xl/sharedStrings.xml' in z.namelist():
    ss=[re.sub('<[^>]+>','',m) for m in re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode(),re.S)]
for n in z.namelist():
    if n.startswith('xl/worksheets/sheet'):
        print('##',n)
        for c in re.finditer(r'<c r="(\w+)"([^>]*?)(?:/>|>(.*?)</c>)',z.read(n).decode(),re.S):
            r,a,b=c.groups()
            if not b: continue
            f=re.search(r'<f>(.*?)</f>',b); v=re.search(r'<v>(.*?)</v>',b)
            val=v.group(1) if v else ''
            if 't="s"' in a: val=ss[int(val)]
            print(r,val,('='+f.group(1)) if f else '')
```

### shell

```text
cd "<close folder>"; S="<claude temp>"; python -I "$S" "05 Month-End/Apr-26/Bank Reconciliation - Operating Account - Apr-26.xlsx"; echo ======; python -I "$S" "05 Month-End/May-26/Cashbook Extract - May-26.xlsx" | head -60
```

### shell

```text
$s='<path>'
$b='<path>'
python -I $s "$b\05 Month-End\Apr-26\Bank Reconciliation - Operating Account - Apr-26.xlsx"
"======"
python -I $s "$b\05 Month-End\May-26\Cashbook Extract - May-26.xlsx" | Select-Object -First 40
```

### shell

```text
python -I '<path>' '<path> Month-End\Apr-26\Bank Reconciliation - Operating Account - Apr-26.xlsx'
```

### shell

```text
python -I '<path>' '<path> Month-End\May-26\Cashbook Extract - May-26.xlsx' | Select-Object -First 30
```

### shell

```text
python -I "<claude temp>" "<close folder>/05 Month-End/Apr-26/Bank Reconciliation - Operating Account - Apr-26.xlsx"
```

### write x.py

```text
if 't="s"' in a: val=ss[int(val)]
            t=re.findall(r'<t[^>]*>(.*?)</t>',b,re.S)
            if t: val=''.join(t)
```

### shell

```text
python -I "<claude temp>" "<close folder>/05 Month-End/Apr-26/Bank Reconciliation - Operating Account - Apr-26.xlsx"
```

### write rec.py

```text
import json
from decimal import Decimal as D
b='<close folder>/02 System Exports/May-26/'
bank=json.load(open(b+'Bank Statement - May-26.json'))['rows']
cb=json.load(open(b+'Cashbook - May-26.json'))
cbr=cb['rows']
def bn(r): return D(r['paid_in_gbp'] or 0)-D(r['paid_out_gbp'] or 0)
open_bank=D(bank[0]['balance_gbp'])-bn(bank[0])
print('bank open',open_bank,'close',bank[-1]['balance_gbp'])
run=open_bank
for r in bank:
    run+=bn(r)
    assert run==D(r['balance_gbp']),(r,run)
print('bank running balance ok')
cbsum=D(str(cb['opening_balance_gbp']))+sum(D(str(r['money_in_gbp']))-D(str(r['money_out_gbp'])) for r in cbr)
print('cb computed close',cbsum,'stated',cb['closing_balance_gbp'])
cbm={r['bank_narrative']:r for r in cbr}
used=set()
for r in bank:
    c=cbm.get(r['description'])
    if not c: print('BANK ONLY',r['date'],r['description'],bn(r)); continue
    used.add(r['description'])
    a=D(str(c['money_in_gbp']))-D(str(c['money_out_gbp']))
    if a!=bn(r): print('AMT DIFF',r['description'],a,bn(r))
tot=D(0)
for k,c in cbm.items():
    if k not in used:
        a=D(str(c['money_in_gbp']))-D(str(c['money_out_gbp'])); tot+=a
        print('CB ONLY',c['entry_ref'],c['book_date'],c['value_date'],k,a)
print('cb only total',tot)
print('dups',len(cbr)-len(cbm))
adj=D(bank[-1]['balance_gbp'])+tot-D('1850.00')
print('bank + cbonly - cheque 1850 =',adj)
```

### shell

```text
python -I "<claude temp>"
```

## Claude's answer

The Operating Account agrees for May-26. After reconciling items, bank and cashbook are both £8,911,388.92, with a £0.00 difference.

## Reconciliation statement: 31 May 2026

Pennine Commercial Bank, 99-42-07 / 00341275.

| | £ |
|---|---:|
| **Balance per bank statement** | **9,882,613.23** |
| Less: unpresented payments | |
| BACS payment run 0528 (value 1 Jun) | (1,191,437.29) |
| BACS expenses batch 0528 (value 1 Jun) | (23,412.77) |
| Cheque 004182, Airedale Window Cleaning (14 Apr), carried from April | (1,850.00) |
| Add: uncleared lodgements | |
| Customer remittance, NHS Trust ref 495765 (value 1 Jun) | 161,309.55 |
| Card settlement batch 2905 (value 1 Jun) | 55,020.10 |
| Card settlement batch 3105 (value 2 Jun) | 29,146.10 |
| **Adjusted bank balance** | **8,911,388.92** |
| **Balance per cashbook** | **8,911,388.92** |
| **Difference** | **0.00** |

Total reconciling items net to (£971,224.31).

## Checks run

- **Bank statement:** Opening balance is £11,257,667.53, matching April's reconciliation. All 48 running balances recompute, and the closing balance is £9,882,613.23.
- **Cashbook:** The opening balance of £10,053,241.57 matches April's closing cashbook. The 50 entries sum to the stated closing balance of £8,911,388.92.
- **Matching:** Every other cashbook entry matched a bank line on narrative and amount. There were no amount differences, duplicates or unrecorded bank items. The May bank charges of £1,842.17 are already in the cashbook as CHG-0529.

## April carry-forwards
- **Cleared on 1 May:** All three April items cleared at their reconciled amounts. These are card settlement batch 3004 (£71,286.40), BACS credit ref 374204 (£138,442.19) and payment run 0429 (£1,412,304.55).
- **Still outstanding:** Cheque 004182 for £1,850.00 has not cleared. By 31 May it is 47 days old, which falls in the 31–60 day "investigate" band. Check whether Airedale Window Cleaning has banked it or lost it, and stop and reissue if needed.

## Reconciling items

| Item | Category | Action |
|---|---|---|
| Cheque 004182, £1,850.00 (47 days) | Timing, but aging | Investigate with payee. |
| The other five items, all value 1–2 Jun | Timing, 0 days old | None; they should clear on the June statement. |

- No items need an adjusting journal.
- No item is over £10,000 except the five timing items. The largest is payment run 0528 at £1.19m, which is routine month-end timing and includes Ridgway Freight's April invoices.
- Total reconciling items are well over the example £100k trigger, but all are one-to-two-day timing items.
- Prepared by me. A reviewer needs to sign off.

## Not verified
- **Pack cash figure:** There is no May Monthly Reporting Pack in the folder, and the trial balance export is P&L only. I couldn't do April's last step, tying the cashbook to pack cash. The cashbook rounds to £8,911k.
- **June clearance:** I haven't confirmed the five timing items against a June statement.
- **Source files:** I used the JSON exports. The May-26 PDF statement and cashbook xlsx in `05 Month-End/May-26/` were not compared with them.

I haven't written a reconciliation workbook to `05 Month-End/May-26/`. I can build one in April's format if you want it.

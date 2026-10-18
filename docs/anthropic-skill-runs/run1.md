# Run 1: Anthropic's reconciliation skill, unmodified (knowledge-work-plugins @ 33eeda1)

_14 model turns, 49s, API-equivalent $0.23. Paths redacted._

## Code Claude wrote and ran

### shell

```text
cd "<close folder>"; cd "02 System Exports/May-26"; wc -c *; cat "Bank Statement - May-26.json"; echo; cat "Cashbook - May-26.json"
```

### shell

```text
cd "<close folder>"; python -I -c "
import openpyxl,sys
for f in ['05 Month-End/Apr-26/Bank Reconciliation - Operating Account - Apr-26.xlsx']:
    wb=openpyxl.load_workbook(f)
    for ws in wb:
        print('##',ws.title)
        for r in ws.iter_rows():
            for c in r:
                if c.value is not None: print(c.coordinate,repr(c.value))
"
```

### shell

```text
cd "<close folder>/05 Month-End/Apr-26" && mkdir -p ../../../x && python -I -c "
import zipfile,re,sys
z=zipfile.ZipFile('Bank Reconciliation - Operating Account - Apr-26.xlsx')
print(z.namelist())
ss=re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode(),re.S) if 'xl/sharedStrings.xml' in z.namelist() else []
ss=[re.sub('<[^>]+>','',s) for s in ss]
for n in z.namelist():
    if 'worksheets/sheet' in n:
        print('##',n)
        x=z.read(n).decode()
        for m in re.finditer(r'<c r=\"(\w+)\"([^>]*?)(?:/>|>(.*?)</c>)',x,re.S):
            r,a,b=m.groups()
            if not b: continue
            v=re.search(r'<v>(.*?)</v>',b); f=re.search(r'<f>(.*?)</f>',b)
            val=v.group(1) if v else re.sub('<[^>]+>','',b)
            if 't=\"s\"' in a: val=ss[int(val)]
            print(r,val,('='+f.group(1)) if f else '')
"
```

### shell

```text
python -I -c "
import zipfile,re
z=zipfile.ZipFile(r'<close folder>/05 Month-End/Apr-26/Bank Reconciliation - Operating Account - Apr-26.xlsx')
ss=[re.sub('<[^>]+>','',s) for s in re.findall(r'<si>(.*?)</si>',z.read('xl/sharedStrings.xml').decode(),re.S)] if 'xl/sharedStrings.xml' in z.namelist() else []
print(z.namelist())
for n in z.namelist():
    if 'worksheets/sheet' in n:
        print('##',n)
        x=z.read(n).decode()
        for m in re.finditer(r'<c r=\"(\w+)\"([^>]*?)(?:/>|>(.*?)</c>)',x,re.S):
            r,a,b=m.groups()
            if not b: continue
            v=re.search(r'<v>(.*?)</v>',b); f=re.search(r'<f>(.*?)</f>',b)
            val=v.group(1) if v else re.sub('<[^>]+>','',b)
            if 't=\"s\"' in a: val=ss[int(val)]
            print(r,val,('='+f.group(1)) if f else '')
"
```

### shell

```text
python -I -c "
import json
d='<close folder>/02 System Exports/May-26/'
b=json.load(open(d+'Bank Statement - May-26.json'))['rows'];c=json.load(open(d+'Cashbook - May-26.json'))
from decimal import Decimal as D
bn={}
for r in b: bn.setdefault(r['description'],[]).append(D(r['paid_in_gbp'] or 0)-D(r['paid_out_gbp'] or 0))
print(len(b),len(c['rows']))
cb=D(str(c['opening_balance_gbp']))
cn={}
for r in c['rows']:
    a=D(str(r['money_in_gbp']))-D(str(r['money_out_gbp'])); cb+=a; cn[r['bank_narrative']]=a
print('cb calc',cb,c['closing_balance_gbp'])
print('bank-only'); 
for k,v in bn.items():
    if k not in cn: print(k,v)
    elif cn[k]!=v[0]: print('DIFF',k,v,cn[k])
print('book-only')
for k,v in cn.items():
    if k not in bn: print(k,v)
# bank balance continuity
prev=D('11257667.53')
for r in b:
    prev+=D(r['paid_in_gbp'] or 0)-D(r['paid_out_gbp'] or 0)
    if prev!=D(r['balance_gbp']): print('BREAK',r); prev=D(r['balance_gbp'])
print(prev)
"
```

### write rec.py

```text
import json, sys
from decimal import Decimal as D
d = sys.argv[1]
b = json.load(open(d + 'Bank Statement - May-26.json'))['rows']
c = json.load(open(d + 'Cashbook - May-26.json'))
bn = {}
for r in b:
    bn.setdefault(r['description'], []).append(D(r['paid_in_gbp'] or 0) - D(r['paid_out_gbp'] or 0))
print(len(b), len(c['rows']))
cb = D(str(c['opening_balance_gbp']))
cn = {}
for r in c['rows']:
    a = D(str(r['money_in_gbp'])) - D(str(r['money_out_gbp']))
    cb += a
    cn[r['bank_narrative']] = a
print('cb calc', cb, c['closing_balance_gbp'])
print('bank-only')
for k, v in bn.items():
    if k not in cn:
        print(k, v)
    elif cn[k] != v[0]:
        print('DIFF', k, v, cn[k])
print('book-only')
for k, v in cn.items():
    if k not in bn:
        print(k, v)
prev = D('11257667.53')
for r in b:
    prev += D(r['paid_in_gbp'] or 0) - D(r['paid_out_gbp'] or 0)
    if prev != D(r['balance_gbp']):
        print('BREAK', r)
        prev = D(r['balance_gbp'])
print('bank close', prev)
```

### shell

```text
python -I "<claude temp>" "<close folder>/02 System Exports/May-26/"
```

## Claude's answer

**Operating Account (Pennine Commercial Bank 99-42-07 / 00341275), 31 May 2026: it agrees. The difference is £0.00.**

I used the JSON exports as the source. I did not open the May-26 PDF or xlsx in `05 Month-End/May-26`.

**Reconciliation statement (GBP)**

| | £ |
|---|---:|
| Balance per bank statement, 31 May | 9,882,613.23 |
| *Less: unpresented payments* | |
| Cheque 004182, Airedale Window Cleaning (14 Apr) | (1,850.00) |
| BACS expenses batch 0528 (value 1 Jun) | (23,412.77) |
| BACS supplier payment run 0528, incl. Ridgway Freight April invoices (value 1 Jun) | (1,191,437.29) |
| *Add: uncleared lodgements* | |
| Card settlement 2905 (value 1 Jun) | 55,020.10 |
| BACS credit ref 495765 NHS Trust (value 1 Jun) | 161,309.55 |
| Card settlement 3105, Sunday online orders (value 2 Jun) | 29,146.10 |
| **Adjusted bank balance** | **8,911,388.92** |
| Balance per cashbook, 31 May | 8,911,388.92 |
| **Difference** | **0.00** |

**Checks**
- The cashbook opening balance of £10,053,241.57 equals the April reconciliation's closing cashbook balance.
- The cashbook rolls forward to £8,911,388.92, so the stated closing balance is arithmetically correct.
- The bank statement's running balance is continuous. It opens at £11,257,667.53, which equals April's bank balance, and closes at £9,882,613.23.
- Three April reconciling items cleared on 1 May at the exact amounts: payment run 0429 (£1,412,304.55), BACS ref 374204 (£138,442.19) and card batch 3004 (£71,286.40).
- The other 45 bank lines match the cashbook one-to-one on narrative and amount. The 5 cashbook-only items plus the carried-forward cheque are listed above.

**Reconciling items**
- **Timing (no adjusting entry):** all 5 May cashbook-only items. They have 1–2 June value dates and should clear in the first days of June.
  - Net unpresented payments are £1,214,850.06 (excluding the cheque).
  - Net lodgements in transit are £245,475.75.
- **Cheque 004182 (£1,850):**
  - It was carried from April and is still unpresented.
  - It is 47 days old at 31 May, so it falls in the 31–60 day "Aging" bucket. The skill says to investigate: chase the payee, then stop or reissue if it stays uncashed.
  - It is below the £10k escalation threshold.
- **Adjustments required:** none.
  - Bank charges of £1,842.17 are already in the cashbook.
  - There are no unrecorded bank items and no errors on either side.
- **Total reconciling items:** about £1.46m gross. Payment run 0528 alone is £1.19m, well above the example £50k controller-review threshold, but it is a normal month-end run clearing on the next working day. Confirm it clears on 1 June.

**Open points**
- The trial balance export has no cash or bank line that I could find, so I did not agree the cashbook to the GL or the board-pack cash figure. April's reconciliation did that tie-out, so it still needs doing for May.
- Preparer and reviewer sign-off is blank.

I wrote nothing to the project folder and created no tracking item. Say if you want this as an xlsx in `05 Month-End/May-26/`.

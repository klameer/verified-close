# Three runs of Anthropic's reconciliation skill, unmodified

On 18 October 2026 I ran Anthropic's own `reconciliation` skill three times on the same month of
Caldergate data. I used it exactly as published, from anthropics/knowledge-work-plugins at commit
`33eeda1`. The aim was to see what the skill does on its own, before any of verified-close's
scripts or gates are involved.

**Set-up**
- **The plugin.** Anthropic's `finance/` folder, with every imported file checked byte for byte
  against `UPSTREAM.json` (10/10 identical). It was loaded with `claude --plugin-dir`.
- **The data.** Each run got a fresh copy of `examples/caldergate/`. I removed `close.toml`, the
  governance folder (it holds the golden set, the answer key) and any working files, which left
  the ERP exports, last month's reconciliation and the estate documents.
- **The prompt**, the same every run: *"Using the finance plugin's reconciliation skill, reconcile
  the Operating Account bank account for May-26 (period end 31 May 2026). The bank statement and
  cashbook exports are in '02 System Exports/May-26/', and last month's reconciliation is in
  '05 Month-End/Apr-26/'. Give me the reconciliation statement, the reconciling items, and whether
  it agrees."*
- **The harness.** Claude Code ran headless (`claude -p`) with no user settings, no MCP servers,
  and the same tool allowance each run: Python, file reads and writes, search, skills.

**What happened**

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Bank to cashbook | agrees, 0.00 | agrees, 0.00 | agrees, 0.00 |
| Reconciling items | 6 | 6 | 6 |
| Cheque 004182 found | yes | yes | yes |
| Code Claude wrote | 107 lines | 97 lines | 91 lines |
| The cheque, called | "Aging" (31 to 60 days) | "stale" | "Timing, but aging" |
| Sign-off | left blank | left blank | "A reviewer needs to sign off" |
| Model time | 49 s | 51 s | 65 s |

Each file holds every command and script Claude ran, plus its full answer. Local paths are
redacted to `<close folder>` and `<path>`.

This is a demonstration, not a statistic: three runs on clean, fictional data, with one bank
account and one month. The essay that discusses it is *What Anthropic's finance plugin leaves to
you* (codelessops.com).

# Verified Close — rules for agents

Portfolio: Free public Claude plugin for the month-end close: Anthropic's Apache-2.0 finance skills plus scripted figures, reviewer gates and an audit log (Caldergate worked example).

Universal rules apply (`~/.claude/CLAUDE.md`). Ops project `PLG` (slug `verified-close`). Plan and
decisions: `CHARTER.md`. Design: `SPEC.md` (draft until Karim signs the merge grid; no code before that).

- **Upstream is Apache-2.0** (`anthropics/knowledge-work-plugins`, `finance/`, pinned SHA in
  `UPSTREAM.md`). Keep the licence text; every upstream file we change gets a one-line
  "Modified from anthropics/knowledge-work-plugins@<sha>: <what>" notice at the top. Never import
  partner-built content (S&P/Kensho, LSEG) or the MIT partner plugins.
- **No Anthropic or Claude marks in names** and nothing implying endorsement. "A plugin for Claude"
  describes; "Claude for Finance" claims.
- **Every figure is computed by a script; every step stops at a reviewer gate.** A skill without a
  script says "guidance only" in the README table. Never present a guidance skill as verified.
- **Data is fictional only.** Sample data = Caldergate close-v2, copied from
  `C:/Projects/20261013_BusinessAssets/caldergate/source-data/close-v2/` (read that folder's README
  first). Never the Board Pack Test holdout or generator. Never real client data (Exscientia, Fox).
- **Never quote the Board Pack Test** score anywhere in this repo, README or posts.
- The skills never post to a ledger. Output = files for a reviewer.
- Public from v0.1 with clean history. Karim creates the empty GitHub repo; no push without his word.
- Tests before every commit once code exists: `pytest` (scripts, goldens G1-G6, gate tests).

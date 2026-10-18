"""Print the close status board, derived from the close log, never claimed.

Usage: status.py <close.toml> [--now "<what is happening right now>"]

A step counts as done solely when its signed record is in the log. The
optional --now line labels what the run is doing this moment; everything
else is derived. No log = the close has not started. Always exits 0.
"""
import sys

from closecfg import STEP_TITLES, Close


def main(argv: list[str]) -> None:
    close = Close(argv[0])
    now = argv[2] if len(argv) > 2 and argv[1] == "--now" else None
    signed = close.records()
    steps = list(STEP_TITLES)

    print(f"CLOSE STATUS - {close.entity} - {close.period}")
    next_seen = False
    for i, step in enumerate(steps):
        label = STEP_TITLES[step]
        r = signed.get(step)
        if r:
            when = r["signed_at_utc"][:16].replace("T", " ")
            print(f"[x] {label:<28} signed {r['reviewer']} {when}Z  sha256 {r['result_sha256'][:12]}")
        elif not next_seen:
            print(f"[ ] {label:<28} <- next")
            next_seen = True
        else:
            print(f"[ ] {label:<28} blocked (needs {STEP_TITLES[steps[i - 1]].split('  ')[0]} signed)")
    done = signed.get("closeout")
    if done:
        when = done["signed_at_utc"][:16].replace("T", " ")
        print(f"[x] {'Close-out (audit binder)':<28} filed {when}Z  sha256 {done['result_sha256'][:12]}")
    else:
        ready = all(s in signed for s in steps)
        print(f"[ ] {'Close-out (audit binder)':<28} "
              + (f'ready - say "Close out {close.period}"' if ready
                 else "blocked (needs all three steps signed)"))
    if now:
        print(f"now: {now}")
    print("derived from the close log: a step is done only when its signed record is in the log")


if __name__ == "__main__":
    main(sys.argv[1:])

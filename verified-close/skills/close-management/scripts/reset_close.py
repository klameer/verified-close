"""Reset the period's close so it can be run again (demos, dry runs, testing).

Usage: reset_close.py <close.toml> [--yes]

Without --yes it only lists what would go. Removes the period's working
folder (including the close log) and, from the filing folder, ONLY the
files a run produces: "* DRAFT.*", "* SIGNED *.*", the close binder and
close-log.jsonl. Estate documents (statements, extracts, prior months,
templates, board papers) are never touched.
"""
import fnmatch
import shutil
import sys

from closecfg import Close


def main(toml: str, confirm: str = "") -> None:
    close = Close(toml)
    patterns = ["* DRAFT.*", "* SIGNED *.*", f"Close Binder - {close.period}.pdf", "close-log.jsonl"]
    filing = close.folder("filing")
    doomed = sorted(p for p in filing.iterdir()
                    if p.is_file() and any(fnmatch.fnmatch(p.name, pat) for pat in patterns)) \
        if filing.exists() else []
    work = close.folder("work")
    print(f"reset {close.period}: working folder {work.relative_to(close.root).as_posix()}"
          + (" (exists)" if work.exists() else " (none)"))
    for p in doomed:
        print(f"  filing: {p.name}")
    if confirm != "--yes":
        print("dry run: nothing removed. Re-run with --yes to reset.")
        return
    shutil.rmtree(work, ignore_errors=True)
    for p in doomed:
        p.unlink()
    print(f"{close.period} reset: {len(doomed)} filing(s) and the working folder removed; "
          "the close log is empty.")


if __name__ == "__main__":
    main(*sys.argv[1:3])

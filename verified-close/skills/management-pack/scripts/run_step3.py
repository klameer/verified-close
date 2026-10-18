"""Step 3 of the close: the management pack, filled from signed figures only.

Usage: run_step3.py <close.toml>

Gate: refuses to run until steps 1 and 2 are signed and both seals hold
(a figure edited after sign-off stops the pack). Needs the pack commentary
at <work>/step3/commentary.txt. build_pack -> checks -> DRAFT filed. Hard
check failures stop with exit 1; commentary numbers the checks cannot trace
to a signed source are listed as REVIEWER MUST VERIFY for the gate.
"""
import shutil
import sys
from pathlib import Path

from closecfg import Close, run_stage, stop

HERE = Path(__file__).resolve().parent


def main(toml: str) -> None:
    close = Close(toml)
    close.require_signed("step1", "step2")
    close.require_unsigned("step3")
    w = close.work("step3")
    commentary = w / "commentary.txt"
    if not commentary.exists():
        stop(f"write the pack commentary to {commentary.relative_to(close.root).as_posix()} "
             "first: the signed step 2 commentary on the flagged lines, plus one line on the "
             "bank position, every number with its source")
    template = w / "template.pptx"
    shutil.copyfile(close.folder("templates") / close.file("pack_template"), template)
    rec = close.work("step1") / "reconciliation.json"
    var = close.work("step2") / "variance.json"
    pack = w / f"Management Pack - {close.period}.pptx"

    run_stage(HERE / "build_pack.py", template, rec, var, commentary, close.log_path,
              close.period, pack, label="STEP 3")
    run_stage(HERE / "checks.py", pack, rec, var, commentary, label="STEP 3")
    draft = f"Management Pack - {close.period} DRAFT.pptx"
    shutil.copyfile(pack, w / draft)
    close.file_into(w / draft)
    close.confirm_filed([draft])


if __name__ == "__main__":
    main(*sys.argv[1:2])

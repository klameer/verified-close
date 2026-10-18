"""The close folder: its close.toml, its paths, and the close log's gate rules.

Every scripted skill ships an identical copy of this file (skills install
self-contained); tests/test_structure.py fails the build if the copies drift.
Stdlib only, Python 3.11+.

The gate rules live here, in code, so no step can run past an unsigned
predecessor however the conversation goes:
  - require_signed(): a step refuses to run until the steps before it hold
    a signed record in the close log
  - require_seal(): a signed result file must still hash to the sha256
    sealed at sign-off; any edit after signing stops the close
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252

STEP_TITLES = {"step1": "Step 1  Bank reconciliation",
               "step2": "Step 2  Variance report",
               "step3": "Step 3  Management pack"}


def stop(message: str) -> None:
    print(message)
    sys.exit(1)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_stage(script: Path, *args, label: str) -> None:
    """Run one pipeline stage as its own process, echo it verbatim, stop on failure."""
    result = subprocess.run([sys.executable, str(script), *map(str, args)],
                            capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "PYTHONUTF8": "1"})
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="")
        stop(f"{label} STOPPED at {Path(script).name} (exit {result.returncode}) "
             "- do not present results")


class Close:
    def __init__(self, toml_path: str):
        self.toml = Path(toml_path).resolve()
        if not self.toml.exists():
            stop(f"no close.toml at {self.toml}: run from the close folder or pass its path")
        self.root = self.toml.parent
        cfg = tomllib.loads(self.toml.read_text(encoding="utf-8"))
        self.cfg = cfg
        self.entity = cfg["entity"]["name"]
        self.currency = cfg["entity"].get("currency", "GBP")
        self.fictional = cfg["entity"].get("fictional", False)
        self.period = cfg["period"]["id"]
        self.prior = cfg["period"]["prior"]
        self.period_end: date = cfg["period"]["end"]
        self.period_label = cfg["period"]["label"]
        self.bank = cfg["bank"]
        self.variance = cfg["variance"]

    # ---- paths -------------------------------------------------------------
    def folder(self, key: str) -> Path:
        rel = self.cfg["folders"][key].format(period=self.period, prior=self.prior)
        return self.root / rel

    def file(self, key: str) -> str:
        return self.cfg["files"][key].format(period=self.period, prior=self.prior,
                                             account=self.bank["account"])

    def work(self, sub: str = "") -> Path:
        p = self.folder("work") / sub
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_path(self) -> Path:
        return self.work("audit") / "close-log.jsonl"

    def footer(self) -> str:
        return f"{self.entity} - Confidential." + (
            " Fictitious data (demo estate)." if self.fictional else "")

    def file_into(self, src: Path, name: str | None = None) -> Path:
        """Copy an output into the filing folder (the reviewer's surface)."""
        dst_dir = self.folder("filing")
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / (name or Path(src).name)
        shutil.copyfile(src, dst)
        return dst

    def confirm_filed(self, names: list[str]) -> None:
        """One listing of the filing folder; a missing filing stops the step."""
        present = {p.name for p in self.folder("filing").iterdir()}
        missing = [n for n in names if n not in present]
        if missing:
            stop("FILING FAILED - not in the filing folder: " + "; ".join(missing))
        print(f"filed in {self.folder('filing').relative_to(self.root)}: " + "; ".join(names))

    # ---- the close log -----------------------------------------------------
    def records(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        if self.log_path.exists():
            for line in self.log_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    if r.get("period", self.period) == self.period:
                        out[r["step"]] = r
        return out

    def require_unsigned(self, step: str) -> None:
        if step in self.records():
            stop(f"GATE: {STEP_TITLES[step].strip()} is already signed for {self.period}. "
                 "A signed step is never re-run; reset the close to start again.")

    def require_signed(self, *steps: str) -> None:
        signed = self.records()
        for step in steps:
            if step not in signed:
                stop(f"GATE: {STEP_TITLES[step]} is not signed for {self.period}. "
                     "This step cannot run until a named reviewer signs it.")
            self.require_seal(signed[step])

    def require_seal(self, record: dict) -> None:
        sealed = [{"file": record["result_file"], "sha256": record["result_sha256"]}]
        for item in sealed + record.get("sealed_files", []):
            path = self.root / item["file"]
            if not path.exists():
                stop(f"SEAL BROKEN: signed file {item['file']} is missing")
            if sha256(path) != item["sha256"]:
                stop(f"SEAL BROKEN: {item['file']} changed after {record['reviewer']} "
                     f"signed it ({record['signed_at_utc']}). The close stops here.")

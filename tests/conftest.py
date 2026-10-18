import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "verified-close" / "skills"
EXAMPLE = ROOT / "examples" / "caldergate"

SCRIPT_HOME = {
    "run_step1.py": "reconciliation", "sign_step1.py": "reconciliation",
    "run_step2.py": "variance-analysis", "sign_step2.py": "variance-analysis",
    "run_step3.py": "management-pack", "sign_step3.py": "management-pack",
    "close_out.py": "close-management", "status.py": "close-management",
    "reset_close.py": "close-management", "run_goldens.py": "close-management",
}


class CloseFolder:
    """A fresh copy of the Caldergate close folder and a way to run the scripts in it."""

    def __init__(self, path: Path):
        self.path = path
        self.work = path / "_work" / "May-26"
        self.filing = path / "05 Month-End" / "May-26"

    def run(self, script: str, *args: str) -> subprocess.CompletedProcess:
        exe = SKILLS / SCRIPT_HOME[script] / "scripts" / script
        return subprocess.run([sys.executable, str(exe), "close.toml", *args], cwd=self.path,
                              capture_output=True, text=True, encoding="utf-8",
                              env={**os.environ, "PYTHONUTF8": "1"})

    def ok(self, script: str, *args: str) -> str:
        r = self.run(script, *args)
        assert r.returncode == 0, f"{script} failed:\n{r.stdout}\n{r.stderr}"
        return r.stdout

    def write(self, rel: str, text: str) -> None:
        p = self.work / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    # the happy path, one step at a time
    def sign_step1(self):
        self.ok("run_step1.py")
        self.ok("sign_step1.py", "KL", "K. Lameer", "cheque 004182: stop and reissue")

    def sign_step2(self):
        self.ok("run_step2.py")
        self.write("step2/commentary.md", "Facilities & Safety Supplies +127.0: driver not evidenced "
                   "in the documents: Commercial Director to comment.\n")
        self.ok("run_step2.py")
        self.ok("sign_step2.py", "KL")

    def sign_step3(self):
        self.write("step3/commentary.txt", "Cash reconciled to the cashbook at 8,911,388.92 "
                   "(signed step 1).\nFacilities & Safety Supplies +127.0 vs budget: driver not "
                   "evidenced, Commercial Director to comment.\n")
        self.ok("run_step3.py")
        self.ok("sign_step3.py", "KL")


@pytest.fixture
def close(tmp_path: Path) -> CloseFolder:
    dst = tmp_path / "caldergate"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("_work"))
    return CloseFolder(dst)

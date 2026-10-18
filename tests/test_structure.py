"""The repository's promises about itself: provenance, shared code, skill layout, README table."""
import hashlib
import re
import subprocess
import sys

from conftest import ROOT, SKILLS

SHARED = {"closecfg.py": ["close-management", "reconciliation", "variance-analysis", "management-pack"],
          "audit_record.py": ["reconciliation", "variance-analysis", "management-pack"]}


def test_shared_helpers_are_identical_in_every_skill():
    for name, skills in SHARED.items():
        digests = {s: hashlib.sha256((SKILLS / s / "scripts" / name).read_bytes()).hexdigest()
                   for s in skills}
        assert len(set(digests.values())) == 1, f"{name} drifted: {digests}"


def test_upstream_files_are_verbatim_or_marked():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "upstream.py"), "check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_every_skill_has_frontmatter_matching_its_folder():
    for skill in SKILLS.iterdir():
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        fm = text.split("---\n")[1]
        assert re.search(rf"^name: {re.escape(skill.name)}$", fm, re.M), skill.name
        assert re.search(r"^description: .{40,}", fm, re.M), skill.name


def test_every_scripted_skill_says_so_and_every_script_it_names_exists():
    for skill in SKILLS.iterdir():
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        named = set(re.findall(r"`(\w+\.py)", text))
        scripts = {p.name for p in (skill / "scripts").glob("*.py")} if (skill / "scripts").exists() else set()
        assert named <= scripts, f"{skill.name} names missing scripts: {named - scripts}"
        assert bool(scripts) == ("Verified run" in text), skill.name


def test_readme_lists_every_skill():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for skill in SKILLS.iterdir():
        assert f"`{skill.name}`" in readme, f"README skill table is missing {skill.name}"

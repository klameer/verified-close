"""Turn a recorded headless run (claude -p --output-format stream-json, one file per turn)
into a readable markdown transcript: the reviewer's words, Claude's replies, and every tool
call with its output folded underneath.

Usage: python tools/transcript.py <logs_dir> <out.md> "<prompt 1>" "<prompt 2>" ...
"""
import json
import re
import sys
from pathlib import Path

SEP = r"[\\/]+"
REDACT = [  # the recording machine's paths become placeholders
    (re.compile(rf"[A-Za-z]:{SEP}Users{SEP}[^\\/\s\"']+{SEP}AppData{SEP}Local{SEP}Temp{SEP}\S*?{SEP}run{SEP}caldergate", re.I),
     "<close folder>"),
    (re.compile(rf"[A-Za-z]:{SEP}Projects{SEP}20261018_VerifiedClose{SEP}verified-close", re.I), "<plugin>"),
]


def clean(text: str) -> str:
    for pattern, repl in REDACT:
        text = pattern.sub(repl, text)
    return text


def tool_line(name: str, inp: dict) -> str:
    if name == "Bash":
        return f"`$ {clean(inp.get('command', ''))}`"
    if name == "Skill":
        return f"Load skill `{inp.get('skill')}`"
    if name in ("Write", "Edit"):
        return f"{name} `{clean(inp.get('file_path', ''))}`"
    if name == "Read":
        return f"Read `{clean(inp.get('file_path', ''))}`"
    return f"{name} `{clean(json.dumps(inp))[:200]}`"


def result_text(content) -> str:
    if isinstance(content, list):
        content = "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return clean(str(content)).strip()


def main(logs: str, out: str, *prompts: str) -> None:
    md = []
    for n, prompt in enumerate(prompts, 1):
        md.append(f"## Turn {n}\n\n**Reviewer:** {prompt}\n")
        pending = {}
        for line in (Path(logs) / f"turn{n}.jsonl").read_text(encoding="utf-8").splitlines():
            e = json.loads(line)
            if e.get("type") == "assistant":
                for c in e["message"]["content"]:
                    if c["type"] == "text" and c["text"].strip():
                        md.append(f"**Claude:**\n\n{clean(c['text']).strip()}\n")
                    elif c["type"] == "tool_use":
                        pending[c["id"]] = tool_line(c["name"], c["input"])
                        if c["name"] == "Write":
                            pending[c["id"]] += "\n\n```text\n" + clean(c["input"].get("content", "")).strip() + "\n```"
            elif e.get("type") == "user":
                for c in e["message"]["content"] if isinstance(e["message"]["content"], list) else []:
                    if c.get("type") == "tool_result" and c["tool_use_id"] in pending:
                        call = pending.pop(c["tool_use_id"])
                        body = result_text(c.get("content", ""))
                        if call.startswith("Load skill"):
                            md.append(f"<sub>{call}</sub>\n")
                            continue
                        if call.startswith("Read"):
                            body = body[:600] + ("\n..." if len(body) > 600 else "")
                        md.append(f"<details><summary>{call.splitlines()[0]}</summary>\n\n"
                                  + ("\n".join(call.splitlines()[1:]) + "\n\n" if "\n" in call else "")
                                  + f"```text\n{body}\n```\n</details>\n")
            elif e.get("type") == "result":
                md.append(f"<sub>turn {n}: {e.get('num_turns')} model turns, "
                          f"{e.get('duration_ms', 0) / 1000:.0f}s</sub>\n")
    Path(out).write_text("\n".join(md), encoding="utf-8", newline="\n")
    print(f"transcript: {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])

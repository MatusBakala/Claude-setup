#!/usr/bin/env python3
"""SessionStart hook: vloží do kontextu preferencie a inštinkty.

Zdroje (v tomto poradí):
  1. <plugin>/context/preferencie.md            - globálne preferencie
  2. <plugin>/instincts/*.md                    - schválené globálne inštinkty
  3. <projekt>/.claude/instincts/*.md           - schválené projektové inštinkty
  4. ecc-homunculus (auto-learned observerom)   - neschválené, len confidence >= prah

Hook nikdy nesmie zablokovať štart session, preto všetky chyby ticho preskočí.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or Path(__file__).resolve().parent.parent)
AUTO_MIN_CONFIDENCE = float(os.environ.get("CORE_AUTO_INSTINCT_MIN_CONFIDENCE", "0.7"))
AUTO_MAX = int(os.environ.get("CORE_AUTO_INSTINCT_MAX", "6"))
INSTINCT_SUFFIXES = {".md", ".yaml", ".yml"}


def read_hook_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_root(cwd):
    base = os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd()
    try:
        out = subprocess.run(
            ["git", "-C", base, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except Exception:
        pass
    return Path(base)


def parse_instinct(path):
    """Vráti dict s frontmatter poliami a 'action', alebo None."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    meta = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        if ":" in lines[i]:
            key, _, value = lines[i].partition(":")
            meta[key.strip()] = value.strip().strip('"').strip("'")
        i += 1
    action = ""
    in_action = False
    for line in lines[i + 1:]:
        if line.startswith("## "):
            in_action = line.strip().lower() in ("## action", "## akcia")
            continue
        if in_action and line.strip():
            action = line.strip()
            break
    if not meta.get("id") or not action:
        return None
    try:
        meta["confidence"] = float(meta.get("confidence", "0.5"))
    except ValueError:
        meta["confidence"] = 0.5
    meta["action"] = action
    return meta


def load_dir(directory):
    if not directory.is_dir():
        return []
    items = []
    for path in sorted(directory.iterdir()):
        if path.suffix in INSTINCT_SUFFIXES and path.name.lower() != "readme.md":
            inst = parse_instinct(path)
            if inst:
                items.append(inst)
    return items


def homunculus_dirs(root):
    """Adresáre s auto-learned inštinktmi (projektový + globálny)."""
    learning = PLUGIN_ROOT / "learning" / "scripts"
    script = (
        f'. "{learning}/lib/homunculus-dir.sh"; '
        f'_clv2_resolve_homunculus_dir; '
        f'CLAUDE_PROJECT_DIR="{root}" . "{learning}/detect-project.sh" >/dev/null 2>&1; '
        f'echo "$PROJECT_DIR"'
    )
    try:
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=8)
        lines = [l for l in out.stdout.splitlines() if l.strip()]
    except Exception:
        return []
    dirs = []
    if lines:
        dirs.append(Path(lines[0]) / "instincts" / "personal")
    if len(lines) > 1:
        dirs.append(Path(lines[-1]) / "instincts" / "personal")
    return dirs


def fmt(inst):
    trigger = inst.get("trigger", "").removeprefix("when ").removeprefix("keď ")
    return f"- **{inst['id']}** ({inst['confidence']:.2f}) — keď {trigger}: {inst['action']}"


def main():
    data = read_hook_input()
    root = project_root(data.get("cwd"))
    parts = []

    prefs = PLUGIN_ROOT / "context" / "preferencie.md"
    if prefs.is_file():
        parts.append(prefs.read_text(encoding="utf-8").strip())

    approved_global = load_dir(PLUGIN_ROOT / "instincts")
    approved_project = load_dir(root / ".claude" / "instincts")
    approved_ids = {i["id"] for i in approved_global + approved_project}

    auto = []
    seen = set(approved_ids)
    for d in homunculus_dirs(root):
        for inst in load_dir(d):
            if inst["id"] not in seen and inst["confidence"] >= AUTO_MIN_CONFIDENCE:
                auto.append(inst)
                seen.add(inst["id"])
    auto.sort(key=lambda i: -i["confidence"])
    auto = auto[:AUTO_MAX]

    if approved_global or approved_project or auto:
        section = ["# Inštinkty (naučené pravidlá)"]
        if approved_global:
            section.append("\n## Schválené – globálne")
            section.extend(fmt(i) for i in approved_global)
        if approved_project:
            section.append(f"\n## Schválené – projekt {root.name}")
            section.extend(fmt(i) for i in approved_project)
        if auto:
            section.append("\n## Automaticky naučené (zatiaľ neschválené, ber ako tip, nie pravidlo)")
            section.extend(fmt(i) for i in auto)
        parts.append("\n".join(section))

    if not parts:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n\n".join(parts),
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass

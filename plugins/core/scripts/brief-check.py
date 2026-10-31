#!/usr/bin/env python3
"""Kontrola zadania a odovzdávky implementera – mechanizmus namiesto disciplíny.

Nástroj Agent v Claude Code nemá povinné polia: celé zadanie je jeden voľný `prompt`.
Tento hook preto vynúti šablónu z `skills/pipeline/SKILL.md` na dvoch miestach:

  PreToolUse (Agent)       – zadanie pre `implementer` musí mať Cieľ, Čítaj, Upravuj, Testy
                             a Hotovo keď; pri `isolation: worktree` aj Bázu s commitom.
                             Chýba niečo → volanie sa zablokuje a orchestrátor dostane dôvod.
  SubagentStop (implementer) – report musí obsahovať `commit: <sha>` alebo `BLOCKED`.
                             Inak agent dostane jeden pokus navyše (ako oprava podľa schémy
                             v Hermese); pri druhom zastavení ho hook pustí.

  CORE_BRIEF_CHECK=off     vypne obe kontroly

Hook nikdy nesmie rozbiť session: pri akejkoľvek vlastnej chybe ticho pustí volanie.
"""

import json
import os
import re
import sys
import unicodedata

REQUIRED = [  # (normalizovaný kľúč, názov v šablóne)
    ("ciel", "Cieľ"),
    ("citaj", "Čítaj"),
    ("upravuj", "Upravuj"),
    ("testy", "Testy"),
    ("hotovo ked", "Hotovo keď"),
]
SHA = re.compile(r"\b[0-9a-f]{7,40}\b")


def plain(text):
    """Malé písmená bez diakritiky, aby prešlo aj `Ciel:` či `Hotovo ked:`."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def fields(prompt):
    """Riadky `Kľúč: hodnota` zo zadania; hodnota `<...>` (nevyplnená šablóna) sa neráta."""
    found = {}
    for line in plain(prompt).splitlines():
        m = re.match(r"\s*[-*]?\s*([a-z ]{3,20}?)\s*:\s*(.*\S)?\s*$", line)
        if not m or not m.group(2):
            continue
        value = m.group(2)
        if value.startswith("<") and value.endswith(">"):
            continue
        found.setdefault(m.group(1).strip(), value)
    return found


def is_implementer(name):
    return (name or "").split(":")[-1] == "implementer"


def check_brief(tool_input):
    if not is_implementer(tool_input.get("subagent_type")):
        return None
    got = fields(tool_input.get("prompt") or "")
    missing = [label for key, label in REQUIRED if key not in got]
    problems = []
    if missing:
        problems.append("chýba " + ", ".join(missing))
    if tool_input.get("isolation") == "worktree" and not SHA.search(got.get("baza", "")):
        problems.append("pri isolation: worktree chýba Báza s commitom (worktree vzniká z hlavnej vetvy)")
    if not problems:
        return None
    return (
        "Zadanie pre implementer nie je podľa šablóny v pipeline/SKILL.md: "
        + "; ".join(problems)
        + ". Doplň riadky vo formáte `Pole: hodnota` a zavolaj agenta znova."
    )


def check_report(data):
    if not is_implementer(data.get("agent_type")) or data.get("stop_hook_active"):
        return None
    msg = data.get("last_assistant_message") or ""
    if re.search(r"commit:\s*[0-9a-f]{7,40}", msg, re.I) or "BLOCKED" in msg:
        return None
    return (
        "Odovzdanie implementera je commit, nie zhrnutie. Report neobsahuje `commit: <sha>` ani "
        "`BLOCKED`. Ak je časť hotová, commitni ju podľa zadania a vráť Report; ak nie, napíš "
        "`BLOCKED: <čo chýba>`."
    )


def main():
    if os.environ.get("CORE_BRIEF_CHECK", "").strip().lower() in {"off", "0", "none"}:
        return 0
    data = json.load(sys.stdin)
    event = data.get("hook_event_name")
    if event == "PreToolUse" and data.get("tool_name") in {"Agent", "Task"}:
        reason = check_brief(data.get("tool_input") or {})
        if reason:
            print(reason, file=sys.stderr)  # exit 2 = blokuj, stderr je dôvod pre Clauda
            return 2
    elif event == "SubagentStop":
        reason = check_report(data)
        if reason:
            print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 0
    sys.exit(code)

#!/usr/bin/env python3
"""UserPromptSubmit hook: pripomenie /poucenia, keď observer vytvoril nové inštinkty.

Pripomína, keď pribudol inštinkt, ktorý ešte nebol pripomenutý, alebo keď neschválené
čakajú dlhšie ako REMIND_AGAIN_HOURS. Inak mlčí, aby neotravoval pri každej správe.
Stav (čo už bolo pripomenuté) je v <homunculus>/.core-reminded.json.
"""

import importlib.util
import json
import os
import sys
import time
from pathlib import Path

REMIND_AGAIN_HOURS = float(os.environ.get("CORE_REMIND_AGAIN_HOURS", "24"))

_spec = importlib.util.spec_from_file_location(
    "session_context", Path(__file__).resolve().parent / "session-context.py"
)
ctx = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctx)


def homunculus_base():
    explicit = os.environ.get("CLV2_HOMUNCULUS_DIR", "")
    if explicit.startswith("/"):
        return Path(explicit)
    xdg = os.environ.get("XDG_DATA_HOME", "")
    if xdg.startswith("/"):
        return Path(xdg) / "ecc-homunculus"
    return Path.home() / ".local" / "share" / "ecc-homunculus"


def main():
    data = ctx.read_hook_input()
    root = ctx.project_root(data.get("cwd"))

    approved = {
        i["id"]
        for i in ctx.load_dir(ctx.PLUGIN_ROOT / "instincts") + ctx.load_dir(root / ".claude" / "instincts")
    }
    pending = {}
    for d in ctx.homunculus_dirs(root):
        for inst in ctx.load_dir(d):
            if inst["id"] not in approved:
                pending[inst["id"]] = inst
    if not pending:
        return

    state_file = homunculus_base() / ".core-reminded.json"
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        state = {"ids": [], "ts": 0}

    new_ids = set(pending) - set(state.get("ids", []))
    stale = time.time() - state.get("ts", 0) > REMIND_AGAIN_HOURS * 3600
    if not new_ids and not stale:
        return

    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"ids": sorted(pending), "ts": time.time()}), encoding="utf-8")
    except Exception:
        pass

    names = ", ".join(sorted(new_ids or pending)[:5])
    note = (
        f"[plugin core] Observer naučil {len(pending)} neschválených inštinktov ({names}). "
        "Na konci svojej odpovede to používateľovi pripomeň jednou vetou a ponúkni `/poucenia`. "
        "Ak je session v cloude, dodaj, že neschválené po skončení session zaniknú. "
        "Úlohu, ktorú zadal, tým neprerušuj."
    )
    print(json.dumps({
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass

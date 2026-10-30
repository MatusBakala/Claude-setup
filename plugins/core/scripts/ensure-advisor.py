#!/usr/bin/env python3
"""SessionStart hook: raz na zariadenie nastaví advisora v ~/.claude/settings.json.

Plugin nemôže nastaviť `advisorModel` vo svojich nastaveniach, preto ho zapíše hook do
používateľských nastavení – len ak tam kľúč ešte nie je. Potom si zapíše značku, takže
neskoršia voľba cez `/advisor` (aj `/advisor off`) ostane rešpektovaná.

  CORE_ADVISOR_MODEL=opus   predvolené; `off` = nič nenastavovať

Hook nikdy nesmie zablokovať štart session, preto všetky chyby ticho preskočí.
"""

import json
import os
from pathlib import Path

MODEL = os.environ.get("CORE_ADVISOR_MODEL", "opus").strip()
OFF = {"", "off", "none", "0"}
CLAUDE_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
SETTINGS = CLAUDE_DIR / "settings.json"
MARKER = CLAUDE_DIR / ".core-advisor-applied"


def main():
    if MODEL.lower() in OFF or MARKER.exists():
        return
    settings = {}
    if SETTINGS.is_file():
        text = SETTINGS.read_text(encoding="utf-8").strip()
        settings = json.loads(text) if text else {}
        if not isinstance(settings, dict):
            return
    if "advisorModel" not in settings:
        settings["advisorModel"] = MODEL
        CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
        target = SETTINGS.resolve()  # symlink z dotfiles ostane symlinkom
        tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(target)
    MARKER.write_text(MODEL + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass

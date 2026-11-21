#!/usr/bin/env python3
"""SessionStart hook: stiahne najnovšie poznámky z git repozitára vaultu a obnoví Mapa.md.

Vault (napr. ~/Matus-Agents) je git repozitár zdieľaný medzi počítačmi; poznámky z agenta Hermes
v ňom pribúdajú z iných strojov. Tu ich len stiahneme (`git pull --ff-only`) a hneď prepočítame
mapu, aby Claude na začiatku session videl aj čerstvé poznámky z Hermesa.

Nikdy nepíše ani nepushuje – push poznámok robí Hermes. Hook nesmie zablokovať štart session, preto
chýbajúci vault, chýbajúci git, offline sieť, konflikt alebo časový limit ticho preskočí.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

GIT_PULL_TIMEOUT_SECONDS = 15
MEMORY_MAP_TIMEOUT_SECONDS = 20


def configured_vault():
    config_path = Path.home() / ".claude" / "memory-map.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        config = {}
    vault = os.environ.get("CLAUDE_MEMORY_MAP_VAULT") or config.get("vault")
    return Path(vault).expanduser() if vault else None


def pull_vault(vault):
    if not (vault / ".git").exists():
        return
    try:
        subprocess.run(
            ["git", "-C", str(vault), "pull", "--ff-only", "--quiet"],
            capture_output=True, timeout=GIT_PULL_TIMEOUT_SECONDS,
            # Nikdy sa nepýtaj na heslo – pri chýbajúcom prihlásení pull len zlyhá.
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except Exception:
        pass


def rebuild_map():
    memory_map_script = Path(__file__).resolve().parent / "memory-map.py"
    try:
        subprocess.run([sys.executable, str(memory_map_script), "--hook"],
                       capture_output=True, timeout=MEMORY_MAP_TIMEOUT_SECONDS)
    except Exception:
        pass


def main():
    vault = configured_vault()
    if vault is None or not vault.is_dir():
        return 0
    pull_vault(vault)
    rebuild_map()
    return 0


if __name__ == "__main__":
    sys.exit(main())

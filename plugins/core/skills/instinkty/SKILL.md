---
name: instinkty
description: Správa systému učenia – stav naučených inštinktov, zoskupenie podobných do nového skillu (evolve), povýšenie projektových na globálne (promote), zoznam projektov, stav a log observera na pozadí, zapnutie/vypnutie učenia. Použi na „/instinkty“, „čo vieš o mojich zvykoch“, „evolve“, „beží observer?“, „koľko to míňa“, „vypni učenie“.
---

# Inštinkty – správa učenia

Nad vendorovanou časťou ECC `continuous-learning-v2` (MIT). Schvaľovanie rieši skill `poucenia`.

`<plugin>` = adresár dve úrovne nad týmto skillom (base directory skillu → `../..`).
CLI: `python3 <plugin>/learning/scripts/instinct-cli.py <príkaz>`.

## Príkazy

| Chceš | Spusti |
|-------|--------|
| Prehľad automaticky naučených | `instinct-cli.py status` |
| Zoskupiť podobné, návrhy na skilly | `instinct-cli.py evolve` (náhľad), `--generate` vytvorí súbory |
| Povýšiť projektové na globálne | `instinct-cli.py promote --dry-run`, potom bez `--dry-run` |
| Zoznam projektov | `instinct-cli.py projects` |
| Zmazať staré neschválené | `instinct-cli.py prune` |

K tomu vždy pridaj aj **schválené** inštinkty: `plugins/core/instincts/` (globálne, v plugine)
a `.claude/instincts/` (v aktuálnom projekte) – CLI ich nevidí.

## Evolve – z inštinktov skill

1. `evolve` ukáže zhluky. Pre zhluk, ktorý dáva zmysel, navrhni **jednu** z možností:
   - pravidlo do `plugins/core/context/preferencie.md` (krátke, všeobecné),
   - nový skill do `plugins/core/skills/<nazov>/SKILL.md` (postup s viacerými krokmi),
   - úpravu existujúceho skillu (`fix-bug`, `tdd`, …).
2. Ukáž návrh a po schválení ho zapíš do repa `claude-setup` (postup klonovania a pushu je v skille `poucenia`).
   Zahrnuté inštinkty potom zmaž, aby sa neduplikovali.

## Observer na pozadí

- **Konfigurácia:** `<plugin>/learning/config.json` (`enabled`, `run_interval_minutes`, `min_observations_to_analyze`).
  Lokálny override bez zmeny pluginu: `~/.local/share/ecc-homunculus/config.json`.
- **Dočasne vypnúť všetko pozorovanie:** `touch ~/.local/share/ecc-homunculus/disabled` (zapnúť: zmaž súbor).
- **Model:** premenná `ECC_OBSERVER_MODEL` (predvolene `haiku`); úsilie `ECC_OBSERVER_EFFORT`
  (predvolene `low`, aby observer nededil effort a thinking session); limit rozboru
  `ECC_OBSERVER_TIMEOUT_SECONDS` (predvolene 300 s).
- **Vstupy:** volania nástrojov aj správy používateľa (`user_prompt`, jedna jasná oprava stačí na
  inštinkt) a zoznam schválených inštinktov (globálne v plugine + `<projekt>/.claude/instincts/`),
  ktoré observer nesmie navrhnúť znova.
- **Aktívne hodiny:** `OBSERVER_ACTIVE_HOURS_START` / `_END` (predvolene 800 / 2300).
- **Dáta:** `${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/` (`CLV2_HOMUNCULUS_DIR` ho prepíše).
  Projekty sú v `projects/<hash>/` s `observations.jsonl`, `instincts/personal/` a logom observera.

### Koľko to míňa

Na otázku o spotrebe sa pozri do logov observera v `ecc-homunculus/projects/*/observer.log`:
spočítaj behy analýzy („Analyzing N observations“) za posledné dni a priemerný počet pozorovaní na beh.
Jedno pozorovanie je max. ~10 000 znakov (vstup + výstup nástroja, každý orezaný na 5 000),
takže hrubý odhad tokenov na beh ≈ počet pozorovaní × priemerná dĺžka / 4. Povedz, že ide o odhad.

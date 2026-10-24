# claude-setup

Moje univerzálne prostredie pre Claude Code. Jeden plugin (`core`), ktorý funguje v každom projekte –
na počítači aj v cloude – bez toho, aby som pri novom projekte čokoľvek vyberal.
Postavené na vzoroch z [ECC](https://github.com/affaan-m/ECC) (MIT), zúžené na to, čo reálne používam.

## Čo obsahuje

| Časť | Čo robí |
|------|---------|
| **Pracovné postupy** (skilly) | `fix-bug`, `add-feature`, `change-feature`, `refactor` – Claude si ich vyberie sám podľa úlohy. Spoločná kostra je v `pipeline`: určí veľkosť zmeny, fázy prieskum → plán → TDD → review → overenie → commit a dve brány (schválenie plánu, potvrdenie commitu). |
| **TDD** (skill) | `tdd` – red → green → refactor a ako rozbehnúť testy bez frameworku (vanilla JS cez `node:test`, Python cez pytest/unittest). |
| **Agenti** | `code-explorer`, `planner`, `tdd-guide`, `code-reviewer`, `security-reviewer`, `build-error-resolver` – každý s úzkou rolou. |
| **Preferencie** | `plugins/core/context/preferencie.md` – môj „globálny CLAUDE.md“. Vkladá sa do každej session. |
| **Učenie** | Observer na pozadí (Haiku, z ECC `continuous-learning-v2`) sleduje prácu a navrhuje *inštinkty*. `/poucenia` ich dá na schválenie a schválené uloží natrvalo. `/instinkty` = stav, evolve, nastavenia. |

## Ako funguje učenie

```
práca → hooky zapisujú volania nástrojov → observer (Haiku, max 1× za 5 min, 8:00–23:00)
      → automatické inštinkty (lokálne, ~/.local/share/ecc-homunculus)
      → /poucenia: schváliť / upraviť / zamietnuť
      → schválené: projektové → <projekt>/.claude/instincts/   globálne → plugins/core/instincts/ (toto repo)
      → na začiatku každej session sa vložia do kontextu (schválené ako pravidlá, automatické ≥ 0.7 ako tipy)
```

Lokálne automatické inštinkty v cloude zaniknú s kontajnerom – preto je dôležité občas spustiť `/poucenia`.

## Inštalácia

### Na počítači (raz)

V Claude Code:

```
/plugin marketplace add MatusBakala/claude-setup
/plugin install core@matus
```

Platí potom pre všetky projekty. Aktualizácia po zmene v repe:
`claude plugin marketplace update matus && claude plugin update core@matus`.

### V cloude (claude.ai/code)

Cloud session začína s prázdnym `~/.claude`, preto treba plugin nahlásiť v projekte.
Skopíruj `templates/project-settings.json` do projektu ako `.claude/settings.json`
(alebo jeho obsah zlúč s existujúcim) a commitni. Každá nová cloud session v tom projekte si plugin načíta sama.

Ak je toto repo **súkromné**, cloud session ho stiahne len vtedy, keď má k nemu prístup
(GitHub App nainštalovaná aj na `claude-setup`). Najjednoduchšie je nechať ho verejné –
nie sú v ňom žiadne tajomstvá, len postupy a pravidlá.

## Úpravy

- Preferencie: `plugins/core/context/preferencie.md`
- Postupy: `plugins/core/skills/*/SKILL.md`
- Agenti: `plugins/core/agents/*.md`
- Observer: `plugins/core/learning/config.json` (`enabled`, interval, min. počet pozorovaní)
- Dočasne vypnúť pozorovanie: `touch ~/.local/share/ecc-homunculus/disabled`

Po úprave zvýš `version` v `plugins/core/.claude-plugin/plugin.json`, aby sa aktualizácia prejavila.

## Licencia

MIT. Časti odvodené z ECC (Copyright (c) 2026 Affaan Mustafa, MIT) – pozri `LICENSE`
a `plugins/core/learning/LICENSE-ECC`. Jediná zmena vo vendorovanom kóde: `learning/hooks/observe.sh`
pozoruje aj cloud sessions (`remote*`) a JetBrains.

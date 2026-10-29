---
name: add-feature
description: Nová funkcia od začiatku do konca – prieskum, plán na schválenie, implementácia cez testy, review a commit po overení. Použi, keď používateľ chce schopnosť, ktorá ešte neexistuje („pridaj“, „sprav“, „implementuj“, „chcem aby to vedelo“, „nová stránka / tlačidlo / report“).
---

# add-feature

Tenký obal nad skillom `pipeline` (prečítaj ho). Prevzaté z ECC `orch-add-feature` (MIT).

## Kedy

- Schopnosť, ktorá **ešte neexistuje**.
- Nie oprava (`fix-bug`) a nie zmena existujúceho správania (`change-feature`).

## Nastavenie

- **Predvolená veľkosť:** štandardná – prieskum aj plán, pokiaľ nie je zjavne malá.
- **Fázy:** 0 → 1 → 2 → 4 → 5 → 6. Malé funkcie sa zúžia na 4 → 5 → 6.
- **Prvý krok fázy 4:** napíš **nové testy, ktoré zlyhajú**, pre nové správanie, potom implementuj do zelena.

## Postup

1. Ujasni si cieľ a kritériá hotovo. Nejasnosti zhrň do otázok – radšej jedna otázka navyše než zlá funkcia.
2. Prieskum (`code-explorer`): kam to v kóde patrí, čo sa dá znovupoužiť. Krátko over,
   či neexistuje hotové riešenie (natívne API prehliadača, štandardná knižnica, overená knižnica).
3. Plán (`planner`) → **BRÁNA 1**.
4. Každý krok plánu cez `tdd-guide` (red → green → refactor).
5. Review (`code-reviewer`, pri bezpečnostnom spúšťači aj `security-reviewer`).
6. Overenie v reálnej aplikácii → **BRÁNA 2** – commit `feat: ...` a push po overení.

Ak funkcia mení formát uložených dát (napr. IndexedDB schéma), plán musí obsahovať migráciu
existujúcich dát a test, že staré dáta po migrácii fungujú.

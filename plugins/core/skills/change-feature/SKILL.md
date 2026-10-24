---
name: change-feature
description: Zmena existujúcej funkčnej vlastnosti na nové požadované správanie – najprv upraviť testy na novú špecifikáciu, potom kód, review a commit po potvrdení. Použi, keď to nie je pokazené, ale má sa to správať inak („zmeň“, „uprav“, „namiesto X nech robí Y“, „nech to ešte aj…“).
---

# change-feature

Tenký obal nad skillom `pipeline` (prečítaj ho). Prevzaté z ECC `orch-change-feature` (MIT).

## Kedy

- Funkcia **funguje**, ale požadované správanie je iné.
- Nie je pokazená → nie `fix-bug`. Nie je nová → nie `add-feature`.

## Nastavenie

- **Predvolená veľkosť:** malá – väčšina úprav je funkcia-dve.
- **Fázy:** 0 → (1 len ak nové správanie treba preskúmať) → 2 ľahko → 4 → 5 → 6.
- **Prvý krok fázy 4:** uprav **existujúce testy** tak, aby vyjadrovali nové správanie (budú zlyhávať),
  potom zmeň implementáciu, kým neprejdú. Zmena testov ako prvá odlišuje úpravu od opravy.

## Postup

1. Zhrň „predtým → potom“ jednou vetou pre každý dotknutý prípad.
2. Nájdi existujúce testy a miesta, ktoré na starom správaní závisia (`code-explorer` pri väčšom zásahu).
3. Plán len pri štandardnej a väčšej veľkosti → **BRÁNA 1** (stačí ukázať, ako sa zmenia testy).
4. Testy → kód (`tdd-guide`) → review → overenie → **BRÁNA 2** – commit `feat:` alebo `refactor:` podľa povahy.

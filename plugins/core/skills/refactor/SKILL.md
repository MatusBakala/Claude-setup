---
name: refactor
description: Refaktor bez zmeny správania – overiť zelené testy, preštruktúrovať po malých krokoch, testy stále zelené, review a commit po potvrdení. Použi, keď sa má zlepšiť štruktúra, ale správanie sa meniť nesmie („uprac“, „rozdeľ súbor“, „odstráň duplicitu“, „mŕtvy kód“, „refaktor“).
---

# refactor

Tenký obal nad skillom `pipeline` (prečítaj ho). Prevzaté z ECC `orch-refine-code` (MIT).

## Kedy

- Rovnaké správanie, **lepšia štruktúra**: vyčlenenie modulu, odstránenie duplicity alebo mŕtveho kódu,
  menej vnorenia, lepšie názvy.
- Ak sa má správanie zmeniť čo i len trochu, toto je zlý postup → `change-feature` / `fix-bug`.

## Nastavenie

- **Predvolená veľkosť:** štandardná.
- **Fázy:** 0 → 2 (plán preštruktúrovania) → 4 → 5 → 6. Nové testy správania sa nepíšu – existujúca sada je záchranná sieť.
- **Prvý krok fázy 4:** over, že relevantné testy existujú a sú **zelené ešte pred zásahom**.
  Ak je pokrytie slabé, najprv dopíš charakterizačné testy (zachytia súčasné správanie, aj keby bolo zvláštne).

## Postup

1. Zelené testy pred začiatkom (výstup ukáž).
2. Plán (`planner`) → **BRÁNA 1**.
3. Malé kroky, po každom spusti testy. Žiadne „popri tom opravím aj…“ – chyby nájdené počas
   refaktoru zapíš a rieš zvlášť cez `fix-bug`.
4. Review (`code-reviewer`) so zameraním na to, že diff je behaviorálne neutrálny.
5. **BRÁNA 2** – commit `refactor: ...` po potvrdení.

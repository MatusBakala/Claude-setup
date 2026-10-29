---
name: fix-bug
description: Oprava chyby – reprodukovať ju testom, ktorý zlyhá, opraviť do zelena, review a commit po overení. Použi vždy, keď je niečo pokazené – zlý výsledok, chyba v konzole, pád, regresia („nefunguje“, „hádže chybu“, „zle počíta“, „bug“, „fix“).
---

# fix-bug

Tenký obal nad skillom `pipeline` (prečítaj ho). Prevzaté z ECC `orch-fix-defect` (MIT).

## Kedy

- Niečo je **pokazené**: zlý výstup, chyba, pád, regresia.
- Ak to funguje správne, ale má sa to správať inak → `change-feature`.
- Ak funkcia ešte neexistuje → `add-feature`.

## Nastavenie

- **Predvolená veľkosť:** malá (často drobná).
- **Fázy:** 0 → (1 len ak príčina nie je zjavná) → (2 ľahko, len pri štandardnej a väčšej) → 4 → 5 → 6.
- **Prvý krok fázy 4:** napíš **nový test, ktorý chybu reprodukuje a zlyhá**. Až potom oprava
  do zelena. Dôkaz, že chyba existuje, je to, čo odlišuje opravu od zmeny.

## Postup

1. Zisti presné symptómy: čo sa deje, čo sa malo diať, kroky na reprodukciu, chybová hláška.
   Ak chýbajú, opýtaj sa – alebo si chybu reprodukuj sám.
2. Pri nejasnej príčine pošli `code-explorer` vystopovať tok. Hľadaj **príčinu**, nie len miesto,
   kde sa prejaví. Skontroluj, či rovnaká chyba nie je aj na iných miestach.
3. Regresný test (RED) → oprava (GREEN) → upratanie.
4. Review (`code-reviewer`, pri bezpečnostnom spúšťači aj `security-reviewer`).
5. Over v reálnej aplikácii, ak sa dá. **BRÁNA 2** – commit `fix: ...` a push po overení.
6. Ak bola príčina netriviálna, navrhni `/poucenia`.

Ak test reprodukovať nejde (napr. čisto vizuálna chyba), povedz to a over ručne / screenshotom.

## Príklad

```
fix-bug: P&L v journale ukazuje NaN pri obchode bez poplatku
→ test: calcPnl({fee: undefined}) očakáva číslo → RED
→ oprava default fee = 0 → GREEN → review → overenie v prehliadači
→ commit fix: [BRÁNA 2]
```

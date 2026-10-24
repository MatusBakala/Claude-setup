---
name: tdd
description: Test-first vývoj (red → green → refactor) a ako rozbehnúť testy v projektoch bez frameworku – vanilla JS v prehliadači, Node, Python. Použi pri písaní testov, keď projekt ešte testy nemá, alebo keď to vyžaduje fáza implementácie pracovného postupu.
---

# TDD

Skrátená a prispôsobená verzia ECC `tdd-workflow` (MIT).

## Cyklus

1. **RED** – test popisuje očakávané správanie. Spusti ho a over, že zlyhá **zo správneho dôvodu**
   (assertion, nie preklep alebo chýbajúci import).
2. **GREEN** – minimálny kód, aby test prešiel.
3. **REFACTOR** – uprac názvy a duplicitu, testy ostávajú zelené.
4. Pred odovzdaním spusti celú relevantnú sadu.

Testuj **správanie** (vstup → výstup, efekt na dáta), nie vnútorné detaily.

## Projekt ešte nemá testy

Nezavádzaj ťažký framework bez súhlasu. Preferuj nástroje, ktoré už sú k dispozícii:

### Vanilla JS (bez build kroku, napr. Trading Journal)

- Logiku (výpočty, parsovanie, transformácie) drž v **čistých funkciách** v ES moduloch, oddelene od DOM.
  Ak sú zamiešané v DOM kóde, pri prvej zmene ich vyčleň (to je malý refaktor – povedz to).
- Testy pre čisté funkcie: vstavaný **`node:test`** + `node:assert/strict`, bez inštalácie:
  ```js
  // tests/pnl.test.js
  import { test } from 'node:test';
  import assert from 'node:assert/strict';
  import { calcPnl } from '../js/pnl.js';

  test('poplatok chýba → počíta sa ako 0', () => {
    assert.equal(calcPnl({ entry: 100, exit: 110, qty: 1 }), 10);
  });
  ```
  Spustenie: `node --test tests/` (ak `package.json` chýba alebo nemá `"type": "module"`, použi
  príponu `.mjs` alebo pridaj minimálny `package.json` s `{"type": "module"}` – povedz to).
- IndexedDB v Node: knižnica `fake-indexeddb` (len so súhlasom), alebo vrstvu úložiska oddeľ za
  malé rozhranie a v testoch ju nahraď objektom v pamäti.
- UI a celé toky: Playwright (`require('playwright')`) – otvor stránku, klikni, over výsledok, sprav screenshot.
  Pri čisto vizuálnych zmenách je screenshot dôkazom namiesto unit testu.

### Python (napr. backtesting)

- **pytest**, ak je dostupný; inak vstavaný `unittest` (`python -m unittest`).
- Pre backtesty testuj na **malých ručne vytvorených dátach** s výsledkom, ktorý vieš spočítať
  na papieri (3–10 sviečok), nie na celej histórii.
- Typické pasce: look-ahead bias (signál používa budúcu sviečku), off-by-one pri vstupe na
  ďalšej sviečke, poplatky a slippage, časové zóny a session hranice, delenie nulou pri prázdnych dátach.

## Na čo myslieť (okrajové prípady)

null / undefined / prázdne, hraničné hodnoty, neplatný vstup, chyby úložiska alebo siete, veľké dáta,
diakritika a špeciálne znaky, dátumy a časové zóny, desatinné čísla pri cenách (zaokrúhľovanie, tick size).

## Anti-vzory

- Test, ktorý prejde aj bez zmeny (príliš slabá assertion).
- Testy závislé na sebe navzájom alebo na reálnom externom API.
- Úprava testu len aby prešiel – vždy povedz, prečo sa test mení.

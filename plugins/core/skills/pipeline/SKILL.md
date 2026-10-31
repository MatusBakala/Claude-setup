---
name: pipeline
description: Spoločná kostra pracovných postupov fix-bug, add-feature, change-feature a refactor – určenie veľkosti zmeny, fázy (prieskum, plán, TDD, review, commit), výber agenta, modelu a effortu podľa náročnosti, zadanie pre agenta, úrovne review a dve brány. Načítaj ju vždy, keď beží niektorý z týchto postupov.
---

# Pipeline – spoločná kostra pracovných postupov

Postupy `fix-bug`, `add-feature`, `change-feature` a `refactor` sú tenké obaly. Určia veľkosť,
vyberú fázy z tejto kostry a fázy delegujú na agentov. Ty si orchestrátor: triedíš, zadávaš,
spájaš, overuješ a commituješ.

## Krok 0 – veľkosť zmeny

Rozsah procesu zodpovedá rozsahu zmeny. Vyhodnoť tri signály, vezmi **najvyšší** stupeň
a oznám ho jednou vetou, aby ho používateľ mohol zmeniť:

| Stupeň | Súbory | Nová závislosť / zmena dátového formátu | Nejasnosť návrhu | Fázy |
|--------|--------|------------------------------------------|------------------|------|
| drobná | 1, pár riadkov | nie | žiadna | 4 → 6, bez agentov |
| malá | 1 súbor / funkcia | nie | jasné po prečítaní kódu | (1 ľahko) → 4 → 5 → 6 |
| štandardná | 2–5 súborov | možno nový interný modul | jedno reálne rozhodnutie | 1 → 2 → 4 → 5 → 6 |
| veľká | veľa / naprieč projektom | externá závislosť, zmena formátu uložených dát, verejné API | viac otvorených otázok | 1 → 2 → vlny → 7, podľa `dlhy-projekt.md` |

Čokoľvek, čo sa dotýka bezpečnostného spúšťača (nižšie) alebo formátu uložených dát
(IndexedDB schéma, formát exportu, súbory), je **minimálne štandardná**.

## Fázy

- **0. Zadanie** – zopakuj požiadavku jednou-dvoma vetami.
- **1. Prieskum** – hľadanie miesta v kóde → `hladac`; vystopovanie toku a vzorov → `code-explorer`.
  Pri novej funkcii krátko over, či neexistuje hotové riešenie (knižnica, natívne API).
- **2. Plán** – `architect`: rozhrania, časti s vlastníctvom súborov a zoznamom na čítanie, pri veľkej
  zmene vlny. Brief mu daj s výslovným zoznamom súborov a sekcií. → **BRÁNA 1**
- **4. Implementácia (TDD)** – `implementer`, jedna časť plánu = jedno zadanie = jeden commit.
  Pri rozbitom builde / prostredí → `build-error-resolver`.
- **5. Review** – podľa sekcie Review nižšie.
- **6. Overenie a commit** – spusti testy a ak sa dá, aj aplikáciu / skript (pozri sa na výsledok,
  nie len na exit kód). Conventional commits (`fix:`, `feat:`, `refactor:` …), jeden logický celok
  na commit. → **BRÁNA 2**
- **7. Finálne review a PR** – len pri vetve s viacerými vlnami, podľa sekcie Review.
- **8. Poučenie** – ak sa počas práce niečo naučilo (oprava od používateľa, netriviálna príčina
  chyby, slepá ulička), navrhni `/poucenia`. Nespúšťaj ho sám.

Agenti sú z pluginu core; v zozname agentov môžu byť s predponou (`core:implementer`).

## Kto, akým modelom a s akým effortom

Model a effort agenta **smieš pri volaní zmeniť**, ale len podľa tejto tabuľky. Predvolené hodnoty
sú v hlavičke agenta; meň ich, len keď náročnosť konkrétnej úlohy patrí do iného riadku.

| Náročnosť úlohy | Agent | Model · effort |
|-----------------|-------|----------------|
| deterministická (testy, počty, hromadné nahradenie) | žiadny – skript / Bash | – |
| nájsť, kde niečo je | `hladac` | Haiku · high |
| rozbitý build / prostredie | `build-error-resolver` | Sonnet · low |
| bežná časť, review vlny, vystopovanie toku | `implementer`, `code-reviewer`, `code-explorer` | Sonnet · medium |
| zložitejšia, ale jasne zadaná časť; bezpečnosť | `implementer`, `security-reviewer` | Sonnet · high |
| plán štandardnej zmeny; ťažká logika (peniaze / riziko, migrácia, súbežnosť) | `architect`, `implementer` | Opus · medium |
| plán veľkej zmeny; finálne review so spúšťačom | `architect`, `code-reviewer` | Opus · high |
| architektúra novej aplikácie (zriedka) | `architect` | Opus · xhigh |

- Náročnosť časti určuje plán: `routine` → bežná, `tricky` → zložitejšia, `hard` → ťažká logika.
  Pri malej zmene bez plánu ju určíš ty.
- **Effort implementera (Sonnet) určuješ ty**, medium alebo high. Anthropic pre Sonnet 5.5 odporúča
  medium pre presne zadané agentické kódovanie a high pre ťažšie alebo dlhšie úlohy. Preto:
  - **medium** – časť je presne zadaná (súbory, rozhranie, testy) v známom kóde,
  - **high** – časť je `tricky`, dlhšia (8+ úprav alebo 3+ súbory), v neznámom kóde, s nejasnými
    okrajovými prípadmi, alebo projekt má v `PLAN.md` náročnosť „zložitý“ (high je potom predvolený
    pre všetky jeho časti),
  - opakovanie po slabom výsledku na medium → high, ďalší stupeň → Opus medium.
- **Eskalácia:** slabý alebo zlý výsledok → zopakuj úlohu raz o stupeň vyššie. Druhé zlyhanie →
  pozri sa na to sám alebo sa opýtaj používateľa.
- Drobnosť urob sám. Delegovanie sa oplatí, len keď agent ušetrí viac čítania, než stojí jeho zadanie.

## Zadanie pre agenta

Agent nevidí konverzáciu ani preferencie – vie len to, čo je v zadaní. Pre `implementer` vždy:

```
Cieľ:        <jedna veta>
Báza:        <vetva + commit, z ktorého vychádza; pri worktree povinné>
Čítaj:       <súbory a rozsahy riadkov>
Upravuj:     <súbory, ktoré časť vlastní>
Nemeň:       nič iné – ak treba, zastav a napíš BLOCKED
Rozhranie:   <signatúry / tvar dát, aby nemusel čítať iné moduly>
Testy:       <čo majú dokázať>
Hotovo keď:  testy zelené, 1 commit „<správa>“
Výstup:      formát Report z agenta implementer
```

Nástroj Agent nemá povinné polia, preto šablónu vynúti hook `scripts/brief-check.py`: bez riadkov
Cieľ, Čítaj, Upravuj, Testy, Hotovo keď (a pri `isolation: worktree` bez Bázy s commitom) volanie
implementera zablokuje s dôvodom. Doplň chýbajúce riadky a zavolaj znova – neobchádzaj ho.

Ostatní agenti dostanú aspoň cieľ, presný rozsah (súbory / diff `base..head`) a čo majú vrátiť.

Po návrate:

- **Commit je odovzdanie, nie zhrnutie.** „Hotovo“ bez commitu = nehotovo; zadaj znova s tým, čo už existuje.
  Hook pri zastavení implementera bez `commit: <sha>` alebo `BLOCKED` ho raz vráti do práce; ak sa
  vráti znova bez commitu, je to na tebe.
- Over `git diff --stat <báza>..<commit>` proti zoznamu „Upravuj“. Zmena mimo neho = vráť alebo vysvetli.
- Celý diff implementera nečítaj; stačí stat, testy a nálezy review. Vážny nález over na `súbor:riadok`.
- `BLOCKED` vyrieš ty (doplň zadanie, rozhodni, prípadne sa opýtaj používateľa) a zadaj znova.

## Review

1. **Malá a štandardná zmena / každá vlna:** `code-reviewer` (Sonnet medium) nad diffom pred commitom
   (pri vlnách po spojení vlny, pred ďalšou vlnou).
2. **Finálne review pred PR** – len pri vetve s 2+ vlnami (pri jednej vlne je review vlny finálne):
   - **Opus · high**, ak platí aspoň jeden spúšťač – a ten jednou vetou pomenuj
     („Opus review: mení IndexedDB schému“). Bez pomenovaného spúšťača Opus nespúšťaj.
     1. zmena formátu uložených dát alebo migrácia (IndexedDB, export, súbory)
     2. výpočty peňazí alebo rizika (P&L, veľkosť pozície, metriky backtestu)
     3. bezpečnostný spúšťač
     4. rozhranie, ktoré používajú iné moduly alebo projekty
     5. asynchrónnosť / súbežnosť
     6. veľká vetva: diff > ~800 riadkov alebo 3+ vlny
   - inak **Sonnet · medium**.
3. **`security-reviewer`** (Sonnet high) paralelne vždy, keď diff zasahuje bezpečnostný spúšťač.

Nálezy CRITICAL/HIGH over, daj opraviť (implementer s tým istým rozsahom) a review zopakuj.
Review nerob sám čítaním celého diffu – agent má čerstvé oči a tvoj kontext ostane čistý.

## Dve brány

1. **BRÁNA 1 – po novom pláne.** Ukáž plán a nepíš implementáciu, kým ho používateľ neschváli.
   Pri pokračovaní v už schválenom pláne (PLAN.md) nečakaj, pýtaj sa len na rozhodnutia, ktoré sú jeho.
2. **BRÁNA 2 – commit po overení.** Keď sú testy zelené a review bez blokujúcich nálezov,
   commitni a pushni bez čakania na potvrdenie; potom ukáž zhrnutie diffu a výsledok overenia.

Medzi bránami pracuj bez zastavovania. Ak si používateľ výslovne vypýta „sprav to celé bez pýtania“,
brány preskoč a na konci podaj súhrn.

## Projektoví agenti majú prednosť

Ak projekt má v `.claude/agents/` vlastného agenta s rovnakou rolou, použi jeho – je šitý na mieru.
Zadanie podľa šablóny vyššie mu daj aj tak.

| Rola | Plugin core | Typický projektový ekvivalent |
|------|-------------|-------------------------------|
| hľadanie v kóde | `hladac` | `hladac-kodu` |
| prieskum toku | `code-explorer` | – |
| plán / architektúra | `architect` | `architekt` |
| implementácia | `implementer` | `implementer` |

## Bezpečnostný spúšťač

Diff zasahuje: vstup od používateľa alebo importované súbory, vkladanie HTML do stránky, volania
externých API, API kľúče / tajomstvá, prácu so súbormi a cestami, spúšťanie príkazov,
prihlasovanie / oprávnenia, databázové dotazy.

## Kontrola na konci

- veľkosť bola oznámená a sedela s prácou
- každý agent dostal model / effort podľa tabuľky; Opus review malo pomenovaný spúšťač
- obe brány boli dodržané (alebo výslovne zrušené používateľom)
- `security-reviewer` bežal práve vtedy, keď bol dotknutý spúšťač
- nové / zmenené správanie má testy; testy prechádzajú
- čo nebolo overené, je povedané nahlas

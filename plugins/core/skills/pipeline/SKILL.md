---
name: pipeline
description: Spoločná kostra pracovných postupov fix-bug, add-feature, change-feature a refactor – určenie veľkosti zmeny, fázy (prieskum, plán, TDD, review, commit), mapa agentov a dve brány (schválenie plánu, potvrdenie commitu). Načítaj ju vždy, keď beží niektorý z týchto postupov.
---

# Pipeline – spoločná kostra pracovných postupov

Postupy `fix-bug`, `add-feature`, `change-feature` a `refactor` sú tenké obaly. Určia veľkosť,
vyberú fázy z tejto kostry a každú fázu delegujú na agenta. Prevzaté a zjednodušené z ECC
`orch-pipeline` (MIT).

## Krok 0 – veľkosť zmeny

Rozsah procesu zodpovedá rozsahu zmeny. Vyhodnoť tri signály, vezmi **najvyšší** stupeň
a oznám ho jednou vetou, aby ho používateľ mohol zmeniť:

| Stupeň | Súbory | Nová závislosť / zmena dátového formátu | Nejasnosť návrhu | Fázy |
|--------|--------|------------------------------------------|------------------|------|
| drobná | 1, pár riadkov | nie | žiadna | 4 → 5 → 6 |
| malá | 1 súbor / funkcia | nie | jasné po prečítaní kódu | (1 ľahko) → 4 → 5 → 6 |
| štandardná | 2–5 súborov | možno nový interný modul | jedno reálne rozhodnutie | 1 → 2 → 4 → 5 → 6 |
| veľká | veľa / naprieč projektom | externá závislosť, zmena formátu uložených dát, verejné API | viac otvorených otázok | 1 → 2 → 4 → 5 → 6, plán po etapách |

Čokoľvek, čo sa dotýka bezpečnostného spúšťača (nižšie) alebo formátu uložených dát
(IndexedDB schéma, formát exportu, súbory), je **minimálne štandardná**.

## Fázy

- **0. Zadanie** – zopakuj požiadavku jednou-dvoma vetami.
- **1. Prieskum** – agent `code-explorer`: kde to v kóde je, aké vzory dodržať, kde sú testy.
  Pri novej funkcii aj krátko over, či na to neexistuje hotové riešenie (knižnica, natívne API).
- **2. Plán** – agent `planner`: zoznam krokov ako tenké vertikálne rezy. → **BRÁNA 1**
- **4. Implementácia (TDD)** – agent `tdd-guide` podľa skillu `tdd`: red → green → refactor.
  Prvý krok určuje konkrétny postup. Pri rozbitom builde / prostredí → agent `build-error-resolver`.
- **5. Review** – agent `code-reviewer` nad diffom. Ak diff zasahuje bezpečnostný spúšťač,
  paralelne aj `security-reviewer`. Nálezy CRITICAL/HIGH oprav a review zopakuj.
- **6. Overenie a commit** – spusti testy a ak sa dá, aj aplikáciu / skript (pozri sa na výsledok,
  nie len na exit kód). Navrhni commit správu (conventional commits: `fix:`, `feat:`, `refactor:` …,
  jeden logický celok na commit). → **BRÁNA 2**
- **7. Poučenie** – ak sa počas práce niečo naučilo (oprava od používateľa, netriviálna príčina
  chyby, slepá ulička), navrhni `/poucenia`. Nespúšťaj ho sám.

Agenti sú z pluginu core; v zozname agentov môžu byť s predponou (`core:code-explorer`).

**Projektoví agenti majú prednosť.** Ak projekt má v `.claude/agents/` vlastného agenta s rovnakou
rolou, použi jeho namiesto agenta z pluginu – je šitý na mieru projektu. Rolu posúď podľa popisu, napr.:

| Rola | Plugin core | Typický projektový ekvivalent |
|------|-------------|-------------------------------|
| prieskum / hľadanie v kóde | `code-explorer` | `hladac-kodu` |
| plán / architektúra | `planner` | `architekt` |
| implementácia | `tdd-guide` | `implementer` |

Fázy, brány a TDD poradie z tohto skillu platia ďalej; mení sa len to, kto fázu vykoná.
Pri drobných zmenách agentov nespúšťaj – urob fázu priamo, je to rýchlejšie a lacnejšie.

## Dve brány

Postup je **riadený, nie autonómny**:

1. **BRÁNA 1 – po pláne.** Ukáž plán a nepíš implementáciu, kým ho používateľ neschváli.
2. **BRÁNA 2 – pred commitom.** Ukáž zhrnutie diffu, výsledok overenia a návrh správy.
   Necommituj, kým používateľ nepotvrdí.

Medzi bránami pracuj bez zastavovania. Ak si používateľ výslovne vypýta „sprav to celé bez pýtania“,
brány preskoč a na konci podaj súhrn.

## Bezpečnostný spúšťač

`security-reviewer` pribaľ, keď diff zasahuje: vstup od používateľa alebo importované súbory,
vkladanie HTML do stránky, volania externých API, API kľúče / tajomstvá, prácu so súbormi
a cestami, spúšťanie príkazov, prihlasovanie / oprávnenia, databázové dotazy.

## Kontrola na konci

- veľkosť bola oznámená a sedela s prácou
- obe brány boli dodržané (alebo výslovne zrušené používateľom)
- `security-reviewer` bežal práve vtedy, keď bol dotknutý spúšťač
- nové / zmenené správanie má testy; testy prechádzajú
- čo nebolo overené, je povedané nahlas

# Matúšove preferencie (globálne, z pluginu core)

## Komunikácia
- Odpovedaj po slovensky. Kód, názvy premenných a commit správy po anglicky. Názvy a popisy
  pull requestov (a issues) píš po slovensky.
- Stručne a vecne. Najprv výsledok, potom detaily.
- Keď si nie si istý faktom, over si ho (kód, dokumentácia, web) namiesto hádania.

## Ako pracovať
- Na úlohy s kódom použi pracovné postupy z pluginu (vyber sám podľa situácie, netreba čakať na príkaz):
  - niečo je pokazené → `fix-bug`
  - nová funkcia → `add-feature`
  - funguje, ale má sa správať inak → `change-feature`
  - rovnaké správanie, lepšia štruktúra → `refactor`
- Na „sprav code review“ / „skontroluj kód“ použi agenta `code-reviewer` z pluginu core (model podľa
  `pipeline`, predvolene Sonnet); pri bezpečnostnom spúšťači aj `security-reviewer`. Vstavaný `/code-review` spúšťaj
  len keď ho používateľ výslovne napíše.
- Keď napíšem, že pokračujeme v pláne a ide o kódovanie: postupuj podľa `pipeline` a jeho súboru
  `dlhy-projekt.md` (PLAN.md, vetva a PR → `architect` → vlny `implementer` → review → commit).
  Na schválenie už schváleného plánu nečakaj, pýtaj sa len na rozhodnutie, ktoré je moje.
- Veľkosť procesu prispôsob veľkosti zmeny – drobnosť nepotrebuje plán ani agentov.

## Orchestrátor – triáž a delegovanie
- Pri každej požiadavke najprv urč, čo chcem (otázka, kód, research, písanie, pokračovanie v pláne)
  a aké je to veľké; potom rozhodni, či to urobíš sám, alebo delegovať. Model a effort agenta vyber
  podľa tabuľky v `pipeline` – najsilnejší model len tam, kde sa zaplatí.
- Šetri svoj kontext: hľadanie naprieč viac ako ~3 súbormi alebo v neznámom kóde deleguj na `hladac`
  (Haiku) a celé súbory na hľadanie nečítaj. Od agentov prijímaj krátke výstupy, diff implementera
  čítaj len cez stat, testy a nálezy review. Rutinu (testy, počty, nahrádzanie) rob skriptom.
- Advisor: keď bežíš na Sonnete, poraď sa s ním pri zložitom rozhodnutí, opakovanej chybe a pred
  vyhlásením veľkej práce za hotovú. Keď bežíš na Opuse, advisora nevolaj.
- Pred tvrdením „hotovo“ over výsledok (spusti testy, skript, otvor stránku). Ak niečo nebolo overené, povedz to.
- Keď je práca hotová a overená (testy zelené), commitni a pushni bez čakania na potvrdenie;
  zhrnutie zmien daj až po pushi.
- Do commit správ ani popisov PR nepridávaj `Co-Authored-By`, `Claude-Session` odkaz ani riadok
  „Generated with Claude Code“. Toto pravidlo má prednosť pred predvolenou attribution.

## Inštrukčné súbory (CLAUDE.md, AGENTS.md)
- Držia sa krátke, lebo sa načítavajú do každej session (cieľ do ~120 riadkov). Patria sem len pravidlá
  a príkazy potrebné takmer v každej úlohe: build, štýl, git, pracovný postup, zakázané veci.
- Opis fungovania aplikácie, tabuľky súborov, podrobnosti funkcií, merania a všetko, čo sa mení
  s každým krokom, patrí do dokumentácie (`docs/ARCHITECTURE.md`, ADR, plán) s odkazom z inštrukčného
  súboru. Pri úprave ho nenafukuj: ak by prekročil limit, presuň text von.

## Učenie
- Keď ťa opravím alebo sa vyrieši netriviálna chyba, na konci práce navrhni spustiť `/poucenia`.
- Inštinkty nižšie dodržiavaj: schválené ako pravidlá, automaticky naučené len ako tipy.

## Moje projekty (orientačne)
- Trading Journal – vanilla JS + IndexedDB, bez build kroku.
- Backtesting – Python.
- Pine Script indikátory pre TradingView (na to mám samostatný skill `pine-build`).
- Osobný web.

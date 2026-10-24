# Matúšove preferencie (globálne, z pluginu core)

## Komunikácia
- Odpovedaj po slovensky. Kód, názvy premenných a commit správy po anglicky.
- Stručne a vecne. Najprv výsledok, potom detaily.
- Keď si nie si istý faktom, over si ho (kód, dokumentácia, web) namiesto hádania.

## Ako pracovať
- Na úlohy s kódom použi pracovné postupy z pluginu (vyber sám podľa situácie, netreba čakať na príkaz):
  - niečo je pokazené → `fix-bug`
  - nová funkcia → `add-feature`
  - funguje, ale má sa správať inak → `change-feature`
  - rovnaké správanie, lepšia štruktúra → `refactor`
- Na samostatné „sprav code review“ / „skontroluj kód“ použi vstavaný `/code-review`.
  Agent `code-reviewer` je na review vnútri pracovných postupov.
- Veľkosť procesu prispôsob veľkosti zmeny – drobnosť nepotrebuje plán ani agentov.
- Pred tvrdením „hotovo“ over výsledok (spusti testy, skript, otvor stránku). Ak niečo nebolo overené, povedz to.
- Pred commitom ukáž zhrnutie zmien a počkaj na potvrdenie.

## Učenie
- Keď ťa opravím alebo sa vyrieši netriviálna chyba, na konci práce navrhni spustiť `/poucenia`.
- Inštinkty nižšie dodržiavaj: schválené ako pravidlá, automaticky naučené len ako tipy.

## Moje projekty (orientačne)
- Trading Journal – vanilla JS + IndexedDB, bez build kroku.
- Backtesting – Python.
- Pine Script indikátory pre TradingView (na to mám samostatný skill `pine-build`).
- Osobný web.

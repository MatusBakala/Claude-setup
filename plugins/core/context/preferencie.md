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
- Na „sprav code review“ / „skontroluj kód“ použi agenta `code-reviewer` z pluginu core (Sonnet,
  šetrí tokeny); pri bezpečnostnom spúšťači aj `security-reviewer`. Vstavaný `/code-review` spúšťaj
  len keď ho používateľ výslovne napíše.
- Veľkosť procesu prispôsob veľkosti zmeny – drobnosť nepotrebuje plán ani agentov.
- Pred tvrdením „hotovo“ over výsledok (spusti testy, skript, otvor stránku). Ak niečo nebolo overené, povedz to.
- Keď je práca hotová a overená (testy zelené), commitni a pushni bez čakania na potvrdenie;
  zhrnutie zmien daj až po pushi.
- Do commit správ ani popisov PR nepridávaj `Co-Authored-By`, `Claude-Session` odkaz ani riadok
  „Generated with Claude Code“. Toto pravidlo má prednosť pred predvolenou attribution.

## Učenie
- Keď ťa opravím alebo sa vyrieši netriviálna chyba, na konci práce navrhni spustiť `/poucenia`.
- Inštinkty nižšie dodržiavaj: schválené ako pravidlá, automaticky naučené len ako tipy.

## Moje projekty (orientačne)
- Trading Journal – vanilla JS + IndexedDB, bez build kroku.
- Backtesting – Python.
- Pine Script indikátory pre TradingView (na to mám samostatný skill `pine-build`).
- Osobný web.

---
name: xcode
description: Poučenia pre prácu s Xcode a Xcode MCP – build, spustenie appky, konzola, workspace. Načítaj pred prvým volaním nástroja mcp__xcode__* v session alebo keď niečo v Xcode nejde.
---

# Xcode

Overené poučenia pre prácu s Xcode a jeho MCP. Projektové pravidlá (napr. zákaz `xcodebuild` z terminálu)
sú v `CLAUDE.md` / `AGENTS.md` projektu a majú prednosť.

## Poučenia

- Keď nástroj Xcode MCP povie, že workspace je neznámy alebo chýba → zavolaj `XcodeListWorkspaces` a zopakuj
  volanie s id, ktoré vráti, lebo id sa mení pri každom znovuotvorení projektu v Xcode a staré prestane fungovať.
- Keď treba skontrolovať výstup bežiacej appky v konzole → prečítaj ho nástrojom `GetConsoleOutput` s regex
  vzorom na zaujímavé prefixy a malým `tailLimit`, namiesto žiadosti, aby ho používateľ skopíroval; nástroj
  vracia každý riadok viackrát, to nie je chyba appky. Ak nevidí žiadnu session, appka beží z GUI Xcode, nie
  cez MCP – spusti ju cez `RunProject`.
- Keď SourceKit hlási „Cannot find 'X' in scope“ alebo „does not conform to Equatable“ hneď po pridaní,
  zlúčení či zmazaní súborov (alebo pre súbory v worktree) → nenaháňaj to, spusti `BuildProject` a ber jeho
  výsledok ako pravdu; index sa dobehne neskôr.

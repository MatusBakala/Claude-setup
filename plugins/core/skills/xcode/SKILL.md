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

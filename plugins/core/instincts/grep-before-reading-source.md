---
id: grep-before-reading-source
trigger: when locating a function, type or API inside a large source file or an unfamiliar codebase
confidence: 0.7
domain: file-patterns
source: approved
scope: global
---

# Grep before reading source

## Action
Search for the definition with grep first and read only the surrounding lines instead of reading the whole file.

## Evidence
- Observer, clicker sessions October 2026: files of 1 000+ lines (WhiteboardLayout, WhiteboardSketchGeometry) were found faster by grep.

---
id: stage-explicit-paths-before-commit
trigger: when committing while other uncommitted edits are present in the working tree
confidence: 0.7
domain: git
source: approved
scope: global
---

# Stage explicit paths

## Action
Stage only the files of the current change by naming their paths (never git add -A or .), then check git status before committing.

## Evidence
- Observer, clicker sessions with parallel implementer agents October 2026.

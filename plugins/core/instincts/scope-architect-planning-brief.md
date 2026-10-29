---
id: scope-architect-planning-brief
trigger: when spawning an architect or planner subagent to plan a feature step
confidence: 0.7
domain: workflow
source: approved
scope: global
---

# Keep architect planning briefs scoped and cheap

## Action
Give an architect or planner subagent an explicit list of files and doc sections to read, tell it not to read the whole codebase, and ask for a plan of limited length (parts, files per part, tests), because a planning run with a broad brief read everything and used about 270k tokens.

## Evidence
- 29.10.: the user asked whether the architect had read all the code and called a 250k-token planning run too long; the brief named docs but set no limits.

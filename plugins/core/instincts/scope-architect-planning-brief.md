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
Give an architect or planner subagent an explicit list of files and doc sections to read, tell it not to read the whole codebase, and ask for a plan of limited length (parts, files per part, tests), because a broad brief makes the planner read the whole codebase.

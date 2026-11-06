---
id: report-background-subagent-progress
trigger: when a long-running subagent (architect, implementer, reviewer) runs in the background while the user waits for its result
confidence: 0.8
domain: workflow
source: approved
scope: global
---

# Report what a background subagent is doing and at which effort

## Action
When starting a background subagent, tell the user in the chat what it will do (planning, writing code with implementers, testing, review), which model and effort it runs at, and roughly what comes next, so the user does not have to guess from the task list why it takes long.

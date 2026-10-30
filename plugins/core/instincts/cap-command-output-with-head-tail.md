---
id: cap-command-output-with-head-tail
trigger: when running a shell command whose output may be long, such as logs, git history or file listings
confidence: 0.7
domain: workflow
source: approved
scope: global
---

# Cap command output with head or tail

## Action
Pipe potentially long command output through `head`, `tail` or `cut` so only the relevant lines come back.

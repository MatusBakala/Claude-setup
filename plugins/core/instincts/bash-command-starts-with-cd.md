---
id: bash-command-starts-with-cd
trigger: when running a Bash command after an earlier shell call in the same session
confidence: 0.85
domain: workflow
source: approved
scope: global
---

# Bash command starts with cd

## Action
Start every Bash command with an explicit `cd` into the directory it needs, or use absolute paths, because the shell working directory resets between calls.

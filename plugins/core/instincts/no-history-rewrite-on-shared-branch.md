---
id: no-history-rewrite-on-shared-branch
trigger: when a branch the user has checked out on their own computer would need a force push, reset or rebase
confidence: 0.9
domain: git
source: approved
scope: global
---

# Agree before rewriting a shared branch

## Action
Do not force-push, reset or rebase a branch the user already pulled locally; propose the step first and, once agreed, give them the exact commands to sync (e.g. git fetch + git reset --hard origin/<branch>).

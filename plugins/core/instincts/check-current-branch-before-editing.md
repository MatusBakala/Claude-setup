---
id: check-current-branch-before-editing
trigger: when about to edit or commit files in a repository, especially after the user merged pull requests or time has passed since the session started
confidence: 0.8
domain: git
source: approved
scope: global
---

# Check the current branch before editing

## Action
Run `git status -sb` before the first edit or commit of a task, because the branch shown in the session context is a snapshot and the user may have merged or switched branches since, leaving you on main.

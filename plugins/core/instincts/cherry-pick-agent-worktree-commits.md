---
id: cherry-pick-agent-worktree-commits
trigger: when integrating commits made by an implementer agent in its own git worktree into the main checkout
confidence: 0.7
domain: git
source: approved
scope: global
---

# Cherry-pick agent worktree commits one by one without committing

## Action
Take each agent commit with `git cherry-pick --no-commit <commit>` one at a time, resolve conflicts in shared lists (test registration, build file lists) by keeping both sides, and apply any further commit of the same agent separately (`git cherry-pick --quit`, then `git diff <commit>~1 <commit> | git apply --index`), because the sequencer stops when several commits are picked with `--no-commit`.

---
id: check-unmerged-commits-before-deleting-branches
trigger: when cleaning up branches after their pull requests were merged
confidence: 0.8
domain: git
source: approved
scope: global
---

# Look for commits missing from main before deleting a merged branch

## Action
Before deleting a branch whose pull request is merged, run `git cherry -v origin/<base> <branch>`; if it lists commits (a commit pushed after the merge, or one whose patch differs), check their content is in the base and carry over what is missing, because a PR merge does not take later commits.

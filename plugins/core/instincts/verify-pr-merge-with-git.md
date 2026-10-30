---
id: verify-pr-merge-with-git
trigger: when checking whether a pull request is already merged
confidence: 0.7
domain: git
source: approved
scope: global
---

# Verify a PR merge with git

## Action
Do not rely on the `merged` field of the GitHub connector; confirm with `git fetch origin <base>` and `git merge-base --is-ancestor <PR head sha> origin/<base>`.

---
id: gh-pr-body-from-scratch-file
trigger: when creating or editing a pull request with gh and the description is longer than one line or contains diacritics
confidence: 0.8
domain: git
source: approved
scope: global
---

# Pass the pull request body to gh from a scratch file

## Action
Write the pull request description to a file in the session scratchpad with the Write tool, then pass it with `gh pr create -F <file>` (or `gh pr edit --body-file <file>`) instead of an inline body or heredoc, because heredocs are blocked and inline text with diacritics breaks easily.

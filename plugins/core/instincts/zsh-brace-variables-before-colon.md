---
id: zsh-brace-variables-before-colon
trigger: when a zsh command puts a variable right before a colon, such as git show $rev:path
confidence: 0.7
domain: workflow
source: approved
scope: global
---

# Brace zsh variables before a colon

## Action
Write `"${rev}:path"` instead of `$rev:path`, because zsh reads `:l`, `:h`, `:t` and similar after a variable as history modifiers and silently changes the value.

---
id: quote-glob-patterns-in-zsh
trigger: when a zsh command passes a glob such as *.swift to grep --include, ls or a compiler, or globs a directory that may not exist
confidence: 0.7
domain: workflow
source: approved
scope: global
---

# Quote glob patterns in zsh commands

## Action
Quote glob patterns meant for the program (`--include='*.swift'`) and build uncertain file lists with find, because zsh aborts the whole command with "no matches found" when an unquoted pattern matches nothing.

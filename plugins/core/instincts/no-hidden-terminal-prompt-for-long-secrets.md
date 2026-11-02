---
id: no-hidden-terminal-prompt-for-long-secrets
trigger: when a one-off command needs an API key or other long secret from the user
confidence: 0.7
domain: workflow
source: approved
scope: global
---

# Long secrets via clipboard or a hidden macOS dialog

## Action
Never ask for a long secret through a hidden terminal prompt (pasting there fails); read it from the clipboard (`pbpaste`, whitespace stripped) or a hidden-input macOS dialog, and never print or store it.

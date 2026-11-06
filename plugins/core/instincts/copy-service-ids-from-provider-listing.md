---
id: copy-service-ids-from-provider-listing
trigger: when writing an external service ID (voice ID, model ID, resource ID) into a config
confidence: 0.7
domain: workflow
source: approved
scope: global
---

# Copy external IDs from the provider's own listing

## Action
Confirm the ID against the provider's listing for the user's account (or a direct lookup call) and copy it from there, never retype it from memory, before committing or deploying it.

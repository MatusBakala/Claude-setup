---
id: check-test-settings-before-attributing-results
trigger: when explaining a result of a live test the user ran (latency, output quality, behavior) and the app has settings the user can switch, such as answer depth, effort or model
confidence: 0.8
domain: debugging
source: approved
scope: global
---

# Check the test settings before naming a cause

## Action
Before attributing a live test result to a cause, find out which user-changeable settings it ran with (from the log, or ask the user), because a switched mode or model often explains the difference by itself.

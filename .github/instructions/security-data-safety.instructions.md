---
applyTo: "**/*.py,**/*.md,**/*.yml,**/*.yaml,**/*.json"
description: "Use when editing code/docs/config to prevent secrets leakage, customer data exposure, and unsafe logging in publishable repository content."
---

# Security and Data Safety Instructions

- Never commit credentials, API tokens, keys, or secrets.
- Never include customer-identifying data in examples, logs, or release notes.
- Use placeholders such as `example.com` and `Acme Corp`.
- Avoid logging full sensitive payloads.
- Keep messages informative but sanitized.

Before completion:

1. Confirm no secret-like literals were introduced.
2. Confirm any command examples avoid sensitive values.
3. Confirm generated docs/changelog entries are safe to publish.

---
name: "context7-retrieval-patterns"
description: "Use when tasks need latest external library documentation, current API signatures, migration/deprecation guidance, version-sensitive setup decisions, or framework best practices via Context7 MCP."
---

# Skill: Context7 Retrieval Patterns

Use this skill when implementation quality depends on current external library/framework documentation.

## Goals

- Reduce outdated API usage and hallucinated methods.
- Ground implementation guidance in current, version-aware docs.
- Keep retrieval output concise and directly actionable for code edits.

## Trigger Signals

Use when task text contains signals such as:

- "latest docs", "up-to-date", "current API", "breaking change", "migration"
- unknown framework symbols or version-specific behavior
- generated code depends on third-party libraries not fully covered by local repository context
- documentation updates that must reflect latest language/framework guidelines (CSS, HTML, JavaScript, Python, SQL)

## Retrieval Workflow

1. Resolve library identity first (`resolve-library-id`) for each external dependency.
2. Query docs second (`query-docs`) for exact symbols/topics needed by the task.
3. Prefer concise excerpts with examples over large generic dumps.
4. Capture version/freshness indicators where available.
5. Convert findings into implementation constraints and concrete code guidance.

## Tooling Contract

- Always call `resolve-library-id` before `query-docs` unless a valid Context7 library ID is already provided.
- Keep retrieval bounded: ask only task-scoped questions and avoid broad "everything about X" pulls.
- If retrieval quality remains low after focused attempts, report uncertainty and switch to safest conservative guidance.

## Quality Rules

- Keep retrieval scoped to task-relevant symbols or features.
- Prefer authoritative library docs over secondary summaries.
- If results conflict, report uncertainty and propose safest default.
- Do not include secrets in queries, outputs, or logs.

## Output Contract

Return a compact packet that includes:

1. Library/topic resolved
2. Key API facts and constraints
3. Freshness/version cues (if available)
4. Recommended implementation direction for this repository
5. Confidence and any unresolved ambiguities
6. Evidence: library IDs queried and topics asked

## Suggested Validations

- `get_errors` for changed files after implementation.
- Targeted tests for affected behavior when available.

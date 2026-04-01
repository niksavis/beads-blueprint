# Governance Warn-Only Hook

This hook set provides warn-only governance messages during Copilot coding sessions.

## Purpose

- Reinforce safety and quality checks without mutating files.
- Remind agents to follow repository rules for diagnostics, architecture, and data safety.

## Events used

- `sessionStart`
- `userPromptSubmitted`
- `sessionEnd`

## Behavior

- Prints warnings/reminders to the session output.
- Does not modify repository files.
- Does not run commit, push, or release actions.

## Notes

- This is intentionally lightweight for phase-1 rollout.
- Escalation to strict enforcement should be done only after pilot metrics are reviewed.

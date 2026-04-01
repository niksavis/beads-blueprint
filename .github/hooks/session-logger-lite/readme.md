# Session Logger Lite Hook

This is a privacy-preserving partial import of session logging hooks.

## Purpose

- Record session lifecycle events for local audit and usage tracking.
- Avoid storing raw prompt content.

## Events used

- `sessionStart`
- `sessionEnd`

## Behavior

- Writes JSON lines to `logs/copilot/session.log`.
- Does not log prompt bodies.
- Does not modify repository files.

## Notes

- Keep `logs/` ignored in Git.
- If deeper analytics are needed later, add prompt metadata fields only (no full text).

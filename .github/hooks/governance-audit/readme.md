# Governance Audit Hook

This hook pack adds lightweight governance auditing for Copilot sessions.

## Purpose

- Keep a local JSONL audit trail for session lifecycle and prompt scans.
- Flag potential threat signals in user prompts.
- Reinforce final validation checks at session end.

## Events used

- `sessionStart`
- `userPromptSubmitted`
- `sessionEnd`

## Behavior

- Logs events to `logs/copilot/governance/audit.log`.
- Scans prompt text for threat categories when prompt text is available.
- Warns on potential threat patterns; does not block execution.

## Threat categories

- `prompt_injection`
- `credential_exposure`
- `system_destruction`
- `privilege_escalation`
- `data_exfiltration`

## Notes

- This is configured in audit/warn mode for safe rollout.
- Keep `logs/` ignored in Git.
- For strict blocking, use the existing strict governance profile and tighten this hook after pilot results.

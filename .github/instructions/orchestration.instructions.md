---
applyTo: ".github/agents/*.agent.md,.github/prompts/*.prompt.md,.github/skills/**/SKILL.md"
description: "Use when creating orchestration assets: enforce explicit delegation paths, deterministic verification loops, and autonomous non-interactive completion behavior."
---

# Orchestration Authoring Instructions

Apply these rules when creating or updating agents, skills, and prompts used for orchestration.

## Core Requirements

- Define one clear orchestrator/coordinator entrypoint for complex tasks.
- Include explicit delegation criteria for specialist agents/skills.
- Include deterministic verification commands in execution order.
- Define fix-and-recheck loop behavior when checks fail.

## Autonomy Rules

- Default to non-interactive execution for implementation and verification.
- Escalate only for hard blockers (permissions, irreversible decision, external outage).
- If blocked, report blocker + attempted mitigations + minimal next action.

## Discoverability Rules

- Keep `description` fields specific and trigger-rich ("Use when...").
- Use explicit keywords users are likely to type (orchestrator, delegate, quality gates, autonomous).
- Keep frontmatter valid and minimal.

## Validation Rules

Every orchestration asset must reference repository-native deterministic checks:

1. `python scripts/verify_agent_harness.py --strict`
2. `python validate.py --fast`
3. Targeted tests for changed behavior

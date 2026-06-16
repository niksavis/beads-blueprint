---
name: orchestrated-execution
description: "Use when work needs decomposition, multi-step delivery, or delegation across agents: define execution graph, assign specialized subtasks, and run autonomous fix-and-verify loops until done."
---

# Skill: Orchestrated Execution

Use this skill to coordinate complex work with deterministic outcomes.

## When to Use

- User asks for orchestrator/coordinator behavior.
- Task spans multiple files, systems, or quality gates.
- Work benefits from specialist agents with isolated context.
- Completion requires iterative verification and follow-up fixes.

## Core Workflow

1. **Scope and constraints**
   - Capture goals, non-goals, and constraints from the request.
2. **Execution graph**
   - Split work into ordered phases with dependencies.
   - Mark independent tracks for delegation.
3. **Delegation**
   - Assign each track to the best-fit specialist agent or skill.
4. **Integration**
   - Merge changes and resolve cross-track conflicts.
5. **Verification loop**
   - Run deterministic checks.
   - If failures exist, create and execute follow-up fixes.
   - Repeat until checks pass.

## Deterministic Verification Set

Run in this order:

```bash
python scripts/verify_agent_harness.py --strict
python validate.py --fast
python -m pytest -q
```

If a command fails:

- Fix root cause.
- Re-run only affected checks first.
- Re-run the full set before completion.

## Delegation Matrix

| Need | Delegate to |
| --- | --- |
| External API/docs freshness | Docs Retrieval Expert |
| Setup, missing tools, broken environment | Development Environment Bootstrap |
| Final gate and regression safety pass | Repo Quality Guardian |
| Post-stability simplification/debt reduction | Universal Janitor |

## Non-Interactive Delivery Rules

- Continue implementation without asking for confirmation unless a hard blocker exists.
- Prefer reversible, behavior-safe defaults.
- Surface explicit blocker reports only when no safe forward path is available.

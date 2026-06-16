---
name: deterministic-quality-gates
description: "Use when multiple agents need consistent linting, typing, formatting, security, and regression checks: run repository gates in deterministic order and enforce fix-then-recheck behavior."
---

# Skill: Deterministic Quality Gates

Use this skill as the shared quality contract across agents.

## When to Use

- Before declaring implementation complete.
- After cross-agent merges where regressions are likely.
- During autonomous loops that must verify and continue.

## Required Gate Order

1. Harness integrity:

```bash
python scripts/verify_agent_harness.py --strict
```

2. Fast development gates:

```bash
python validate.py --fast
```

3. Targeted behavior validation:

```bash
python -m pytest -q
```

4. Hook integrity (when hooks or setup changed):

```bash
python install_hooks.py --check
```

## Full Hardening Pass (Release or High-Risk Changes)

```bash
python validate.py --full
```

## Fix-and-Recheck Policy

- Do not stop at first green-looking partial result.
- Any failed gate must trigger implementation updates.
- Re-run failed gate, then re-run upstream dependent gates.
- Completion requires all required gates for the task scope to pass.

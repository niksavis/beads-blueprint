---
name: caveman-tooling-update
description: "Use when installing, updating, or verifying JuliusBrussee/caveman in this repository, especially for GitHub Copilot rule wiring and skills-lock refresh. Trigger on phrases like caveman update, refresh caveman, reinstall caveman, copilot caveman install, npx skills add caveman, or npx github:JuliusBrussee/caveman."
---

# Caveman Tooling Update

## When to Use This Skill

- You need to install or update caveman in this repository.
- You ran installer commands and want to verify what changed.
- You need to confirm whether to use npx skills add or the caveman installer.
- You need to commit caveman update artifacts safely.

## Command Selection

Use the command that matches the target agent.

1. GitHub Copilot in this repo:
   npx -y github:JuliusBrussee/caveman -- --only copilot --with-init
2. Agent profiles supported by vercel-labs/skills:
   npx skills add JuliusBrussee/caveman -a PROFILE_SLUG

Guidance:

- For Copilot rule-file wiring in this repo, prefer the installer command with --only copilot --with-init.
- npx skills add is valid for many profile-based agents, but Copilot setup in INSTALL.md is explicitly listed under the installer command path.

## Verification Workflow

1. Inspect changes:
   - git status --short
   - git diff --stat
2. Confirm expected caveman footprint:
   - .agents/skills/caveman*/
   - .agents/skills/cavecrew/
   - skills-lock.json
   - possibly .github/copilot-instructions.md when --with-init updates rule text
3. Validate repository gates in order:
   - python scripts/verify_agent_harness.py --strict
   - python validate.py --fast
   - targeted tests only if behavior changed
4. If lint/type failures are introduced by upstream updates:
   - apply minimal, behavior-preserving fixes
   - re-run validation until clean
5. Commit only after checks pass.

## Commit Guidance

- Use a focused commit with caveman update scope.
- Example subject:
  - chore(caveman): update toolkit assets
- Include only caveman-related files in this commit.

## Safety Rules

- Do not bypass validation to force a commit.
- Do not stage unrelated files.
- Do not assume npx skills add covers every agent; verify against INSTALL.md.

## References

- Upstream install guide:
  - https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md

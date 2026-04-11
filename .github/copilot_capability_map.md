# Copilot Capability Map

## Always-On Policy

- .github/copilot-instructions.md
- agents.md (external-agent compatibility shim)

## Core Capability Areas

- Environment bootstrap and recovery:
  - Skill: .github/skills/environment-readiness/SKILL.md
  - Agent: .github/agents/development-environment-bootstrap.agent.md
  - Prompt: .github/prompts/initialize-development-environment.prompt.md

- Greenfield project kickoff and scaffolding:
  - Prompt: .github/prompts/greenfield-project-kickoff.prompt.md

- Beads issue lifecycle and team sync:
  - Skill: .github/skills/beads-workflow/SKILL.md
  - Instruction: .github/instructions/beads-onboarding.instructions.md
  - Prompt: .github/prompts/start-work-session.prompt.md

- Python quality and review enforcement:
  - Agent: .github/agents/repo-quality-guardian.agent.md
  - Instructions: python-code-quality, review, security-data-safety, testing

- External documentation grounding and API freshness:
  - Agent: .github/agents/docs-retrieval-expert.agent.md
  - Skill: .github/skills/context7-retrieval-patterns/SKILL.md
  - Skills: .github/skills/microsoft-docs/SKILL.md, .github/skills/microsoft-code-reference/SKILL.md

- Decision quality and technical debt cleanup:
  - Agent: .github/agents/critical-thinking.agent.md
  - Agent: .github/agents/universal-janitor.agent.md

- Release flow and changelog:
  - Skill: .github/skills/release-management/SKILL.md
  - Prompt: .github/prompts/release-notes-draft.prompt.md
  - Instruction: .github/instructions/release-workflow.instructions.md

- Dependency hygiene and reproducibility:
  - Instruction: .github/instructions/dependency-management.instructions.md

- CLI discovery and search workflows:
  - Skill: .github/skills/cli-search-tools/SKILL.md
  - Skill: .github/skills/dev-tools-setup/SKILL.md

## Hook Profiles

- Governance reminders: .github/hooks/governance-warn-only/hooks.json
- Release hygiene reminders: .github/hooks/release-hygiene-warn-only/hooks.json
- Session logging: .github/hooks/session-logger-lite/hooks.json
- Governance auditing: .github/hooks/governance-audit/hooks.json

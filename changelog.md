# Changelog

## Unreleased

### Notes

- No unreleased changes yet.

## v1.0.2

Released: 2026-04-02

### v1.0.2 Features

- Added an `environment-readiness` skill to run preflight checks and route setup only when environment checks fail.

### v1.0.2 Improvements

- Reduced always-on instruction context by replacing setup playbooks in `.github/copilot-instructions.md` and `agents.md` with a lightweight readiness gate.
- Updated capability and customization maps to include the new environment-readiness workflow.
- Standardized template release policy as no-tag and aligned release docs/skill guidance with that policy.
- Simplified release automation by removing git-tag creation support from `release.py`.

## v1.0.1

Released: 2026-04-01

### Improvements

- Clarified first-time setup guidance for brand-new developers and AI agents.
- Added explicit AI bootstrap entry points and discovery-friendly task phrases.
- Strengthened instruction, skill, and agent descriptions with `Use when ...` trigger keywords to improve auto-discovery reliability.
- Standardized LF line-ending policy and expanded `.gitignore` coverage to reduce cross-platform Git noise.
- Removed template release-tag guidance and kept template release workflow version-and-changelog only.

## v1.0.0

Released: 2026-04-01

### v1.0.0 Features

- Migrated repository automation to Python-only scripts
- Added one-command development environment initialization
- Added VS Code bash-first terminal defaults across platforms
- Added reusable Copilot instructions, skills, agents, prompts, and hook templates
- Added lightweight GitHub Actions lint/build workflows

### v1.0.0 Improvements

- Removed shell-specific setup scripts and rigid plan template/parser artifacts
- Added managed git hooks and validation script for repeatable quality gates
- Added optional release tagging support (`python release.py <bump> --tag`)

## v0.1.0

Released: 2026-02-08

### v0.1.0 Features

- Initial Beads template with plan-to-beads workflow
- Multi-shell support (PowerShell, bash, Python)
- Plan template with Feature/Task/Subtask hierarchy
- Plan-to-beads parser with parent reference support

### v0.1.0 Improvements

- Bootstrap scripts with automatic OS/architecture detection (Windows, macOS, Linux, FreeBSD; x64, ARM64)
- Project-local tools installation pattern (avoids PATH length limits)
- Detection of existing Beads installations (skip-install option)
- LLM-assisted changelog generation workflow with JSON export for agent processing
- Release scripts for version bumping and automated changelog scaffolding

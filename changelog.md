# Changelog

## v0.1.0

*Released: 2026-02-08*

### Features

- Initial Beads template with plan-to-beads workflow
- Multi-shell support (PowerShell, bash, Python)
- Plan template with Feature/Task/Subtask hierarchy
- Plan-to-beads parser with parent reference support

### Improvements

- Bootstrap scripts with automatic OS/architecture detection (Windows, macOS, Linux, FreeBSD; x64, ARM64)
- Project-local tools installation pattern (avoids PATH length limits)
- Detection of existing Beads installations (skip-install option)
- LLM-assisted changelog generation workflow with JSON export for agent processing
- Release scripts for version bumping and automated changelog scaffolding

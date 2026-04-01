---
name: cli-search-tools
description: "Use when asked to search, grep, find files, locate symbol usages, inspect repository structure, or parse JSON/YAML/TOML using rg, fd, jq, and yq across any language or framework."
---

# CLI Search Tools

Four focused tools that cover nearly all read-only codebase exploration and structured data tasks. Prefer these over native shell search commands — they are faster, smarter, and composable.

| Tool | Purpose                      | Best for                                               |
| ---- | ---------------------------- | ------------------------------------------------------ |
| `rg` | Fast regex content search    | Finding where identifiers, strings, or patterns appear |
| `fd` | Fast file/directory finder   | Discovering files by name, extension, or location      |
| `jq` | JSON stream processor        | Parsing, filtering, and transforming JSON data         |
| `yq` | YAML/JSON/XML/TOML processor | Reading and querying structured config files           |

## When to Use This Skill

- Searching for function, class, or variable usages across a codebase
- Finding files by name, extension, or directory pattern
- Parsing `package.json`, `pyproject.toml`, `*.yaml`, or any structured config
- Extracting data from API JSON responses or log files
- Exploring an unfamiliar codebase efficiently before making changes
- Combining search and structured parsing in a pipeline

## Prerequisites

Check availability before use:

```bash
# Git Bash (Windows) / WSL / macOS / Linux
command -v rg && echo "rg installed"
command -v fd || command -v fdfind && echo "fd installed"  # fdfind on Ubuntu/Debian/WSL
command -v jq && echo "jq installed"
command -v yq && echo "yq installed"
```

```powershell
# Windows PowerShell (fallback)
Get-Command rg -ErrorAction SilentlyContinue
Get-Command fd -ErrorAction SilentlyContinue
Get-Command jq -ErrorAction SilentlyContinue
Get-Command yq -ErrorAction SilentlyContinue
```

> **fd binary name by platform**: On Ubuntu/Debian (including WSL), the apt package `fd-find`
> installs the binary as `fdfind`. Shell profiles alias it to `fd`, but agents running
> non-interactive bash/zsh sessions do not inherit those aliases. Use `fdfind` explicitly
> on Linux/WSL, or resolve at runtime (see fd section below).

**Install if missing:**

```bash
# Windows (Git Bash or PowerShell — winget)
winget install BurntSushi.ripgrep.MSVC sharkdp.fd jqlang.jq MikeFarah.yq
```

```bash
# macOS (Homebrew)
brew install ripgrep fd jq yq
```

```bash
# Linux / WSL (Ubuntu/Debian)
sudo apt install ripgrep fd-find jq
pip install yq   # or: brew install yq (if Homebrew on Linux)
```

## Tool Selection Guide

```
Search file CONTENTS for text or pattern?  → rg
FIND files by name, extension, location?   → fd
Query or transform JSON data?              → jq
Query or transform YAML / TOML / XML?      → yq
Find files, then search their contents?    → fd | rg  (or rg with globs)
Search and parse JSON in rg output?        → rg --json | jq
```

---

## rg — Content Search

### Essentials

```bash
rg "pattern"                    # Search all files
rg -i "pattern"                 # Case-insensitive
rg -F "exact.string"            # Fixed string (no regex; faster for literals)
rg -w "word"                    # Whole-word match
rg -l "pattern"                 # List matching filenames only
rg -c "pattern"                 # Count matches per file
rg -C 3 "pattern"               # 3 lines of context around each match
rg -n "pattern"                 # Show line numbers (default; explicit)
```

### Filter by File Type

```bash
rg "pattern" --type py          # Python files
rg "pattern" --type js          # JavaScript
rg "pattern" --type ts          # TypeScript
rg "pattern" --type json        # JSON
rg "pattern" --type yaml        # YAML
rg --type-list                  # List all known type aliases
rg "pattern" -g "*.test.ts"     # Include glob
rg "pattern" -g "!*.test.ts"    # Exclude glob
```

### Scope and Exclusion

```bash
rg "pattern" src/               # Scope to directory
rg "pattern" -g "!node_modules/**"   # Exclude directory
rg "pattern" --hidden           # Include hidden files
rg "pattern" --max-depth 3      # Limit traversal depth
rg "pattern" -L                 # Follow symlinks
```

### Structured Output (for Piping)

```bash
# JSON output — most robust for programmatic consumption
rg "pattern" --json | jq 'select(.type=="match") | .data.path.text'

# Null-delimited filenames — safe for filenames with spaces
rg -l0 "pattern" | xargs -0 wc -l

# No filename prefix (useful in single-file mode)
rg "pattern" --no-filename src/module.py
```

### Code Exploration Patterns

```bash
# All function definitions
rg "^def " --type py
rg "^(export )?function " --type js
rg "^(export )?(async )?function\b" --type ts

# All class definitions
rg "^class " --type py
rg "^(export )?(abstract )?class " --type ts

# All usages of an identifier
rg "\bmyFunction\b"

# All TODO / FIXME comments
rg "TODO|FIXME|HACK|XXX"

# All imports of a specific module
rg "from mymodule import|import mymodule" --type py

# All error / exception handling blocks
rg "except .+:" --type py
rg "catch\s*\(" --type ts
```

---

## fd — File Discovery

### Cross-Platform Binary Name

| Platform                      | Binary   | Install                     |
| ----------------------------- | -------- | --------------------------- |
| Windows (Git Bash/PowerShell) | `fd`     | `winget install sharkdp.fd` |
| macOS (Homebrew)              | `fd`     | `brew install fd`           |
| Linux / WSL (Ubuntu/Debian)   | `fdfind` | `sudo apt install fd-find`  |

**Agent rule**: Do not assume `fd` resolves on Linux/WSL. Resolve the binary at runtime:

```bash
# Safe cross-platform invocation (Git Bash, WSL, Linux, macOS)
FD=$(command -v fd 2>/dev/null || command -v fdfind) && $FD "pattern" dir/
```

Or inline per command:

```bash
$(command -v fd 2>/dev/null || echo fdfind) -e py src/
```

### Essentials

```bash
fd "config"                     # Substring match on filename (smart-case)
fd -e py                        # By extension
fd -e yaml -e yml               # Multiple extensions
fd "\.test\.(ts|js)$"           # Regex pattern
fd -t d "src"                   # Directories only
fd -t f "readme"                # Files only
```

### Scoping and Exclusion

```bash
fd "pattern" src/               # Scope to directory
fd "pattern" --exclude node_modules --exclude .git
fd -H "pattern"                 # Include hidden files
fd "pattern" --max-depth 2      # Limit depth
fd "pattern" --absolute-path    # Output absolute paths
```

### Output and Piping

```bash
# Execute a command for each result
fd -e py --exec rg "TODO" {}

# Null-delimited output — safe for filenames with spaces
fd -0 "pattern" | xargs -0 wc -l

# Collect results into a list
fd -e json --max-depth 1
```

### Common Discovery Tasks

```bash
# Test files
fd "test_" -e py
fd "\.spec\.(ts|js)$"
fd "\.test\.(ts|js)$"

# Config files at repo root
fd -e yaml -e yml -e toml -e json --max-depth 2

# All documentation
fd -e md

# Recently modified files (last 7 days)
fd --changed-within 7d

# Large files (over 1 MB)
fd --size +1mb
```

---

## jq — JSON Query

### Essentials

```bash
jq '.'                          # Pretty-print
jq '.field'                     # Top-level field
jq '.parent.child'              # Nested field
jq '.[0]'                       # First array element
jq '.items[]'                   # Iterate array
jq -r '.version'                # Raw string output (strip quotes)
jq -c '.items[]'                # Compact (one object per line)
```

### Filtering and Conditions

```bash
jq '.items[] | select(.status == "active")'
jq '.items[] | select(.id != null)'
jq '.items[] | select(.count > 10)'
jq '.items[] | select(.name | contains("api"))'
```

### Common Repo Tasks

```bash
# package.json
jq '.version' package.json
jq '.dependencies | keys' package.json
jq '.scripts' package.json

# Parse rg --json output
rg "pattern" --json | jq -r 'select(.type=="match") | .data.path.text' | sort -u

# Count matches per file from rg JSON
rg "pattern" --json \
  | jq -r 'select(.type=="match") | .data.path.text' \
  | sort | uniq -c | sort -rn

# Summarize JSON config keys
jq 'keys' file.json
```

### Transformation

```bash
# Project/reshape
jq '[.items[] | {id: .id, label: .name}]'

# Flatten nested arrays
jq '[.items[] | .tags[]] | unique'

# Group and count
jq '[.items[] | .status] | group_by(.) | map({status: .[0], count: length})'

# Modify a field
jq '.version = "2.0.0"' file.json

# Delete a field
jq 'del(.private)' package.json
```

---

## yq — YAML / TOML / XML Query

### Essentials

```bash
yq '.'                          # Pretty-print YAML
yq '.field' file.yaml           # Top-level field
yq '.parent.child' config.yaml  # Nested field
yq '.tool.ruff.line-length' pyproject.toml   # TOML field
yq '.version' package.json      # JSON (yq handles all formats)
```

### Common Config Exploration

```bash
# GitHub Actions
yq '.jobs | keys' .github/workflows/ci.yml
yq '.jobs.build.steps[].name' .github/workflows/ci.yml
yq '.on' .github/workflows/release.yml

# Docker Compose
yq '.services | keys' docker-compose.yml
yq '.services.app.environment' docker-compose.yml

# pyproject.toml
yq '.project.version' pyproject.toml
yq '.project.dependencies' pyproject.toml
yq '.tool.ruff.line-length' pyproject.toml

# Kubernetes manifests
yq '.metadata.name' deployment.yaml
yq '.spec.containers[].image' deployment.yaml

# Multi-document YAML: select by kind
yq 'select(.kind == "Deployment") | .metadata.name' manifests.yaml
```

### Format Conversion

```bash
# YAML → JSON (pipe to jq)
yq -o=json file.yaml | jq '.field'

# JSON → YAML
yq -o=yaml file.json

# TOML → JSON (pipe to jq)
yq -o=json pyproject.toml | jq '.tool.ruff'
```

---

## Combined Power Patterns

```bash
# Find Python files containing a deprecated call
fd -e py --exec rg -l "old_function" {} | sort

# Find all GitHub Actions workflows that reference a specific action
fd -e yml -e yaml .github/ --exec rg -l "uses: actions/checkout" {}

# Summarize all JSON configs at the repo root
fd -e json --max-depth 1 --exec sh -c 'echo "=== {} ==="; jq "keys" {}'

# Find all TODO comments and report with context
rg -n "TODO|FIXME" -C 1 --type py

# Get all unique import targets across a Python project
rg "^from (.+) import|^import (.+)" --type py -o --no-filename | sort -u

# Parse rg JSON output for structured analysis
rg "def test_" --json --type py \
  | jq -r 'select(.type=="match") | "\(.data.path.text):\(.data.line_number)"'

# Inspect all pyproject.toml dependency lists across a monorepo
fd "pyproject.toml" --exec yq '.project.dependencies' {}
```

---

## Output Format Tips for AI Agent Use

- Prefer `rg --json | jq` over parsing plain rg output — handles filenames with colons or spaces
- Use `jq -r` for raw strings when embedding results in further shell commands
- Use `fd -0 | xargs -0` for filenames that may contain spaces
- Use `yq -o=json | jq` when you need YAML data fed into a jq pipeline
- Use `rg -l` (filenames only) when building a file list to pass to other tools
- On Windows PowerShell, pipe works the same; prefer single quotes inside double-quoted `-e` expressions
- **PowerShell stderr**: Use `2>$null` instead of `2>/dev/null`. Never use `2>&1` when
  piping `--json` output to a JSON consumer — it merges stderr and corrupts JSON.

---

## Tool Selection Matrix

| Need                              | Best tool                                                        | Fallback             |
| --------------------------------- | ---------------------------------------------------------------- | -------------------- |
| Find function or class definition | `rg "^def\|^class" dir/`                                         | `grep_search`        |
| Find all usages of a symbol       | `rg symbol dir/`                                                 | `grep_search`        |
| Full semantic code search         | `semantic_search`                                                | `rg` with globs      |
| Find a file by partial name       | `fd partial_name` (Win/macOS), `fdfind partial_name` (Linux/WSL) | `file_search`        |
| Find files by extension           | `fd -e ext dir/` (Win/macOS), `fdfind -e ext dir/` (Linux/WSL)   | `file_search **/ext` |
| Inspect JSON output               | `jq` pipe                                                        | manual `read_file`   |
| Inspect YAML/TOML configs         | `yq`                                                             | manual `read_file`   |
| Semantic / conceptual questions   | `semantic_search`                                                | N/A                  |

---

## Integration with Agent Workflow

When rg and fd are available, prefer them in the **parallel context-gathering phase**.
On Linux/WSL use `fdfind` directly (agents do not inherit shell aliases):

```text
Phase 1 (parallel read-only): rg / fd (or fdfind on Linux/WSL) / jq for fast discovery
Phase 2 (sequential): read_file for specific line ranges
Phase 3 (sequential): edits + validation
```

Example workflow for finding and fixing a function:

```bash
# 1. Locate the function fast
rg "def my_function" src/ --type py

# 2. Read the specific file + line range (build on rg line numbers with read_file)

# 3. Find all callers before editing
rg "my_function" src/ --type py

# 4. Find related tests
fd "test_" tests/ -e py --exec rg "my_function" {}
```

---

## Command Safety Guardrails (PowerShell Only)

These rules apply only when the shell is PowerShell. Git Bash, macOS, and WSL do not have these constraints.

### Multi-key sorting

```powershell
# FORBIDDEN — parser error
Sort-Object Percent -Descending, Lines -Descending

# CORRECT — explicit per-key direction (preferred)
Sort-Object -Property @{Expression='Percent'; Descending=$true}, @{Expression='Lines'; Descending=$true}

# CORRECT — same direction for all keys
Sort-Object -Property Percent, Lines -Descending
```

### Markdown lint target discipline

- Run Markdown linters only on Markdown targets (`*.md`).
- Do not pass JSON, Python, or other non-Markdown files to markdownlint tools.
- Prefer a project-provided Markdown lint script (e.g. `npm run lint:md`) to keep globs and ignores consistent.

---

## References

- ripgrep guide: <https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md>
- jq manual: <https://jqlang.org/jq/manual/>
- yq documentation: <https://mikefarah.gitbook.io/yq/>
- fd documentation: <https://github.com/sharkdp/fd#readme>

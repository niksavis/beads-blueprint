---
applyTo: "tests/**/*.py, **/*_test.py, **/test_*.py"
description: "Use when writing or reviewing tests: enforce pytest conventions, clear assertions, and isolation patterns for this Python-first template."
---

# Testing Instructions

Apply these rules when writing or reviewing test code.

## Structure

- Place all tests under `tests/`.
- Name test files `test_<module>.py`.
- Name test functions `test_<description>`.
- One logical assertion per test when possible; group only tightly related assertions.

## Style

- Use plain `assert` statements — not `assertEqual` or other unittest-style calls.
- Prefer descriptive failure messages: `assert result == expected, f"got {result}"`.
- Keep tests short. Extract setup into fixtures, not helper functions called inline.

## Fixtures and Isolation

- Use `pytest` fixtures (`@pytest.fixture`) for shared setup/teardown.
- Never rely on global mutable state between tests.
- Use `tmp_path` (built-in pytest fixture) for temporary file operations.
- Use `monkeypatch` for environment variables and subprocess calls, not manual patching.

## Mocking

- Mock at the boundary: mock external I/O, subprocess calls, and network; not internal logic.
- Prefer `monkeypatch` over `unittest.mock.patch` for simplicity.
- When `unittest.mock` is needed, import explicitly: `from unittest.mock import MagicMock, patch`.

## Coverage

- Tests must cover the happy path and at least one failure or edge case per function.
- New features require at least one test before merge.
- Scripts in `scripts/` that accept CLI flags must have at least a smoke test.

## Running Tests

```bash
pytest -q
```

Or via the quality gate:

```bash
python validate.py --fast
```

## Repository Constraints

- Do not use `unittest.TestCase` subclasses — use plain functions and fixtures.
- Keep test dependencies in `requirements-dev.in` / `requirements-dev.txt`.
- Do not import application code that triggers side effects at import time.

# Repository Guidelines

## Project Structure & Module Organization
- `src/dnd_manager/` holds the application code, with focused modules for `ai/`, `rulesets/`, `models/`, `storage/`, `dice/`, `export/`, and `ui/`.
- `src/dnd_manager/data/` contains ruleset data and YAML guidelines.
- `tests/` contains pytest-based tests; fixtures live under `tests/fixtures/`.
- `characters/` is the default runtime storage for YAML character files (created on first use).
- `scripts/` includes standalone test scripts for AI integrations.

## Build, Test, and Development Commands
- `uv sync` sets up the virtual environment and installs dependencies.
- `uv pip install -e ".[dev]"` installs editable package plus dev tools.
- `ccvault` launches the Textual TUI once installed.
- `pytest` runs the full test suite.
- `pytest --cov=dnd_manager` runs tests with coverage output.
- `mypy src/` runs strict type checks.
- `ruff check src/` runs linting.

## Coding Style & Naming Conventions
- Python target: 3.11+ (see `pyproject.toml`).
- Indentation: 4 spaces.
- Line length: 100 (Ruff configuration).
- Type checking: `mypy` in strict mode; add types for new code.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` enabled (`asyncio_mode = auto`).
- Place new tests in `tests/` and mirror module names (e.g., `tests/test_rulesets.py`).
- Prefer small, focused tests; use fixtures in `tests/fixtures/` for shared data.

## Commit & Pull Request Guidelines
- Commit subjects in history are short, imperative, sentence case (e.g., “Fix critical issues…”, “Migrate from…”). Follow that pattern.
- PRs should describe the change, list any user-facing behavior updates, and include screenshots for UI/TUI changes.
- Link related issues when applicable.

## Configuration & Runtime Notes
- Character data is YAML and meant to be human-readable; avoid breaking schema compatibility.
- AI integrations require provider API keys; keep secrets out of the repo and document new env vars in `README.md`.

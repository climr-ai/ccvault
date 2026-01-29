---
name: dev-rules
description: Development rules that must always be followed. Enforces commit discipline, no hardcoded secrets, no workarounds, and proper code integration. Load this skill at the start of any coding session.
---

# Development Rules

These rules MUST be followed for all development work in this repository:

## Commit Discipline
- Never commit changes unless explicitly requested by the user
- Always run tests before committing
- Use meaningful commit messages that describe WHY, not just WHAT
- Never use `--no-verify` or skip hooks unless explicitly requested

## Security
- NEVER hardcode secrets, API keys, tokens, or credentials
- Use environment variables or config files (excluded from git)
- Check `.gitignore` before committing sensitive file types

## Code Quality
- No workarounds or hacks - fix the root cause
- Proper error handling, not suppression
- Follow existing code patterns and conventions
- Integration over isolation - make code work with the existing system

## Testing
- Write tests for new functionality
- Ensure existing tests pass before committing
- Don't skip or comment out failing tests - fix them

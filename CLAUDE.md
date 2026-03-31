# CrackNuts

## Project Rules

- [Git & PR Conventions](.claude/rules/git-conventions.md)

## Environment

This project uses [uv](https://github.com/astral-sh/uv) for environment and dependency management.

- Run Python: `uv run python`
- Run scripts: `uv run python <script.py>`
- Run tests: `uv run pytest`
- Add dependencies: `uv add <package>`

## Pull Requests

Before creating a PR, run the copyright fixer to ensure all source files have the required header:

```bash
uv run python scripts/copyright.py
```

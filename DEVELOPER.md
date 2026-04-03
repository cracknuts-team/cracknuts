# Developer Guide

## Project Structure

`src/` — production source code  
`tests/` — unit and integration tests

## Branch Strategy

- `main` — main branch; only tested, reviewed code is merged here
- `major.minor_dev` — feature development branch for a specific version; merged into `major.minor` once stable
- `major.minor` — stable branch for a released version; receives bug fixes only

Developers should complete feature work and testing on a local branch, then open a pull request targeting either `main` or the appropriate `major.minor` branch.

## Development Environment Setup

This project uses [uv](https://github.com/astral-sh/uv) for environment and dependency management.

**1. Clone the repository**

```shell
git clone https://github.com/cracknuts-team/cracknuts.git
cd cracknuts
```

**2. Install uv** (if not already installed)

On Linux / macOS:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**3. Install project dependencies**

```shell
uv sync
```

This creates `.venv/` and installs all dependencies (including dev dependencies) in editable mode.

**4. Install JavaScript dependencies**

```shell
cd jupyter_frontend
pnpm install
```

**5. Run in development mode**

```shell
pnpm run dev
```

To enable HMR (Hot Module Replacement), set `ANYWIDGET_HMR=1`:

```shell
# bash
ANYWIDGET_HMR=1 jupyter lab
```

```powershell
# PowerShell
$env:ANYWIDGET_HMR=1; jupyter lab
```

## Common Commands

| Task | Command |
|---|---|
| Run Python | `uv run python` |
| Run a script | `uv run python <script.py>` |
| Run tests | `uv run pytest` |
| Add a dependency | `uv add <package>` |
| Build the package | `uv build` |

## Code Conventions

- Variables and functions: `snake_case`
- Classes: `PascalCase`
- All variables and function parameters must have type annotations
- Logger instances in classes must use the fully-qualified path as name (e.g. `cracknuts.cracker.cracker_s1`)
- Docstrings: reStructuredText (reST) format

## Commit Message Conventions

All commit messages must be written in **English**.

**Format:**

```
<type>[(<scope>)]: <short description>

[body]

[footer]
```

**Types:**

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructure — no new feature or bug fix |
| `test` | Adding or updating tests |
| `chore` | Build tools, config files, dependencies |

**Rules:**

- Subject line ≤ 50 characters, imperative mood ("Add X", not "Added X")
- Scope is optional; use it to indicate the affected module (e.g. `fix(cracker):`)
- Leave a blank line between subject and body

**Examples:**

```
feat(cracker): add voltage configuration interface

Added new interface for configuring voltage settings.
Closes #42
```

```
fix: correct ADC sampling rate calculation
```

# Developer Guide

## Project Overview

**cracknuts** is a Python library for controlling cryptanalysis hardware devices, focused on Side-Channel Analysis (SCA). It supports power analysis and fault injection (Glitch).

- **Python**: >= 3.12
- **Frontend**: React + TypeScript (via anywidget)
- **Build**: setuptools (Python), esbuild (frontend)
- **Package Manager**: pip (Python), pnpm (frontend)

## Project Structure

```
cracknuts/
├── src/cracknuts/             # Python source code
│   ├── cracker/               # Device communication layer (CNP protocol, S1/G1/O1 models)
│   ├── acquisition/           # Acquisition orchestration (template method lifecycle)
│   ├── trace/                 # Data storage layer (Zarr/NumPy/Scarr format adapters)
│   ├── jupyter/               # Interactive UI layer (anywidget panels)
│   ├── glitch/                # Fault injection (Glitch parameter generators)
│   ├── scope/                 # Oscilloscope module
│   ├── mock/                  # Mock device layer for testing without hardware
│   ├── utils/                 # Shared utilities
│   └── template/              # Project templates
├── jupyter_frontend/          # TypeScript/React frontend source
│   └── src/                   # Widget components (panels, charts, controls)
├── tests/                     # Test suite (pytest)
├── demo/                      # Usage examples and demo notebooks
├── docs/                      # Documentation source
├── scripts/                   # Build and release scripts
├── install/                   # Installation helpers
└── pyproject.toml             # Project metadata and tool configuration
```

### Key Python Modules

| Module | Description |
|---|---|
| `cracker/` | CNP protocol implementation, device abstraction (`CrackerBasic`, `CrackerS1`, `CrackerG1`, `CrackerO1`) |
| `acquisition/` | Acquisition lifecycle with template method pattern, thread concurrency |
| `trace/` | Trace data I/O via Zarr, NumPy, and Scarr formats with downsampling |
| `jupyter/` | anywidget-based Jupyter panels, bridging Python models to React UI |
| `glitch/` | Glitch parameter generation for fault injection campaigns |
| `scope/` | Oscilloscope integration |
| `mock/` | Simulated devices for development and CI without physical hardware |

### Frontend Structure (`jupyter_frontend/src/`)

The frontend uses React 18, Ant Design, and ECharts, bundled with esbuild. Each panel widget has a corresponding `*Widget.tsx` entry point that bridges anywidget's model to React components.

## Development Environment Setup

### Prerequisites

- Python >= 3.12
- Node.js (LTS recommended)
- pnpm (see version in `jupyter_frontend/package.json` `packageManager` field)

### Clone and Install

```shell
git clone https://github.com/cracknuts-team/cracknuts.git
cd cracknuts
```

#### Python Setup

On Linux:

```shell
python3 -m venv --prompt cracknuts .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

On Windows:

```shell
python -m venv --prompt cracknuts .venv
.venv\Scripts\Activate.ps1
pip install -e .
pip install -r requirements-dev.txt
```

#### Frontend Setup

```shell
cd jupyter_frontend
pnpm i
```

### Running in Development Mode

Start the frontend dev server (with watch and rebuild):

```shell
cd jupyter_frontend
npm run dev
```

To enable Hot Module Replacement (HMR) for anywidget, set the `ANYWIDGET_HMR` environment variable:

```shell
# bash
ANYWIDGET_HMR=1 jupyter lab
```

```shell
# powershell
$env:ANYWIDGET_HMR=1
```

### Building

Build the Python package:

```shell
python -m build
```

Build the frontend for production:

```shell
cd jupyter_frontend
pnpm run clean-build
```

## Branch Strategy

- **`main`**: The primary branch. Only tested, stable code is merged here. Always reflects the latest release-ready state.
- **`major.minor_dev`**: Feature development branches for a specific version. Used during active development of new features. Merged into the corresponding `major.minor` branch once stable.
- **`major.minor`**: Version branches. Contain stable feature code for that version and subsequent bug fixes.

### Workflow

1. Create a local branch from the appropriate base branch for your work.
2. Complete development and testing locally.
3. Push to the remote dev branch.
4. After review and verification, merge into `main` and the corresponding version branch.

## Code Style and Conventions

### Python

- **Naming**: snake_case for variables, functions, and modules; PascalCase for classes.
- **Type annotations**: All function parameters, return types, and class attributes must have type annotations.
- **Logging**: Logger instances in classes must use the fully qualified name (`package.module.ClassName`).
- **Docstrings**: Use reStructuredText (reST) format.
- **Line length**: 120 characters max (configured in `pyproject.toml` under `[tool.ruff]`).
- **Linter/Formatter**: Ruff is used for both linting and formatting.

### TypeScript

- **Linter**: ESLint (configured in `jupyter_frontend/eslint.config.mjs`).
- **Formatter**: Prettier.
- **Type checking**: `tsc --noEmit` via `pnpm run typecheck`.

### Pre-commit Hooks

The project uses `pre-commit` with the following hooks (see `.pre-commit-config.yaml`):

- `validate-pyproject`: Validates `pyproject.toml`.
- `markdownlint-fix`: Lints and auto-fixes Markdown files.
- `typos`: Catches common typos.
- `ruff`: Lints and formats Python code.

Install the hooks after cloning:

```shell
pre-commit install
```

## Testing

Tests are located in `tests/` and run with pytest:

```shell
pytest tests/
```

Test modules mirror the source structure (`tests/acquisition/`, `tests/cracker/`, `tests/jupyter/`, `tests/trace/`, etc.).

## Commit Message Convention

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <short description>

<body (optional)>

<footer (optional)>
```

### Rules

1. **Subject line**: Keep under 50 characters. Use imperative mood (e.g., "Add", not "Added").
2. **Type**: One of the following:
   - `feat`: A new feature
   - `fix`: A bug fix
   - `docs`: Documentation changes only
   - `style`: Code style changes (formatting, no functional impact)
   - `refactor`: Code refactoring (no new features, no bug fixes)
   - `test`: Adding or updating tests
   - `chore`: Miscellaneous changes (build tools, config, etc.)
   - `release`: Version release
3. **Scope** (optional): The module or subsystem affected, in parentheses (e.g., `feat(cracker)`, `fix(acquisition)`).
4. **Body** (optional): Separated from the subject by a blank line. Explain the motivation and context for the change.
5. **Footer** (optional): Reference related issues or PRs (e.g., `Closes #42`).

### Examples

```
feat(cracker): add voltage configuration interface

Add a new interface for configuring device voltage levels.
Closes #42
```

```
fix(trace): resolve Zarr chunk size mismatch on large traces
```

```
docs: update developer guide with commit conventions
```

## Dev Dependencies

The development toolchain (see `requirements-dev.txt`):

| Tool | Purpose |
|---|---|
| `ruff` | Python linter and formatter |
| `mypy` | Static type checker |
| `pytest` | Test framework |
| `pytest-html` | HTML test reports |
| `pre-commit` | Git hook management |
| `typos` | Spell checker |
| `build` | Python package builder |
| `watchfiles` | File watcher for dev workflows |
| `nbstripout` | Strips output from Jupyter notebooks before commit |

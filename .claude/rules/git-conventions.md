# Git & PR Conventions

## Commit Message Format

```
<type>[(<scope>)]: <short description>

<body (optional)>

<footer (optional)>
```

**Types:**

- `feat` — new feature added
- `fix` — bug fix
- `docs` — documentation changes only
- `style` — formatting, whitespace, no logic change
- `refactor` — code restructure, no new feature or bug fix
- `test` — adding or updating tests
- `chore` — build tools, config files, dependencies, misc

**Rules:**

- English only
- Subject line ≤ 50 chars, imperative mood ("Add X", not "Added X")
- Scope is optional; use it to indicate the affected module (e.g. `fix(cracker):`)
- No Co-Authored-By or Claude attribution lines

**Example:**

```
feat(cracker): add voltage configuration interface

Added new interface for configuring voltage settings.
Closes #42
```

## GitHub PR Format

- Title follows the same `<type>: <description>` format
- Body in English only
- No Co-Authored-By or Claude attribution lines

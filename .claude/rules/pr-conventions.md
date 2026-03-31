# PR Conventions

## Before Creating a PR

Run the copyright fixer to ensure all source files have the required header:

```bash
uv run python scripts/copyright.py
```

Every Python file under `src/` must start with:

```python
# Copyright 2024 CrackNuts. All rights reserved.
```

followed by a blank line.

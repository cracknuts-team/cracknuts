---
name: release
description: Bump version, tag, and publish a release. Trigger for any request to release, publish, or bump a version — e.g. "release patch", "bump minor", "publish a new alpha", or equivalent in any language.
argument-hint: <major|minor|patch> [alpha|beta|rc|-]
allowed-tools: [Bash]
---

# Release

Bump the project version, commit, tag, and push to remote.

## Trigger

Invoke this skill whenever the user's request matches release / publish / version-bump intent, including but not limited to:

- release / publish / bump a (patch|minor|major) version
- create a new release / tag a new version
- publish a (alpha|beta|rc) pre-release
- any equivalent phrasing in any language

## Arguments

The user invoked this with: $ARGUMENTS

## Version Bump Rules

The script reads the current version from `src/cracknuts/__init__.py` and computes the next version:

| Arguments | Effect |
|---|---|
| `major` | Bump major (e.g. 1.2.3 → 2.0.0) |
| `minor` | Bump minor (e.g. 1.2.3 → 1.3.0) |
| `patch` | Bump patch (e.g. 1.2.3 → 1.2.4) |
| `major alpha\|beta\|rc` | New major pre-release (e.g. 1.2.3 → 2.0.0-alpha.0) |
| `minor alpha\|beta\|rc` | New minor pre-release (e.g. 1.2.3 → 1.3.0-alpha.0) |
| `patch alpha\|beta\|rc` | New patch pre-release (e.g. 1.2.3 → 1.2.4-alpha.0) |
| `major\|minor\|patch -` | Release final from pre-release (e.g. 1.2.3-alpha.0 → 1.2.3) |
| `alpha\|beta\|rc` | Bump pre-release sequence only (e.g. 1.2.3-alpha.0 → 1.2.3-alpha.1, or → 1.2.3-beta.0) |

## Argument Parsing

Before running anything, determine the script arguments from `$ARGUMENTS`:

**Case 1 — Standard arguments** (already match the script's accepted format, e.g. `patch`, `minor alpha`, `rc`):
Use them directly as the script arguments.

**Case 2 — Natural language** (anything else, e.g. "release a beta", "bump minor pre-release", or equivalent in any language):
Parse the intent and map it to the standard argument format using the Version Bump Rules table above.
Examples:

- "release patch" → `patch`
- "publish a minor alpha" → `minor alpha`
- "bump to the next rc" → `rc`
- "finalize the current pre-release" → `patch -` (or the appropriate level)

**Case 3 — Empty or ambiguous**:
Tell the user the arguments could not be determined and ask them to provide the script arguments manually, then proceed once clarified.

## Instructions

1. Parse `$ARGUMENTS` per the rules above to determine the script arguments (call them `<confirmed_args>`).

2. Run preview to get the current and next version:

   ```
   uv run python scripts/release.py preview <confirmed_args>
   ```

   If this exits with an error, show the output and stop.

3. **Ask the user to confirm before proceeding.** Use AskUserQuestion with the preview output, e.g.:
   > Current: 0.24.0 → Next: 0.24.1. Proceed with release? Or enter different args to override.

   Wait for explicit confirmation. If the user provides different args, update `<confirmed_args>` and repeat from step 2.

4. Run the release script to bump version, commit and tag:

   ```
   uv run python scripts/release.py <confirmed_args>
   ```

   If this exits with an error, show the error output and stop.

5. **Ask the user to confirm before pushing.** Use AskUserQuestion, e.g.:
   > Tagged as 0.24.1. Push to remote?

   Wait for explicit confirmation. If the user says no, stop here and report the tag was created but not pushed.

6. Push the commit and tag:

   ```
   uv run python scripts/release.py push
   ```

7. Report the new version tag that was pushed.

## Error Handling

- If the script fails (including when called with no arguments and the script prints its own usage), show the output and stop.
- Never force-push or use `--force` flags.

---
name: git-commit
description: Stage, commit, and optionally push changes to git. Trigger for any request to commit, stage, or submit changes — e.g. "commit changes", "git commit", "提交变更", or equivalent in any language.
allowed-tools: [Bash, AskUserQuestion]
---

# Git Commit

Stage, commit, and optionally push changes to git.

## Trigger

Invoke this skill whenever the user's request matches commit / stage intent, including but not limited to:

- commit / git commit / stage changes
- submit changes / 提交变更
- any equivalent phrasing in any language

**Note**: If the user only wants to push (e.g. "push to remote", "git push"), do NOT invoke this skill — that's a simple command that doesn't need skill assistance.

## Arguments

The user invoked this with: $ARGUMENTS

## Instructions

### Step 1 — Determine which files to stage

**Case 1 — User specified files or paths** (e.g. "commit file1.py and file2.py", "commit src/"):
Stage only the specified paths. Skip to Step 2.

**Case 2 — User wants to commit staged changes** (e.g. "commit staged changes", "commit what's in the index", "提交暂存区的内容"):
Only consider already-staged changes. Run:

```bash
git diff --staged --stat
git diff --staged --name-only
```

If nothing is staged, inform the user and stop. Skip to Step 3 (no need to stage again).

**Case 3 — User did not specify** (e.g. "commit", "commit changes"):
Run the following to get the current status:

```bash
git status --short
git diff --stat
git diff --staged --stat
```

Based on the output and the conversation context, determine which files should be staged. Present the proposed changes (including both staged and unstaged) to the user and ask for confirmation using AskUserQuestion.

If the user wants to adjust the selection, update the file list accordingly.

### Step 2 — Show proposed changes and confirm staging

Before staging, show the user a summary of what will be staged:

```bash
git diff --stat <files>
git diff --staged --stat <files>
```

Ask the user to confirm using AskUserQuestion:
> Stage the following changes to git? [Yes/No/Edit]

Wait for explicit confirmation. If the user says no or wants to edit, ask which files to include/exclude and update the list.

### Step 3 — Generate commit message

Analyze the staged changes and the conversation context to generate a commit message that follows the commit message format:

```
<type>(<scope>): <short description>

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
- No Co-Authored-By or Claude attribution lines

Show the proposed commit message to the user and ask for confirmation using AskUserQuestion:
> Commit with message: "<message>"? [Yes/Edit/Cancel]

Wait for explicit confirmation. If the user wants to edit, accept their revised message.

### Step 4 — Stage and commit

Stage the confirmed files:

```bash
git add <file1> <file2> ...
```

Commit with the confirmed message:

```bash
git commit -m "<message>"
```

If the commit fails, show the error and stop.

### Step 5 — Ask to push to remote (optional)

After a successful commit, ask the user using AskUserQuestion:
> Push to remote? [Yes/No]

Default to **Yes**.

If the user confirms, check if the current branch has a tracking branch:

```bash
git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
```

**If a tracking branch exists**, push normally:

```bash
git push
```

**If no tracking branch exists**, push with upstream setup:

```bash
git push -u origin <branch>
```

**CRITICAL: NEVER use `--force` or `-f` flags under any circumstances.**

If push fails, show the error and stop.

If the user declines, stop here and report the commit was created but not pushed.

### Step 6 — Report result

Report the final status:

- Commit hash and message
- Whether push succeeded or was skipped

## Error Handling

- If any git command fails, show the output and stop.
- Never use `--force` or `-f` flags for push.
- If the user declines at any confirmation step, stop and report what was done so far.

#!/usr/bin/env python3

import os
import re
import subprocess
import sys


def get_next_version(file_path, bump_type, is_alpha):
    with open(file_path) as file:
        content = file.read()

    match = re.search(r'__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)\.(\d+))?"', content)

    if not match:
        print("Error: Could not find version in the file.")
        sys.exit(1)

    major, minor, patch, alpha = (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        None if match.group(4) is None else int(match.group(4)),
    )

    if bump_type == "major":
        major += 1
        minor, patch = 0, 0
        if is_alpha:
            alpha = 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
        if is_alpha:
            alpha = 1
    elif bump_type == "patch":
        patch += 1
        if is_alpha:
            alpha = 1
    elif bump_type == "alpha":
        if is_alpha and alpha is None:
            print("Error: Alpha version requires the base version to be alpha.")
            sys.exit(1)
        else:
            alpha += 1
    else:
        print("Error: Bump type must be 'major', 'minor', 'patch', or 'alpha'.")
        sys.exit(1)

    if is_alpha:
        new_version = f"{major}.{minor}.{patch}-alpha.{alpha}"
    else:
        new_version = f"{major}.{minor}.{patch}"

    return new_version


def update_version(file_path, new_version):
    with open(file_path, "r+") as file:
        content = file.read()
        new_content = re.sub(
            r'__version__\s*=\s*"\d+\.\d+\.\d+(?:-alpha\.\d+)?"', f'__version__ = "{new_version}"', content
        )
        file.seek(0)
        file.write(new_content)
        file.truncate()


def git_commit_and_tag(file_path, version, repo_root):
    # 在Git根目录中执行添加、提交和打标签的命令
    subprocess.run(["git", "add", file_path], cwd=repo_root)

    # 提交更改
    commit_message = f"release: {version}"
    subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_root)

    # 打标签
    subprocess.run(["git", "tag", version], cwd=repo_root)

    print(f"Committed and tagged as {version}")


def main(args):
    if len(args) < 2:
        print("Usage: python update_version.py [major|minor|patch|alpha] [alpha]")
        sys.exit(1)

    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    file_path = os.path.join(root_path, "src/cracknuts/__init__.py")

    pr_release = ["a", "b", "rc"]
    is_pre = args[1] in pr_release or (len(args) > 2 and args[2] in pr_release)
    new_version = get_next_version(file_path, args[1], is_pre)
    print(f"New version: {new_version}")
    # update_version(file_path, new_version)
    # git_commit_and_tag(file_path, new_version, root_path)


if __name__ == "__main__":
    main(sys.argv)

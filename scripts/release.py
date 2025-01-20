#!/usr/bin/env python3

import os
import re
import subprocess
import sys


def update_version(file_path, bump_type, is_alpha):
    with open(file_path) as file:
        content = file.read()

    match = re.search(r'__version__\s*=\s*"([0-9]+)\.([0-9]+)\.([0-9]+)(-alpha\.([0-9]))?"', content)

    if not match:
        print("Error: Could not find version in the file.")
        sys.exit(1)

    print(match.groups())
    # 获取版本号
    if is_alpha:
        major, minor, patch, alpha = map(int, match.groups())
    else:
        major, minor, patch = map(int, match.groups())
        alpha = 1  # 如果不是 alpha 版本，设置 alpha 为 1（不使用，但需要避免后续错误）

    # 根据 bump_type 增加版本号
    if bump_type == "major":
        major += 1
        minor, patch = 0, 0
        if is_alpha:
            alpha = 1  # Reset alpha to 1 for major bump
    elif bump_type == "minor":
        minor += 1
        patch = 0
        if is_alpha:
            alpha = 1  # Reset alpha to 1 for minor bump
    elif bump_type == "patch":
        patch += 1
    elif bump_type == "alpha":
        if is_alpha:  # 增长 alpha 后缀的版本
            alpha += 1
        else:
            print("Error: Alpha version requires the base version to be alpha.")
            sys.exit(1)
    else:
        print("Error: Bump type must be 'major', 'minor', 'patch', or 'alpha'.")
        sys.exit(1)

    # 更新版本号字符串
    if is_alpha:
        new_version = f"{major}.{minor}.{patch}-alpha.{alpha}"
    else:
        new_version = f"{major}.{minor}.{patch}"

    # 替换文件中的版本号
    new_content = re.sub(
        r'__version__\s*=\s*"[0-9]+\.[0-9]+\.[0-9]+(-alpha\.[0-9]+)?"', f'__version__ = "{new_version}"', content
    )

    with open(file_path, "w") as file:
        file.write(new_content)

    print(f"Updated version to {new_version}")
    return new_version


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

    # 拼接目标文件的路径 (假设目标文件位于脚本同级的其他目录)
    file_path = os.path.join(root_path, FILE_PATH)

    # 判断是否为 alpha 版本
    is_alpha = args[1] == "alpha" or (len(args) > 2 and args[2] == "alpha")
    new_version = update_version(file_path, args[1], is_alpha)
    git_commit_and_tag(file_path, new_version, root_path)


FILE_PATH = "src/cracknuts/__init__.py"

if __name__ == "__main__":
    main(sys.argv)

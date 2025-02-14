#!/usr/bin/env python3

import os
import re
import subprocess
import sys

PRE_RELEASE_SEQ = ["alpha", "beta", "rc", "-"]


def get_next_version(file_path, version_level, next_pre_release):
    with open(file_path) as file:
        content = file.read()

    match = re.search(r'__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta|rc)\.(\d+))?"', content)

    if not match:
        print("Error: Could not find version in the file.")
        sys.exit(1)

    major, minor, patch, pre_release, pre_release_no = (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        None if match.group(4) is None else match.group(4),
        None if match.group(5) is None else int(match.group(5)),
    )

    if pre_release is not None and pre_release_no is None:
        pre_release_no = 0

    if version_level is None:
        if next_pre_release is None:
            print("Either version_level or next_pre_release must be specified.")
            sys.exit(1)
        else:
            if pre_release is None:
                print("The version_level must be specified when the current version is not a pre-release.")
                sys.exit(1)
            else:
                if pre_release != next_pre_release:
                    if PRE_RELEASE_SEQ.index(next_pre_release) <= PRE_RELEASE_SEQ.index(pre_release):
                        print(
                            f"Next pre-release {next_pre_release} must greater than current pre-release: {pre_release}."
                        )
                        sys.exit(1)
                    pre_release = next_pre_release
                    pre_release_no = 0
                else:
                    pre_release_no += 1
    elif version_level == "major":
        if next_pre_release is None:
            if pre_release is None:
                major += 1
                minor, patch = 0, 0
                pre_release = None
                pre_release_no = None
            else:
                pre_release = None
                pre_release_no = None
        else:
            if next_pre_release == PRE_RELEASE_SEQ[-1]:
                major += 1
                minor, patch = 0, 0
                pre_release = None
                pre_release_no = None
            else:
                major += 1
                minor, patch = 0, 0
                pre_release = next_pre_release
                pre_release_no = 0

    elif version_level == "minor":
        if next_pre_release is None:
            if pre_release is None:
                minor += 1
                patch = 0
                pre_release = None
                pre_release_no = None
            else:
                pre_release = None
                pre_release_no = None
        else:
            if next_pre_release == PRE_RELEASE_SEQ[-1]:
                minor += 1
                patch = 0
                pre_release = None
                pre_release_no = None
            else:
                minor += 1
                patch = 0
                pre_release = next_pre_release
                pre_release_no = 0
    elif version_level == "patch":
        if next_pre_release is None:
            if pre_release is None:
                patch += 1
                pre_release = None
                pre_release_no = None
            else:
                pre_release = None
                pre_release_no = None
        else:
            if next_pre_release == PRE_RELEASE_SEQ[-1]:
                patch += 1
                pre_release = None
                pre_release_no = None
            else:
                patch += 1
                pre_release = next_pre_release
                pre_release_no = 0
    else:
        print("Error: version_level must be 'major', 'minor', 'patch', or left unspecified.")
        sys.exit(1)

    if pre_release is not None and pre_release_no is not None:
        new_version = f"{major}.{minor}.{patch}-{pre_release}.{pre_release_no}"
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


def help():
    return r"""
    release.py [version_level] [pre_release]

    Commands:
    version_level:
        major
        minor
        patch
    pre_release:
        alpha
        beta
        rc

    Examples:
    - increase major|minor|patch on no pre-release: release.py major|minor|patch
    - increase major|minor|patch on pre-release: release.py major|minor|patch -
    - release pre-release on pre-release: release.py major|minor|patch
    - increase major|minor|patch with pre-release: release.py major|minor|patch alpha|beta|rc
    """


def main(args):
    if len(args) < 2:
        print(f"Usage: {help()}")
        sys.exit(1)

    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    file_path = os.path.join(root_path, "src/cracknuts/__init__.py")

    if len(args) == 2 and args[1] in PRE_RELEASE_SEQ:
        new_version = get_next_version(file_path, None, args[1])
    else:
        new_version = get_next_version(file_path, args[1], args[2] if len(args) == 3 else None)
    update_version(file_path, new_version)
    git_commit_and_tag(file_path, new_version, root_path)


if __name__ == "__main__":
    main(sys.argv)

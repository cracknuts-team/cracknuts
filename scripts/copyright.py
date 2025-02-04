#!/usr/bin/env python3

import os
import sys


def add_copyright():
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(__file__))

    # Directories to scan
    src_path = os.path.join(project_root, "src")

    # Counter for updated files
    count = 0

    skip_dirs = ["bin", "node_modules"]
    new_line = "# Copyright 2024 CrackNuts. All rights reserved.\n\n"

    # Iterate over each Python file in the specified directory
    for root, _, files in os.walk(src_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Check if the file is in a directory to skip
                skip = any(skip_dir in root for skip_dir in skip_dirs)
                # If the file is not in a directory to skip, process it
                if not skip:
                    print(f"checking {file_path}.")
                    with open(file_path, "r+", encoding="utf-8") as f:
                        content = f.readlines()

                        # Check if the file does not start with "# Copyright"
                        if not content or not content[0].startswith("# Copyright"):
                            # Prepend the copyright line
                            content.insert(0, new_line)

                            # Move the cursor to the beginning of the file and write the updated content
                            f.seek(0)
                            f.writelines(content)
                            f.truncate()  # Truncate the file to the new length
                            print(f"Success add copyright notices to {file_path}.")
                            count += 1

    if count > 0:
        print(f"added copyright notices to {count} files")


def check_copyright(files: list[str]):
    if len(files) == 0:
        home = os.path.dirname(os.path.dirname(__file__))
        src_path = os.path.join(home, "src")
        files = (os.path.join(root, file) for root, dirs, files in os.walk(src_path) for file in files)

    files_without_copyright = []

    skip_dirs = ["tests", "node_modules", "scripts", "docs", "demo"]

    for file in files:
        if file.endswith(".py"):
            skip = any(skip_dir in file for skip_dir in skip_dirs)
            if skip:
                continue
            print(f"Checking {file}.")
            with open(file, encoding="utf-8") as f:
                content = f.readlines()
                if content:
                    if content[0].strip() != "# Copyright 2024 CrackNuts. All rights reserved.":
                        files_without_copyright.append(file)
                    elif content[1].strip() != "":
                        files_without_copyright.append(file)

    if len(files_without_copyright) > 0:
        files_list = "\n".join(files_without_copyright)
        print(
            f"The files: \n{files_list}\nis missing a copyright notice or "
            f"lacks a blank line after the copyright notice."
        )
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not sys.stdin.isatty():
        files = sys.stdin.read().strip().splitlines()
        args.extend(files)
    if len(args) >= 1 and args[0] == "check":
        check_copyright(args[1:])
    else:
        add_copyright()

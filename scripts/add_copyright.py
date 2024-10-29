import os

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Directories to scan
dir_path = os.path.join(project_root, "src")

# Counter for updated files
count = 0

skip_dirs = ["bin"]
new_line = "# Copyright 2024 CrackNuts. All rights reserved.\r\n"

# Iterate over each Python file in the specified directory
for root, _, files in os.walk(dir_path):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)

            # Check if the file is in a directory to skip
            skip = any(skip_dir in root for skip_dir in skip_dirs)

            # If the file is not in a directory to skip, process it
            if not skip:
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
                        count += 1

if count > 0:
    print(f"added copyright notices to {count} files")

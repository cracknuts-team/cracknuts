import json
from pathlib import Path

# ====== 配置 ======
TARGET_DIR = Path("src/cracknuts/firmware")  # 目标目录
JSON_PATH = TARGET_DIR / "map.json"
DRY_RUN = False  # True: 仅打印；False: 实际删除
# ==================


def load_used_files(json_path: Path) -> set[str]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    used = set()
    for item in data.values():
        if "server" in item:
            used.add(item["server"])
        if "bitstream" in item:
            used.add(item["bitstream"])
    return used


def cleanup_directory(target_dir: Path, json_path: Path, used_files: set[str], dry_run: bool):
    json_filename = json_path.name

    for path in target_dir.iterdir():
        # 只处理普通文件
        if not path.is_file():
            continue

        # 跳过配置 JSON 本身
        if path.name == json_filename:
            continue

        # JSON 未引用的文件 → 删除
        if path.name not in used_files:
            if dry_run:
                print(f"[DRY-RUN] would delete: {path.name}")
            else:
                path.unlink()
                print(f"[DELETED] {path.name}")


def main():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {JSON_PATH}")

    used_files = load_used_files(JSON_PATH)

    print("Files referenced in config:")
    for f in sorted(used_files):
        print("  ", f)

    print(f"\nCleaning directory: {TARGET_DIR}")
    cleanup_directory(TARGET_DIR, JSON_PATH, used_files, DRY_RUN)


if __name__ == "__main__":
    main()

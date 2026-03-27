#!/usr/bin/env python3
# Copyright 2024 CrackNuts. All rights reserved.

"""Build the wheel and smoke-test it in a clean virtual environment."""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
SMOKE_ENV = DIST_DIR / ".smoke_env"


def _venv_bin(venv_path: Path, name: str) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / name
    return venv_path / "bin" / name


def build_wheel() -> Path:
    print("==> Building wheel ...")
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(DIST_DIR)],
        cwd=PROJECT_ROOT,
        check=True,
    )
    wheels = sorted(DIST_DIR.glob("*.whl"))
    if not wheels:
        print("ERROR: No wheel found in dist/ after build.")
        sys.exit(1)
    wheel = wheels[-1]
    print(f"    Built: {wheel.name}")
    return wheel


def create_smoke_env():
    import venv

    if SMOKE_ENV.exists():
        shutil.rmtree(SMOKE_ENV)
    SMOKE_ENV.mkdir(parents=True, exist_ok=True)
    print("==> Creating clean virtual environment ...")
    venv.create(SMOKE_ENV, with_pip=True)


def run_smoke_test(wheel: Path):
    pip = _venv_bin(SMOKE_ENV, "pip")
    python = _venv_bin(SMOKE_ENV, "python")

    print("==> Installing wheel ...")
    subprocess.run([str(pip), "install", str(wheel)], check=True)

    print("==> Running smoke test ...")
    subprocess.run(
        [
            str(python),
            "-c",
            "import cracknuts; print(f'cracknuts {cracknuts.version()} imported successfully')",
        ],
        check=True,
    )


def cleanup():
    if SMOKE_ENV.exists():
        shutil.rmtree(SMOKE_ENV)
        print("==> Cleaned up smoke env.")


def main():
    wheel = build_wheel()
    create_smoke_env()
    try:
        run_smoke_test(wheel)
        print("\nBuild and smoke test passed. Safe to push.")
    except subprocess.CalledProcessError:
        print("\nSmoke test FAILED.")
        sys.exit(1)
    finally:
        cleanup()


if __name__ == "__main__":
    main()

"""Script for cleaning up temporary files and directories"""

import shutil
from pathlib import Path


def remove_path(path: Path) -> None:
    """Remove a file or directory

    Args:
        path (Path): The path to the file or directory to remove.
    """
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.is_file():
        path.unlink()


def clean() -> None:
    """Clean up temporary files and directories"""
    print("\n🧹 Cleaning up temporary files and directories...\n")
    patterns = [
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".ruff_cache",
        "__pycache__",
        "*.egg-info",
        "*.dist-info",
        "*.pyc",
    ]
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            remove_path(path)

    artifacts = [
        Path("dist"),
        Path("build"),
        Path(".test-env"),
        Path(".pypi"),
        Path(".testpypi"),
    ]
    for path in artifacts:
        if path.exists():
            remove_path(path)
            print(f"Removed {path}")

    print("\n🧹 Cleanup complete!\n")


if __name__ == "__main__":
    clean()

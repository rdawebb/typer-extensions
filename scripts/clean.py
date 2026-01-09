"""Script for cleaning up temporary files and directories"""

import shutil
from pathlib import Path


def remove_path(path: Path):
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.is_file():
        path.unlink()


def clean():
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


if __name__ == "__main__":
    clean()

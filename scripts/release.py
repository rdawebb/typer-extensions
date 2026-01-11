"""Build, test, and validate package ready for release"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and report results

    Args:
        cmd (list[str]): The command to run.
        description (str): A description of the command for logging purposes.

    Returns:
        bool: True if the command succeeded, False otherwise.
    """
    print(f"\n📌 {description}\n")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}\n")
        return False


def build() -> int:
    """Execute pre-release validation pipeline

    Returns:
        int: The exit code of the pre-release validation pipeline.
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    test_env = ".test-env"
    dist_dir = "dist"

    # Step 1: Build package
    if not run_command(["uv", "build"], "🔨 Building package"):
        return 1

    # Step 2: Clean test environment
    print("\n🧹 Cleaning test environment")
    if Path(test_env).exists():
        shutil.rmtree(test_env)
        print(f"Removed {test_env}")

    # Step 3: Create test environment
    if not run_command(
        ["python3", "-m", "venv", test_env], "📦 Creating test environment"
    ):
        return 1

    # Step 4: Install package from dist
    print("\n💾 Installing package from dist")
    wheel_files = list(Path(dist_dir).glob("*.whl"))
    if not wheel_files:
        print("\n❌ No wheel file found in dist/")
        return 1

    wheel_path = wheel_files[0]
    pip_cmd = f"source {test_env}/bin/activate && uv pip install {wheel_path} pytest"
    try:
        subprocess.run(pip_cmd, shell=True, check=True, executable="/bin/bash")
        print(f"Installed {wheel_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed with exit code {e.returncode}")
        return 1

    # Step 5: Test import
    print("\n✅ Testing import")
    import_cmd = f"source {test_env}/bin/activate && python -c 'import typer_aliases; print(f\"Version: {{typer_aliases.__version__}}\")'"
    try:
        subprocess.run(import_cmd, shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Import test failed with exit code {e.returncode}\n")
        return 1

    # Step 6: Run tests
    print("\n🧪 Running test suite\n")
    test_cmd = f"source {test_env}/bin/activate && pytest ."
    try:
        subprocess.run(test_cmd, shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}\n")
        return 1

    # Success
    print("\n✨ Pre-release validation complete!\n")
    return 0


if __name__ == "__main__":
    sys.exit(build())

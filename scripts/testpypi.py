"""Script to install and test the latest release on TestPyPI."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE_NAME = "typer-extensions"
TESTPYPI_URL = "https://test.pypi.org/simple/"
TEST_VENV = ".testpypi"
DIST_DIR = "dist"


def expected_version() -> str:
    """Get the expected version of the package.

    Returns:
        str: The expected version string.
    """
    version_file = Path("src/typer_extensions/_version.py")
    content = version_file.read_text()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise ValueError("Version not found")


def run_command(
    cmd: list[str], description: str, capture_output: bool = False
) -> subprocess.CompletedProcess[str]:
    """Run a command and report results

    Args:
        cmd (list[str]): The command to run.
        description (str): A description of the command for logging purposes.
        capture_output (bool): Whether to capture stdout/stderr.

    Returns:
        subprocess.CompletedProcess: The completed process result.

    Raises:
        subprocess.CalledProcessError: If the command fails.
    """
    print(f"\n📌 {description}\n")
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=capture_output, text=True
        )
        if capture_output and result.stdout:
            print(result.stdout)
        return result

    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}\n")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        raise


def install_testpypi() -> int:
    """TestPyPI install & test script.

    Returns:
        int: The exit code of the script.
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    try:
        EXPECTED_VERSION = expected_version()
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Failed to determine version: {e}")
        return 1

    # Step 1: Clean up any existing test environment
    print("\n🧹 Cleaning test environment")
    if Path(TEST_VENV).exists():
        shutil.rmtree(TEST_VENV)
        print(f"Removed {TEST_VENV}")

    # Step 2: Create test environment
    try:
        run_command(["uv", "venv", TEST_VENV], "📦 Creating test environment")
    except subprocess.CalledProcessError:
        print("Failed to create test environment")
        return 1

    # Determine the Python executable path in the venv
    python_path = Path(TEST_VENV) / "bin" / "python"

    # Step 3: Install package from TestPyPI
    # Two-step: fetch the package itself from TestPyPI (no deps, since most deps
    # aren't on TestPyPI), then satisfy dependencies via the local wheel metadata.
    print("\n💾 Installing typer-extensions from TestPyPI")
    wheel_files = list(Path(DIST_DIR).glob("*.whl"))
    if not wheel_files:
        print("\n❌ No wheel file found in dist/ — run 'uv build' first.")
        return 1

    wheel_path = wheel_files[0]

    try:
        run_command(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python_path),
                "--index-url",
                TESTPYPI_URL,
                "--no-deps",
                f"{PACKAGE_NAME}=={EXPECTED_VERSION}",
            ],
            "Installing package from TestPyPI (no deps)",
        )
        run_command(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(python_path),
                str(wheel_path),
            ],
            "Installing dependencies from PyPI via local wheel metadata",
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Package installation from TestPyPI failed: {e}")
        print("\nℹ️ Note: Ensure the package has been published to TestPyPI first.")
        return 1

    # Step 4: Test import and version
    print("\n✅ Testing import and version")
    try:
        result = run_command(
            [
                str(python_path),
                "-c",
                f"import {PACKAGE_NAME.replace('-', '_')}; print({PACKAGE_NAME.replace('-', '_')}.__version__)",
            ],
            "Checking package version",
            capture_output=True,
        )
        installed_version = result.stdout.strip()
        if installed_version == EXPECTED_VERSION:
            print(
                f"✅ {PACKAGE_NAME} is installed with the expected version: {EXPECTED_VERSION}"
            )
        else:
            print(
                f"❌ {PACKAGE_NAME} version mismatch: expected {EXPECTED_VERSION}, got {installed_version}"
            )
            return 1
    except subprocess.CalledProcessError as e:
        print(f"❌ Version check failed: {e}")
        return 1

    # Step 5: Install pytest & run tests
    print("\n🧪 Running test suite\n")
    try:
        run_command(
            ["uv", "pip", "install", "--python", str(python_path), "pytest"],
            "Installing pytest",
        )
        run_command(
            [str(python_path), "-m", "pytest", "-v", "tests/"],
            "Running tests",
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return 1

    # Success
    print("\n✨ Pre-release validation complete!\n")
    return 0


if __name__ == "__main__":
    sys.exit(install_testpypi())

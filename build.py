#!/usr/bin/env python3
"""Build script for ISF Shader Renderer."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print("STDOUT:")
        print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    if result.returncode != 0:
        print(f"Error: {description} failed with return code {result.returncode}")
        sys.exit(result.returncode)

    print(f"Success: {description}")
    return result


def main():
    """Main build function."""
    print("Building ISF Shader Renderer...")

    # Clean previous builds
    print("\nCleaning previous builds...")
    for path in ["build", "dist", "*.egg-info"]:
        run_command(["rm", "-rf", path], f"Removing {path}")

    # Build the package
    print("\nBuilding package...")
    run_command([sys.executable, "-m", "build"], "Building package with build")

    # Show the built files
    print("\nBuilt files:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.glob("*"):
            print(f"  {file}")

    print("\nBuild completed successfully!")
    print("\nTo install the package:")
    print("  pip install dist/*.whl")
    print("\nTo install in development mode:")
    print("  pip install -e .")
    print("\nTo test the CLI:")
    print("  isf-shader-render --help")


if __name__ == "__main__":
    main()

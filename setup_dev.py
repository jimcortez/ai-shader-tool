#!/usr/bin/env python3
"""Development setup script for ISF Shader Renderer."""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("Setting up ISF Shader Renderer development environment...")
    print()
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Install the package in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command("pip install -e '.[dev]'", "Installing development dependencies"):
        sys.exit(1)
    
    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        print("Warning: Pre-commit hooks installation failed. Continuing...")
    
    # Create example directories
    Path("examples/output").mkdir(exist_ok=True)
    Path("examples/shaders").mkdir(exist_ok=True)
    
    # Run tests to verify installation
    if not run_command("pytest -v", "Running tests"):
        print("Warning: Tests failed. Please check the installation.")
    
    print()
    print("Setup completed! You can now:")
    print("  - Run 'isf-renderer --help' to see available commands")
    print("  - Run 'make help' to see available development tasks")
    print("  - Check examples/config.yaml for configuration examples")
    print("  - Run 'make run-example' to test with the example shader")


if __name__ == "__main__":
    main() 
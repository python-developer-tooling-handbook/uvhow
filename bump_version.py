#!/usr/bin/env python3
"""
Script to bump version in pyproject.toml and create git tag for deployment.

Usage:
    python bump_version.py patch    # 0.1.2 -> 0.1.3
    python bump_version.py minor    # 0.1.2 -> 0.2.0
    python bump_version.py major    # 0.1.2 -> 1.0.0
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Read current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Version not found in pyproject.toml")

    return match.group(1)


def bump_version(current_version, bump_type):
    """Bump version according to semantic versioning."""
    parts = current_version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current_version}")

    major, minor, patch = map(int, parts)

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Replace version line
    new_content = re.sub(
        r'^version = "[^"]+"', f'version = "{new_version}"', content, flags=re.MULTILINE
    )

    pyproject_path.write_text(new_content)
    print(f"✅ Updated pyproject.toml version to {new_version}")


def run_git_command(cmd):
    """Run git command and return result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr.strip()}")
        sys.exit(1)


def run_git_command_silent(cmd):
    """Run git command silently, return True if successful, False otherwise."""
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_git_status():
    """Check if git repo is clean."""
    status = run_git_command(["git", "status", "--porcelain"])
    if status:
        print(
            "❌ Git working directory is not clean. Please commit or stash changes first."
        )
        print("Uncommitted changes:")
        print(status)
        sys.exit(1)


def create_git_tag(version):
    """Create and push git tag."""
    tag_name = f"v{version}"

    # Check if tag already exists
    if run_git_command_silent(["git", "rev-parse", tag_name]):
        print(f"❌ Tag {tag_name} already exists")
        sys.exit(1)

    # Add and commit the version change
    run_git_command(["git", "add", "pyproject.toml"])
    run_git_command(["git", "commit", "-m", f"Bump version to {version}"])
    print("✅ Committed version bump")

    # Create and push tag
    run_git_command(["git", "tag", tag_name])
    print(f"✅ Created tag {tag_name}")

    # Push commits and tags
    run_git_command(["git", "push"])
    run_git_command(["git", "push", "--tags"])
    print(f"✅ Pushed tag {tag_name} to remote")
    print(f"🚀 GitHub Actions will now build and deploy version {version}")


def main():
    parser = argparse.ArgumentParser(description="Bump version and create git tag")
    parser.add_argument(
        "bump_type",
        choices=["patch", "minor", "major"],
        help="Type of version bump (patch, minor, or major)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    try:
        # Get current version
        current_version = get_current_version()
        new_version = bump_version(current_version, args.bump_type)

        print(f"📦 Current version: {current_version}")
        print(f"📦 New version: {new_version}")

        if args.dry_run:
            print("🧪 Dry run mode - no changes will be made")
            return

        # Check git status
        check_git_status()

        # Update version
        update_pyproject_toml(new_version)

        # Create git tag and push
        create_git_tag(new_version)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional


class UvInstallation(NamedTuple):
    """Information about a detected uv installation."""

    path: Path
    version: str
    method: str
    upgrade_command: str


def get_uv_version() -> Optional[str]:
    """Get the version of uv if it's installed."""
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_uv_installed_via_pip() -> bool:
    """Check if uv is installed via pip by checking pip list."""
    try:
        # Try python -m pip first (most reliable)
        result = subprocess.run(
            ["python", "-m", "pip", "show", "uv"],
            capture_output=True,
            text=True,
            check=True,
        )
        return "Name: uv" in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Fallback to python3 -m pip
            result = subprocess.run(
                ["python3", "-m", "pip", "show", "uv"],
                capture_output=True,
                text=True,
                check=True,
            )
            return "Name: uv" in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Final fallback to pip directly
                result = subprocess.run(
                    ["pip", "show", "uv"], capture_output=True, text=True, check=True
                )
                return "Name: uv" in result.stdout
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False


def detect_uv_installation() -> Optional[UvInstallation]:
    """Detect how uv was installed and return installation information."""
    # Check if uv is installed
    uv_path_str = shutil.which("uv")
    if not uv_path_str:
        return None

    uv_path = Path(uv_path_str).resolve()
    version = get_uv_version() or "unknown"

    # Check if uv is installed via pip for better detection accuracy
    is_pip_installed = is_uv_installed_via_pip()

    # Detect installation method based on path patterns
    # Use original path for pattern matching to avoid filesystem resolution issues
    path_str = uv_path_str

    # Check .local/bin/uv locations (could be standalone installer or user pip)
    if "/.local/bin/uv" in path_str and (
        path_str.startswith("/Users/") or path_str.startswith("/home/")
    ):
        if is_pip_installed:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="pip (user)",
                upgrade_command="pip install --upgrade --user uv",
            )
        return UvInstallation(
            path=uv_path,
            version=version,
            method="Standalone installer",
            upgrade_command="uv self update",
        )

    # Cargo
    if "/.cargo/bin/uv" in path_str:
        return UvInstallation(
            path=uv_path,
            version=version,
            method="Cargo",
            upgrade_command="cargo install --git https://github.com/astral-sh/uv uv --force",
        )

    # Homebrew
    if "/opt/homebrew/" in path_str or (
        "/usr/local/" in path_str and "Cellar" in path_str
    ):
        return UvInstallation(
            path=uv_path,
            version=version,
            method="Homebrew",
            upgrade_command="brew upgrade uv",
        )

    # pipx
    if "/pipx/venvs/uv/" in path_str:
        return UvInstallation(
            path=uv_path,
            version=version,
            method="pipx",
            upgrade_command="pipx upgrade uv",
        )

    # Virtual environment pip
    if any(
        venv in path_str for venv in ["/venv/bin/uv", "/env/bin/uv", "/.venv/bin/uv"]
    ):
        return UvInstallation(
            path=uv_path,
            version=version,
            method="pip (virtual environment)",
            upgrade_command="pip install --upgrade uv",
        )

    # System or user pip (fallback for other /bin/uv paths)
    if path_str.endswith("/bin/uv"):
        if "/usr/local/bin/uv" in path_str or "/usr/bin/uv" in path_str:
            # System-wide locations
            if is_pip_installed:
                return UvInstallation(
                    path=uv_path,
                    version=version,
                    method="pip (system)",
                    upgrade_command="sudo pip install --upgrade uv",
                )
        else:
            # Other locations - check if pip-installed
            if is_pip_installed:
                return UvInstallation(
                    path=uv_path,
                    version=version,
                    method="pip (user)",
                    upgrade_command="pip install --upgrade --user uv",
                )

    # Unknown method
    return UvInstallation(
        path=uv_path,
        version=version,
        method="Unknown",
        upgrade_command="uv self update",
    )


def print_installation_info(installation: UvInstallation) -> None:
    """Print formatted installation information."""
    print("🔍 uv installation detected")
    print()
    print(f"✅ Found uv: {installation.version}")
    print(f"📍 Location: {installation.path}")
    print()
    print(f"🎯 Installation method: {installation.method}")
    print(f"💡 To upgrade: {installation.upgrade_command}")

    if installation.method == "Unknown":
        print(f"📍 Path: {installation.path}")
        print("💡 Try: uv self update or reinstall with the standalone installer")


def main() -> None:
    """Main entry point for the uvhow CLI."""
    installation = detect_uv_installation()

    if installation is None:
        print("❌ uv is not installed or not in PATH")
        print("Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    print_installation_info(installation)

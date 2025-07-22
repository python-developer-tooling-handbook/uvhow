import os
import platform
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
    # Try multiple pip commands in order of preference
    pip_commands = [
        [sys.executable, "-m", "pip", "show", "uv"],  # Use current Python interpreter
        ["python", "-m", "pip", "show", "uv"],        # Standard python
        ["python3", "-m", "pip", "show", "uv"],       # python3 (Unix-like systems)
        ["pip", "show", "uv"],                        # Direct pip call
    ]

    # On Windows, also try py launcher
    if platform.system() == "Windows":
        pip_commands.insert(1, ["py", "-m", "pip", "show", "uv"])

    for cmd in pip_commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            if "Name: uv" in result.stdout:
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

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
    is_windows = platform.system() == "Windows"

    if is_windows:
        # Windows-specific detection
        path_str_lower = path_str.lower()

        # Windows Store Python (check first to avoid conflicts)
        if "\\microsoft\\windowsapps\\" in path_str_lower:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="pip (Windows Store Python)",
                upgrade_command="pip install --upgrade uv",
            )

        # Standalone installer
        if "\\appdata\\local\\programs\\uv\\" in path_str_lower:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="Standalone installer",
                upgrade_command="uv self update",
            )

        # Cargo on Windows
        if "\\.cargo\\bin\\" in path_str_lower:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="Cargo",
                upgrade_command="cargo install --git https://github.com/astral-sh/uv uv --force",
            )

        # Scoop
        if "\\scoop\\apps\\uv\\" in path_str_lower or "\\scoop\\shims\\" in path_str_lower:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="Scoop",
                upgrade_command="scoop update uv",
            )

        # Chocolatey
        if "\\chocolatey\\bin\\" in path_str_lower or "\\programdata\\chocolatey\\" in path_str_lower:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="Chocolatey",
                upgrade_command="choco upgrade uv",
            )

        # pipx on Windows
        if "\\pipx\\venvs\\uv\\" in path_str_lower:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="pipx",
                upgrade_command="pipx upgrade uv",
            )

        # Virtual environment pip on Windows
        if any(
            venv in path_str_lower for venv in ["\\venv\\scripts\\", "\\env\\scripts\\", "\\.venv\\scripts\\", "\\.env\\scripts\\"]
        ):
            return UvInstallation(
                path=uv_path,
                version=version,
                method="pip (virtual environment)",
                upgrade_command="pip install --upgrade uv",
            )

        # System Python on Windows (check for broader patterns)
        if any(pattern in path_str_lower for pattern in ["\\python39\\scripts\\", "\\python3\\scripts\\", "\\python\\scripts\\"]) and not "\\users\\" in path_str_lower:
            if is_pip_installed:
                return UvInstallation(
                    path=uv_path,
                    version=version,
                    method="pip (system)",
                    upgrade_command="pip install --upgrade uv",
                )

        # User Python installations (fallback for AppData and user paths)
        if ("\\appdata\\roaming\\python\\scripts\\" in path_str_lower or "\\users\\" in path_str_lower) and is_pip_installed:
            return UvInstallation(
                path=uv_path,
                version=version,
                method="pip (user)",
                upgrade_command="pip install --upgrade --user uv",
            )

    else:
        # Unix-like systems (Linux, macOS, etc.)

        # Check .local/bin/uv locations (could be standalone installer or user pip)
        if "/.local/bin/uv" in path_str:
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
            "/usr/local/" in path_str and ("Cellar" in path_str or "cellar" in path_str)
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
            venv in path_str for venv in ["/venv/bin/uv", "/env/bin/uv", "/.venv/bin/uv", "/.env/bin/uv"]
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
    try:
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
    except UnicodeEncodeError:
        # Fallback for Windows terminals that can't display emojis
        print("uv installation detected")
        print()
        print(f"Found uv: {installation.version}")
        print(f"Location: {installation.path}")
        print()
        print(f"Installation method: {installation.method}")
        print(f"To upgrade: {installation.upgrade_command}")

        if installation.method == "Unknown":
            print(f"Path: {installation.path}")
            print("Try: uv self update or reinstall with the standalone installer")


def main() -> None:
    """Main entry point for the uvhow CLI."""
    installation = detect_uv_installation()

    if installation is None:
        try:
            print("❌ uv is not installed or not in PATH")
        except UnicodeEncodeError:
            print("uv is not installed or not in PATH")
        print("Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    print_installation_info(installation)

# uvhow

Detect how [uv](https://github.com/astral-sh/uv) was installed and get upgrade instructions.

Works on **Windows**, **macOS**, and **Linux** with support for all major installation methods.

## Usage

Run with uvx (recommended):
```bash
uvx uvhow
```

Or install and run:
```bash
uv add uvhow
uvhow
```

## Example Output

```
🔍 uv installation detected

✅ Found uv: uv 0.8.0 (0b2357294 2025-07-17)
📍 Location: /Users/user/.local/bin/uv

🎯 Installation method: Standalone installer
💡 To upgrade: uv self update
```

## Supported Installation Methods

### Unix/Linux/macOS
- **Standalone installer** (`~/.local/bin/uv`) -> `uv self update`
- **Cargo** (`~/.cargo/bin/uv`) -> `cargo install --git https://github.com/astral-sh/uv uv --force`
- **Homebrew** (`/opt/homebrew/bin/uv`) -> `brew upgrade uv`
- **pipx** (`~/.local/share/pipx/venvs/uv/bin/uv`) -> `pipx upgrade uv`
- **pip (virtual environment)** -> `pip install --upgrade uv`
- **pip (system)** -> `sudo pip install --upgrade uv`
- **pip (user)** -> `pip install --upgrade --user uv`

### Windows
- **Standalone installer** (`%USERPROFILE%\AppData\Local\Programs\uv\uv.exe`) -> `uv self update`
- **Cargo** (`%USERPROFILE%\.cargo\bin\uv.exe`) -> `cargo install --git https://github.com/astral-sh/uv uv --force`
- **Scoop** (`%USERPROFILE%\scoop\apps\uv\current\uv.exe`) -> `scoop update uv`
- **Chocolatey** (`C:\ProgramData\chocolatey\bin\uv.exe`) -> `choco upgrade uv`
- **pipx** (`%USERPROFILE%\pipx\venvs\uv\Scripts\uv.exe`) -> `pipx upgrade uv`
- **pip (virtual environment)** -> `pip install --upgrade uv`
- **pip (system)** -> `pip install --upgrade uv`
- **pip (user)** -> `pip install --upgrade --user uv`
- **pip (Windows Store Python)** -> `pip install --upgrade uv`

## Programmatic Usage

```python
from uvhow import detect_uv_installation

installation = detect_uv_installation()
if installation:
    print(f"Method: {installation.method}")
    print(f"Upgrade: {installation.upgrade_command}")
```

## Development

### Setup

Install pre-commit hooks for code quality:

```bash
pip install pre-commit
pre-commit install
```

This will automatically:
- Remove trailing whitespace
- Fix end-of-file issues
- Format Python code with Black
- Sort imports with isort
- Validate YAML/TOML syntax
- Check for merge conflicts

### Releasing New Versions

Use the included version bump script to release new versions:

```bash
# Preview what will happen
python bump_version.py patch --dry-run

# Bump patch version (0.1.2 -> 0.1.3) and deploy
python bump_version.py patch

# Bump minor version (0.1.2 -> 0.2.0) and deploy
python bump_version.py minor

# Bump major version (0.1.2 -> 1.0.0) and deploy
python bump_version.py major
```

The script will:
1. Update the version in `pyproject.toml`
2. Commit the version change
3. Create a git tag (e.g., `v0.1.3`)
4. Push the tag to trigger GitHub Actions deployment to PyPI

**Requirements:**
- Clean git working directory (no uncommitted changes)
- Push access to the repository

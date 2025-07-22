# uvhow

Detect how [uv](https://github.com/astral-sh/uv) was installed and get upgrade instructions.

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
= uv installation detected

 Found uv: uv 0.8.0 (0b2357294 2025-07-17)
=Í Location: /Users/user/.local/bin/uv

<¯ Installation method: Standalone installer
=¡ To upgrade: uv self update
```

## Supported Installation Methods

- **Standalone installer** (`~/.local/bin/uv`) ’ `uv self update`
- **Cargo** (`~/.cargo/bin/uv`) ’ `cargo install --git https://github.com/astral-sh/uv uv --force`
- **Homebrew** (`/opt/homebrew/bin/uv`) ’ `brew upgrade uv`
- **pipx** (`~/.local/share/pipx/venvs/uv/bin/uv`) ’ `pipx upgrade uv`
- **pip (virtual environment)** ’ `pip install --upgrade uv`
- **pip (system)** ’ `sudo pip install --upgrade uv`
- **pip (user)** ’ `pip install --upgrade --user uv`

## Programmatic Usage

```python
from uvhow import detect_uv_installation

installation = detect_uv_installation()
if installation:
    print(f"Method: {installation.method}")
    print(f"Upgrade: {installation.upgrade_command}")
```
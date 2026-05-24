"""JSON save/load for pet state at ~/.terminal_pet/state.json."""

import json
import os
import tempfile
from pathlib import Path

from terminal_pet import config


def _save_path() -> Path:
    return Path(os.path.expanduser(config.SAVE_DIR)) / config.SAVE_FILE


def save_state(data: dict):
    """Atomically write state to JSON file."""
    path = _save_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file then rename for atomicity
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        # On Windows, we need to remove target first
        if path.exists():
            path.unlink()
        os.rename(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load_state() -> dict | None:
    """Load state from JSON file. Returns None if no saved state."""
    path = _save_path()
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

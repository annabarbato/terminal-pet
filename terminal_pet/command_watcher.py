"""Polls shell history files for commands that trigger pet reactions."""

import os
import re
import time
from pathlib import Path

from terminal_pet import config
from terminal_pet.state_machine import DogEvent


class CommandWatcher:
    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._last_poll = 0.0
        self._history_files = self._find_history_files()
        self._file_positions: dict[str, int] = {}
        self._patterns = {
            DogEvent.POSITIVE_COMMAND: [re.compile(p, re.IGNORECASE) for p in config.POSITIVE_COMMANDS],
            DogEvent.SCARY_COMMAND: [re.compile(p, re.IGNORECASE) for p in config.SCARY_COMMANDS],
            DogEvent.SHOO: [re.compile(p, re.IGNORECASE) for p in config.SHOO_COMMANDS],
        }
        # Initialize file positions to end of file (skip existing history)
        self._init_positions()

    def _find_history_files(self) -> list[str]:
        """Find shell history files on the system."""
        candidates = []
        home = Path.home()

        # Bash
        bash_hist = home / ".bash_history"
        if bash_hist.exists():
            candidates.append(str(bash_hist))

        # Zsh
        zsh_hist = home / ".zsh_history"
        if zsh_hist.exists():
            candidates.append(str(zsh_hist))

        # PowerShell (Windows)
        ps_hist = (
            home / "AppData" / "Roaming" / "Microsoft" / "Windows"
            / "PowerShell" / "PSReadLine" / "ConsoleHost_history.txt"
        )
        if ps_hist.exists():
            candidates.append(str(ps_hist))

        # PowerShell Core (cross-platform)
        ps_core = home / ".local" / "share" / "powershell" / "PSReadLine" / "ConsoleHost_history.txt"
        if ps_core.exists():
            candidates.append(str(ps_core))

        return candidates

    def _init_positions(self):
        """Set initial read positions to end of each history file."""
        for path in self._history_files:
            try:
                self._file_positions[path] = os.path.getsize(path)
            except OSError:
                self._file_positions[path] = 0

    def poll(self) -> DogEvent | None:
        """Check for new commands. Returns highest-priority event or None."""
        if not self._enabled:
            return None

        now = time.time()
        if now - self._last_poll < config.HISTORY_POLL_INTERVAL:
            return None
        self._last_poll = now

        new_lines = []
        for path in self._history_files:
            try:
                size = os.path.getsize(path)
                prev_pos = self._file_positions.get(path, 0)

                # File was truncated/rotated
                if size < prev_pos:
                    prev_pos = 0

                if size > prev_pos:
                    with open(path, "r", errors="replace") as f:
                        f.seek(prev_pos)
                        new_lines.extend(f.readlines())
                    self._file_positions[path] = size
            except OSError:
                continue

        # Check lines against patterns (priority: SHOO > SCARY > POSITIVE)
        for line in new_lines:
            line = line.strip()
            if not line:
                continue

            for event in [DogEvent.SHOO, DogEvent.SCARY_COMMAND, DogEvent.POSITIVE_COMMAND]:
                for pattern in self._patterns[event]:
                    if pattern.search(line):
                        return event

        return None

"""All timing, speed, and dimension constants."""

# Display
SPRITE_SIZE = 24          # 24x24 pixel sprites
FPS = 20                  # Main loop target
TICK_MS = 50              # 1000 / FPS

# Movement speeds (pixels per tick)
IDLE_DRIFT_SPEED = 0.3
RUNNING_SPEED = 3.0

# State timing (seconds)
IDLE_TIMEOUT = 30         # Idle -> Sleeping
DEATH_TIMEOUT = 7200      # 2 hours -> Dead
HAPPY_DURATION = 3.0      # Happy dance length
SCARED_FLINCH = 0.5       # Scared before running
RUN_RETURN_MIN = 3.0      # Min time before run ends
RUN_RETURN_MAX = 5.0      # Max time before run ends
APPEAR_DELAY = 10.0       # Seconds before dog first appears

# Animation
BLINK_INTERVAL = 4.0      # Seconds between blinks
BLINK_DURATION = 0.15     # How long blink lasts

# Per-state FPS overrides
STATE_FPS = {
    "IDLE": 4,
    "HAPPY": 6,
    "SCARED": 8,
    "RUNNING": 8,
    "SLEEPING": 2,
    "DEAD": 1,
}

# Persistence
SAVE_INTERVAL = 30        # Auto-save every N seconds
SAVE_DIR = "~/.terminal_pet"
SAVE_FILE = "state.json"

# Command watcher
HISTORY_POLL_INTERVAL = 1.0  # Seconds between history checks

# Command patterns
POSITIVE_COMMANDS = [
    r"git\s+commit",
    r"git\s+push",
    r"npm\s+publish",
    r"cargo\s+publish",
    r"pytest.*passed",
    r"make\s+deploy",
    r"docker\s+push",
    r"pip\s+install",
    r"npm\s+install",
    r"brew\s+install",
]

SCARY_COMMANDS = [
    r"rm\s+-rf",
    r"rm\s+-r",
    r"sudo\s+rm",
    r"DROP\s+TABLE",
    r"format\s+[cC]:",
    r"del\s+/[sS]",
    r"git\s+reset\s+--hard",
    r":(){ :\|:& };:",
    r"mkfs\.",
    r"dd\s+if=",
]

SHOO_COMMANDS = [
    r"\bshoo\b",
    r"\bgo\s+away\b",
    r"\bscram\b",
]

# Minimum terminal size
MIN_TERM_WIDTH = 24
MIN_TERM_HEIGHT = 14

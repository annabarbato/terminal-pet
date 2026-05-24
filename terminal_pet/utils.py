"""Color conversion utilities."""


def rgb_to_256(r: int, g: int, b: int) -> int:
    """Convert RGB to xterm-256 color index using 6x6x6 cube."""
    if r == g == b:
        # Grayscale ramp (indices 232-255)
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round((r - 8) / 247 * 24) + 232

    # 6x6x6 color cube (indices 16-231)
    ri = round(r / 255 * 5)
    gi = round(g / 255 * 5)
    bi = round(b / 255 * 5)
    return 16 + 36 * ri + 6 * gi + bi


# Standard 16-color palette RGB values
_ANSI_16 = [
    (0, 0, 0),       # 0 black
    (128, 0, 0),     # 1 red
    (0, 128, 0),     # 2 green
    (128, 128, 0),   # 3 yellow
    (0, 0, 128),     # 4 blue
    (128, 0, 128),   # 5 magenta
    (0, 128, 128),   # 6 cyan
    (192, 192, 192), # 7 white
    (128, 128, 128), # 8 bright black
    (255, 0, 0),     # 9 bright red
    (0, 255, 0),     # 10 bright green
    (255, 255, 0),   # 11 bright yellow
    (0, 0, 255),     # 12 bright blue
    (255, 0, 255),   # 13 bright magenta
    (0, 255, 255),   # 14 bright cyan
    (255, 255, 255), # 15 bright white
]


def rgb_to_16(r: int, g: int, b: int) -> int:
    """Convert RGB to nearest ANSI 16-color index using Euclidean distance."""
    best = 0
    best_dist = float("inf")
    for i, (cr, cg, cb) in enumerate(_ANSI_16):
        dist = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if dist < best_dist:
            best_dist = dist
            best = i
    return best

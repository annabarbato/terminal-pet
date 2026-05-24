"""Half-block rendering engine using blessed terminal library."""

import hashlib

from blessed import Terminal

from terminal_pet.utils import rgb_to_256, rgb_to_16


class SpriteRenderer:
    def __init__(self, term: Terminal):
        self.term = term
        self._color_mode = self._detect_color_mode()
        self._last_frame_hash = None

    def _detect_color_mode(self) -> str:
        """Detect terminal color capability."""
        t = self.term
        if t.number_of_colors >= 16777216:
            return "truecolor"
        elif t.number_of_colors >= 256:
            return "256"
        else:
            return "16"

    def _color_fg(self, r: int, g: int, b: int) -> str:
        if self._color_mode == "truecolor":
            return self.term.color_rgb(r, g, b)
        elif self._color_mode == "256":
            return self.term.color(rgb_to_256(r, g, b))
        else:
            return self.term.color(rgb_to_16(r, g, b))

    def _color_bg(self, r: int, g: int, b: int) -> str:
        if self._color_mode == "truecolor":
            return self.term.on_color_rgb(r, g, b)
        elif self._color_mode == "256":
            return self.term.on_color(rgb_to_256(r, g, b))
        else:
            return self.term.on_color(rgb_to_16(r, g, b))

    def render_sprite(self, frame: list, x: int, y: int) -> str:
        """Render a sprite frame at position (x, y) using half-block characters.

        frame: 2D list [row][col] of (r,g,b)|None, must have even number of rows.
        Returns string to print.
        """
        frame_hash = hashlib.md5(str((frame, x, y)).encode()).hexdigest()
        if frame_hash == self._last_frame_hash:
            return ""
        self._last_frame_hash = frame_hash

        t = self.term
        normal = t.normal
        half_block = "\u2580"  # Upper half block
        lines = []

        rows = len(frame)
        cols = len(frame[0]) if rows > 0 else 0

        for pair_idx in range(0, rows, 2):
            top_row = frame[pair_idx]
            bot_row = frame[pair_idx + 1] if pair_idx + 1 < rows else [None] * cols
            screen_y = y + pair_idx // 2

            if screen_y < 0 or screen_y >= t.height:
                continue

            line_parts = []
            col_start = None

            for col_idx in range(cols):
                screen_x = x + col_idx
                if screen_x < 0 or screen_x >= t.width:
                    continue

                top = top_row[col_idx] if col_idx < len(top_row) else None
                bot = bot_row[col_idx] if col_idx < len(bot_row) else None

                if top is None and bot is None:
                    continue

                if col_start is None:
                    col_start = screen_x

                # Position cursor for this cell
                pos = t.move_xy(screen_x, screen_y)

                if top is not None and bot is not None:
                    # Both pixels have color: fg=top, bg=bot, char=upper half block
                    fg = self._color_fg(*top)
                    bg = self._color_bg(*bot)
                    line_parts.append(f"{pos}{fg}{bg}{half_block}{normal}")
                elif top is not None:
                    # Only top pixel: fg=top, default bg, upper half block
                    fg = self._color_fg(*top)
                    line_parts.append(f"{pos}{fg}{half_block}{normal}")
                else:
                    # Only bottom pixel: use lower half block with fg=bot
                    fg = self._color_fg(*bot)
                    line_parts.append(f"{pos}{fg}\u2584{normal}")

            lines.extend(line_parts)

        return "".join(lines)

    def clear_rect(self, x: int, y: int, width: int, height_rows: int) -> str:
        """Clear a rectangular area (in terminal rows)."""
        t = self.term
        parts = []
        for row in range(height_rows):
            screen_y = y + row
            if 0 <= screen_y < t.height:
                clamped_x = max(0, x)
                clamped_w = min(width, t.width - clamped_x)
                if clamped_w > 0:
                    parts.append(t.move_xy(clamped_x, screen_y) + " " * clamped_w)
        return "".join(parts)

    def invalidate(self):
        """Force next render to redraw."""
        self._last_frame_hash = None

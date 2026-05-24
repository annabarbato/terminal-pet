"""Animation controller: frame cycling, blink timing, per-state FPS."""

import time

from terminal_pet import config
from terminal_pet.state_machine import DogState
from terminal_pet.sprites import get_frames, get_blink_frame


class AnimationController:
    def __init__(self):
        self._state = DogState.IDLE
        self._frames = get_frames(DogState.IDLE)
        self._frame_index = 0
        self._last_frame_time = time.time()
        self._last_blink_time = time.time()
        self._blinking = False
        self._blink_start = 0.0

    def set_state(self, state: DogState):
        """Switch to a new animation state, resetting frame index."""
        if state == self._state:
            return
        self._state = state
        self._frames = get_frames(state)
        self._frame_index = 0
        self._last_frame_time = time.time()

    def update(self) -> list:
        """Advance animation and return current frame to render."""
        now = time.time()
        state_name = self._state.name
        fps = config.STATE_FPS.get(state_name, 4)
        frame_duration = 1.0 / fps

        # Advance frame if enough time has passed
        if now - self._last_frame_time >= frame_duration and len(self._frames) > 0:
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            self._last_frame_time = now

        # Handle blinking for idle state
        if self._state == DogState.IDLE:
            if not self._blinking:
                if now - self._last_blink_time >= config.BLINK_INTERVAL:
                    self._blinking = True
                    self._blink_start = now
                    self._last_blink_time = now
            else:
                if now - self._blink_start >= config.BLINK_DURATION:
                    self._blinking = False

            if self._blinking:
                blink = get_blink_frame(self._state)
                if blink is not None:
                    return blink

        if len(self._frames) == 0:
            return []
        return self._frames[self._frame_index]

    @property
    def frame_index(self) -> int:
        return self._frame_index

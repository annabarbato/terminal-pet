"""Dog state machine with enum states, events, and transition table."""

import random
import time
from enum import Enum, auto

from terminal_pet import config


class DogState(Enum):
    IDLE = auto()
    HAPPY = auto()
    SCARED = auto()
    RUNNING = auto()
    SLEEPING = auto()
    DEAD = auto()


class DogEvent(Enum):
    POSITIVE_COMMAND = auto()
    SCARY_COMMAND = auto()
    SHOO = auto()
    IDLE_TIMEOUT = auto()
    DEATH_TIMEOUT = auto()
    ANIMATION_COMPLETE = auto()
    RETURN_FROM_RUN = auto()
    WAKE_UP = auto()


# Transition table: (current_state, event) -> next_state
_TRANSITIONS = {
    (DogState.IDLE, DogEvent.POSITIVE_COMMAND): DogState.HAPPY,
    (DogState.IDLE, DogEvent.SCARY_COMMAND): DogState.SCARED,
    (DogState.IDLE, DogEvent.SHOO): DogState.RUNNING,
    (DogState.IDLE, DogEvent.IDLE_TIMEOUT): DogState.SLEEPING,
    (DogState.IDLE, DogEvent.DEATH_TIMEOUT): DogState.DEAD,
    (DogState.HAPPY, DogEvent.ANIMATION_COMPLETE): DogState.IDLE,
    (DogState.HAPPY, DogEvent.SCARY_COMMAND): DogState.SCARED,
    (DogState.SCARED, DogEvent.ANIMATION_COMPLETE): DogState.RUNNING,
    (DogState.RUNNING, DogEvent.RETURN_FROM_RUN): DogState.IDLE,
    (DogState.SLEEPING, DogEvent.WAKE_UP): DogState.IDLE,
    (DogState.SLEEPING, DogEvent.POSITIVE_COMMAND): DogState.IDLE,
    (DogState.SLEEPING, DogEvent.SCARY_COMMAND): DogState.SCARED,
    (DogState.SLEEPING, DogEvent.SHOO): DogState.RUNNING,
    (DogState.SLEEPING, DogEvent.DEATH_TIMEOUT): DogState.DEAD,
}


class DogStateMachine:
    def __init__(self):
        self.state = DogState.IDLE
        self.state_entered_at = time.time()
        self.last_interaction_at = time.time()
        self._run_return_time = 0.0

    def handle_event(self, event: DogEvent) -> DogState | None:
        """Process an event. Returns new state if transition occurred, else None."""
        key = (self.state, event)
        new_state = _TRANSITIONS.get(key)
        if new_state is None:
            return None
        self._enter_state(new_state)
        return new_state

    def _enter_state(self, new_state: DogState):
        self.state = new_state
        self.state_entered_at = time.time()
        if new_state == DogState.RUNNING:
            self._run_return_time = time.time() + random.uniform(
                config.RUN_RETURN_MIN, config.RUN_RETURN_MAX
            )
        if new_state not in (DogState.SLEEPING, DogState.DEAD):
            self.last_interaction_at = time.time()

    def check_timers(self) -> DogEvent | None:
        """Check time-based transitions. Returns event if one should fire."""
        now = time.time()
        elapsed_in_state = now - self.state_entered_at
        time_since_interaction = now - self.last_interaction_at

        if self.state == DogState.IDLE:
            if time_since_interaction >= config.DEATH_TIMEOUT:
                return DogEvent.DEATH_TIMEOUT
            if elapsed_in_state >= config.IDLE_TIMEOUT:
                return DogEvent.IDLE_TIMEOUT

        elif self.state == DogState.SLEEPING:
            if time_since_interaction >= config.DEATH_TIMEOUT:
                return DogEvent.DEATH_TIMEOUT

        elif self.state == DogState.HAPPY:
            if elapsed_in_state >= config.HAPPY_DURATION:
                return DogEvent.ANIMATION_COMPLETE

        elif self.state == DogState.SCARED:
            if elapsed_in_state >= config.SCARED_FLINCH:
                return DogEvent.ANIMATION_COMPLETE

        elif self.state == DogState.RUNNING:
            if now >= self._run_return_time:
                return DogEvent.RETURN_FROM_RUN

        return None

    def to_dict(self) -> dict:
        return {
            "state": self.state.name,
            "state_entered_at": self.state_entered_at,
            "last_interaction_at": self.last_interaction_at,
        }

    def load_dict(self, data: dict):
        try:
            self.state = DogState[data["state"]]
        except KeyError:
            self.state = DogState.IDLE
        self.state_entered_at = data.get("state_entered_at", time.time())
        self.last_interaction_at = data.get("last_interaction_at", time.time())
        # Check if should be dead
        if time.time() - self.last_interaction_at >= config.DEATH_TIMEOUT:
            self.state = DogState.DEAD

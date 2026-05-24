"""Sprite registry mapping DogState to frame lists."""

from terminal_pet.state_machine import DogState


def get_frames(state: DogState) -> list:
    """Get animation frames for a given state. Lazy import to avoid circular deps."""
    if state == DogState.IDLE:
        from terminal_pet.sprites.idle import FRAMES
        return FRAMES
    elif state == DogState.HAPPY:
        from terminal_pet.sprites.happy import FRAMES
        return FRAMES
    elif state == DogState.SCARED:
        from terminal_pet.sprites.scared import FRAMES
        return FRAMES
    elif state == DogState.RUNNING:
        from terminal_pet.sprites.running import FRAMES
        return FRAMES
    elif state == DogState.SLEEPING:
        from terminal_pet.sprites.sleeping import FRAMES
        return FRAMES
    elif state == DogState.DEAD:
        from terminal_pet.sprites.dead import FRAMES
        return FRAMES
    return []


def get_blink_frame(state: DogState):
    """Get blink variant frame if available."""
    if state == DogState.IDLE:
        from terminal_pet.sprites.idle import BLINK_FRAME
        return BLINK_FRAME
    return None

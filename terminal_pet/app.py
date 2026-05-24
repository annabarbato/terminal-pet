"""Terminal pet: background animation process for shell overlay."""

import argparse
import os
import random
import signal
import sys
import time

from terminal_pet import config
from terminal_pet.animation import AnimationController
from terminal_pet.command_watcher import CommandWatcher
from terminal_pet.persistence import save_state, load_state
from terminal_pet.state_machine import DogState, DogEvent, DogStateMachine


def _run_animate(args):
    """Background animation loop. Writes directly to /dev/tty."""
    from blessed import Terminal
    from terminal_pet.renderer import SpriteRenderer

    # Write directly to terminal device so we don't interfere with shell stdout
    tty = None
    if sys.platform == "win32":
        os.system("")  # Enable VT100 sequences
        try:
            tty = open("CONOUT$", "w", encoding="utf-8", errors="replace")
        except OSError:
            pass
    if tty is None:
        try:
            tty = open("/dev/tty", "w", encoding="utf-8", errors="replace")
        except OSError:
            tty = sys.stdout
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    term = Terminal(stream=tty)
    renderer = SpriteRenderer(term)
    animator = AnimationController()
    sm = DogStateMachine()
    watcher = CommandWatcher(enabled=not args.no_history)

    direction = 1
    x = float((term.width - config.SPRITE_SIZE) // 2)

    if not args.reset:
        data = load_state()
        if data:
            sm.load_dict(data.get("state_machine", {}))
            x = float(data.get("x", x))
            direction = data.get("direction", 1)
            animator.set_state(sm.state)

    dog_h = config.SPRITE_SIZE // 2
    prev_ix, prev_iy = -1, -1
    last_save = time.time()
    running = True

    def stop(sig, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    while running:
        try:
            iy = term.height - dog_h
            sw = config.SPRITE_SIZE

            # State machine timers
            timer_event = sm.check_timers()
            if timer_event:
                result = sm.handle_event(timer_event)
                if result:
                    animator.set_state(result)

            # Command history polling
            cmd_event = watcher.poll()
            if cmd_event:
                result = sm.handle_event(cmd_event)
                if result:
                    animator.set_state(result)
                    if result == DogState.RUNNING:
                        direction = random.choice([-1, 1])

            # Movement
            if sm.state == DogState.IDLE:
                x += config.IDLE_DRIFT_SPEED * direction
            elif sm.state == DogState.RUNNING:
                x += config.RUNNING_SPEED * direction

            max_x = max(0, term.width - sw)
            if x <= 0:
                x = 0
                direction = 1
            elif x >= max_x:
                x = max_x
                direction = -1

            ix = int(x)

            # Render with cursor save/restore
            frame = animator.update()
            if frame:
                parts = ["\0337"]  # DEC save cursor

                if ix != prev_ix or iy != prev_iy:
                    if prev_ix >= 0:
                        parts.append(renderer.clear_rect(prev_ix, prev_iy, sw, dog_h))
                    renderer.invalidate()

                output = renderer.render_sprite(frame, ix, iy)
                if output:
                    parts.append(output)

                parts.append("\0338")  # DEC restore cursor

                tty.write("".join(parts))
                tty.flush()

                prev_ix, prev_iy = ix, iy

            # Auto-save
            if time.time() - last_save >= config.SAVE_INTERVAL:
                save_state({"state_machine": sm.to_dict(), "x": x, "direction": direction})
                last_save = time.time()

            time.sleep(config.TICK_MS / 1000.0)

        except (BrokenPipeError, OSError):
            break
        except Exception:
            time.sleep(0.1)

    # Cleanup: save and clear dog area
    try:
        save_state({"state_machine": sm.to_dict(), "x": x, "direction": direction})
        if prev_ix >= 0:
            tty.write(renderer.clear_rect(prev_ix, prev_iy, sw, dog_h))
            tty.flush()
    except Exception:
        pass

    try:
        tty.close()
    except Exception:
        pass


def main():
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(description="Terminal Pet")
    parser.add_argument("--reset", action="store_true", help="Reset pet state")
    parser.add_argument("--no-history", action="store_true", help="Disable history watching")
    parser.add_argument("--debug", action="store_true", help="Show debug info")
    parser.add_argument("--animate", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.animate:
        _run_animate(args)
    else:
        pet_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")).replace(os.sep, "/")
        print("Setup: add ONE line to your shell profile, then restart your terminal.\n")
        print(f"  PowerShell (add to $PROFILE):  . {pet_dir}/pet.ps1")
        print(f"  Bash (add to ~/.bashrc):       source {pet_dir}/pet.sh\n")
        print("Then type 'pet' to start, 'pet-stop' to dismiss.")


if __name__ == "__main__":
    main()

#!/bin/bash
# Source this file to get `pet` and `pet-stop` commands.
# Add to ~/.bashrc:  source ~/terminal-pet/pet.sh

pet() {
    # Kill existing pet if any
    [ -n "$__PET_PID" ] && kill "$__PET_PID" 2>/dev/null

    local lines=$(tput lines)
    local dog_rows=13
    local usable=$((lines - dog_rows))

    # Reserve bottom rows for the dog
    printf '\033[1;%dr' "$usable"
    printf '\033[%d;1H' "$usable"

    # Start animation in background
    python -m terminal_pet --animate "$@" &
    __PET_PID=$!
    disown "$__PET_PID" 2>/dev/null

    # Auto-cleanup when shell exits
    trap '__pet_cleanup' EXIT

    echo "Pet is here! Type 'pet-stop' to dismiss."
}

__pet_cleanup() {
    [ -n "$__PET_PID" ] && kill "$__PET_PID" 2>/dev/null
    wait "$__PET_PID" 2>/dev/null
    printf '\033[1;%dr' "$(tput lines)"
    printf '\033[%d;1H\n' "$(tput lines)"
    unset __PET_PID
}

pet-stop() {
    __pet_cleanup
    trap - EXIT
    clear
}

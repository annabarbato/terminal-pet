# Source this in your PowerShell profile to get `pet` and `pet-stop` commands.
# Add to $PROFILE:  . ~/terminal-pet/pet.ps1

function pet {
    param([switch]$Reset, [switch]$NoHistory)

    # Kill existing pet if running
    if ($global:__PetProc -and !$global:__PetProc.HasExited) {
        Stop-Process -Id $global:__PetProc.Id -ErrorAction SilentlyContinue
    }

    $h = $Host.UI.RawUI.WindowSize.Height
    $usable = $h - 13
    $esc = [char]27

    # Reserve bottom 13 rows for the dog
    [Console]::Write("${esc}[1;${usable}r${esc}[${usable};1H")

    # Build args
    $pyArgs = "-m terminal_pet --animate"
    if ($Reset) { $pyArgs += " --reset" }
    if ($NoHistory) { $pyArgs += " --no-history" }

    # Start animation in background (same console window)
    $global:__PetProc = Start-Process -FilePath "python" -ArgumentList $pyArgs -NoNewWindow -PassThru

    Write-Host "Pet is here! Type 'pet-stop' to dismiss."
}

function pet-stop {
    if ($global:__PetProc -and !$global:__PetProc.HasExited) {
        Stop-Process -Id $global:__PetProc.Id -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 200
    }

    # Restore full terminal
    $h = $Host.UI.RawUI.WindowSize.Height
    $esc = [char]27
    [Console]::Write("${esc}[1;${h}r${esc}[${h};1H")
    Clear-Host

    $global:__PetProc = $null
}

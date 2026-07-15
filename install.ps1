# Install agent config templates to the user's home directory (Windows).
# Usage: powershell -ExecutionPolicy Bypass -File .\install.ps1
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path

function Install-ConfigFile {
    param([string]$Source, [string]$Dest)
    $destDir = Split-Path -Parent $Dest
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }
    if (Test-Path $Dest) {
        $srcHash = (Get-FileHash $Source).Hash
        $dstHash = (Get-FileHash $Dest).Hash
        if ($srcHash -eq $dstHash) {
            Write-Host "  unchanged: $Dest"
            return
        }
        Write-Host ""
        Write-Host "--- existing file differs: $Dest ---"
        Compare-Object -ReferenceObject (Get-Content $Dest) -DifferenceObject (Get-Content $Source) |
            Format-Table -AutoSize | Out-String | Write-Host
        try {
            $answer = Read-Host "  overwrite? (y/N)"
        } catch {
            # Non-interactive session: never overwrite silently.
            Write-Host "  non-interactive, keeping existing: $Dest"
            return
        }
        if ($answer -ne "y") {
            Write-Host "  skipped: $Dest"
            return
        }
    }
    Copy-Item -Path $Source -Destination $Dest -Force
    Write-Host "  installed: $Dest"
}

Write-Host "Installing Claude Code settings..."
Install-ConfigFile "$repo\claude\user-settings.json" "$env:USERPROFILE\.claude\settings.json"

# NOTE: ~/.codex/config.toml is managed by the Codex app itself (plugins, trusted
# projects, MCP servers). Never copy over it. Apply codex\safety-snippet.toml by hand.
Write-Host "Installing Codex CLI profile (config.toml is NOT touched)..."
Install-ConfigFile "$repo\codex\readonly.config.toml" "$env:USERPROFILE\.codex\readonly.config.toml"

Write-Host ""
Write-Host "Done. Restart agent sessions for changes to take effect."

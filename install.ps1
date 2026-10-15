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
        # Mirror install.sh's `[ ! -t 0 ]` check: with redirected stdin Read-Host
        # blocks forever instead of throwing, so detect it up front.
        if ([Console]::IsInputRedirected -or -not [Environment]::UserInteractive) {
            Write-Host "  non-interactive, keeping existing: $Dest"
            return
        }
        Write-Host ""
        Write-Host "--- existing file differs: $Dest ---"
        # Get-Content defaults to the OEM code page here (cp932 on Japanese Windows),
        # which renders UTF-8 config files as mojibake. Read both sides as UTF-8.
        # Print line by line as well: Format-Table truncated the long lines.
        $existingLines = Get-Content $Dest   -Encoding UTF8
        $incomingLines = Get-Content $Source -Encoding UTF8
        Compare-Object -ReferenceObject $existingLines -DifferenceObject $incomingLines |
            ForEach-Object {
                $tag = if ($_.SideIndicator -eq "=>") { "new     " } else { "existing" }
                Write-Host ("  [$tag] " + $_.InputObject)
            }
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
# Claude Code reads settings.json, CLAUDE.md and skills/ from the directory named by
# CLAUDE_CONFIG_DIR, defaulting to ~/.claude. A second account (a separate login under a
# separate CLAUDE_CONFIG_DIR) therefore reads a different copy of both files, and gets no
# safety settings at all unless they are installed there too.
$claudeDirs = @("$env:USERPROFILE\.claude")
# Extra config dirs are opt-in per machine: listed here, but only used when the directory
# already exists. Create the directory to start managing it; machines without it are
# unaffected.
foreach ($extra in @("$env:USERPROFILE\.claude-work")) {
    if (Test-Path $extra) { $claudeDirs += $extra }
}
foreach ($dir in $claudeDirs) {
    Install-ConfigFile "$repo\claude\user-settings.json" "$dir\settings.json"
    Install-ConfigFile "$repo\claude\CLAUDE.md" "$dir\CLAUDE.md"
}

# Skills: one folder per skill, SKILL.md inside. The body is loaded only when the
# skill is invoked, so procedures live here instead of bloating CLAUDE.md. Installed
# into every config dir, like CLAUDE.md.
Write-Host "Installing Claude Code skills..."
Get-ChildItem "$repo\claude\skills" -Directory | ForEach-Object {
    $skill = $_
    foreach ($dir in $claudeDirs) {
        Install-ConfigFile "$($skill.FullName)\SKILL.md" "$dir\skills\$($skill.Name)\SKILL.md"
    }
}

# NOTE: ~/.codex/config.toml is managed by the Codex app itself (plugins, trusted
# projects, MCP servers). Never copy over it. Apply codex\safety-snippet.toml by hand.
Write-Host "Installing Codex CLI profile (config.toml is NOT touched)..."
Install-ConfigFile "$repo\codex\readonly.config.toml" "$env:USERPROFILE\.codex\readonly.config.toml"
Install-ConfigFile "$repo\codex\AGENTS.md" "$env:USERPROFILE\.codex\AGENTS.md"

Write-Host ""
Write-Host "Checking for a trash command (agents use it instead of rm; see claude\CLAUDE.md)..."
if (Get-Command trash -ErrorAction SilentlyContinue) {
    Write-Host "  trash: found"
} else {
    Write-Host "  trash: NOT found. Recommended: 'npm install -g trash-cli' (moves files to the Recycle Bin)."
    Write-Host "  Until installed, agents fall back to moving files into ~\.agent-trash\."
}

Write-Host ""
Write-Host "Done. Restart agent sessions for changes to take effect."

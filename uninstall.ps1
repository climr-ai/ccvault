<#
.SYNOPSIS
    CCVault Uninstaller
.DESCRIPTION
    Run: irm https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/uninstall.ps1 | iex
#>

$ErrorActionPreference = "Stop"

# Colors and formatting
function Write-Step { param($msg) Write-Host "`n>> " -NoNewline -ForegroundColor Cyan; Write-Host $msg }
function Write-Success { param($msg) Write-Host "   [OK] " -NoNewline -ForegroundColor Green; Write-Host $msg }
function Write-Info { param($msg) Write-Host "   " -NoNewline; Write-Host $msg -ForegroundColor Gray }
function Write-Warn { param($msg) Write-Host "   [!] " -NoNewline -ForegroundColor Yellow; Write-Host $msg }

# Banner
Write-Host @"

   ██████╗ ██████╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
  ██╔════╝██╔════╝██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
  ██║     ██║     ██║   ██║███████║██║   ██║██║     ██║
  ██║     ██║     ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║
  ╚██████╗╚██████╗ ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║
   ╚═════╝ ╚═════╝  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝

                    Uninstaller

"@ -ForegroundColor Magenta

Write-Host "  We're sorry to see you go!" -ForegroundColor White
Write-Host ""

# Check if ccvault is installed
Write-Step "Checking installation..."
$ccvaultCmd = Get-Command ccvault -ErrorAction SilentlyContinue
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
$uvToolList = if ($uvCmd) { & uv tool list 2>$null } else { "" }

if ($ccvaultCmd -or ($uvToolList -match "ccvault")) {
    Write-Success "CCVault installation found"
} else {
    Write-Warn "CCVault doesn't appear to be installed"
    Write-Host ""
    exit 0
}

# Data directories
$ConfigDir = "$env:LOCALAPPDATA\dnd-manager"
$DataDir = "$env:LOCALAPPDATA\dnd-manager"

# Alternative locations (platformdirs may use these)
$AltConfigDir = "$env:APPDATA\dnd\dnd-manager"
$AltDataDir = "$env:LOCALAPPDATA\dnd\dnd-manager"

# Check for character data
$CharCount = 0
$CharLocation = ""

foreach ($dir in @("$DataDir\characters", "$AltDataDir\characters")) {
    if (Test-Path $dir) {
        $chars = Get-ChildItem -Path $dir -Filter "*.yaml" -ErrorAction SilentlyContinue
        if ($chars) {
            $CharCount = $chars.Count
            $CharLocation = $dir
            break
        }
    }
}

if ($CharCount -gt 0) {
    Write-Host ""
    Write-Host "  You have $CharCount character(s) saved." -ForegroundColor Yellow
    Write-Host "  Location: $CharLocation" -ForegroundColor Gray
    Write-Host ""
}

# Confirm uninstall
Write-Host "  What would you like to remove?" -ForegroundColor White
Write-Host ""
Write-Host "  1) CCVault only (keep your characters and settings)"
Write-Host "  2) Everything (CCVault + characters + settings)"
Write-Host "  3) Cancel"
Write-Host ""
$Choice = Read-Host "  Choose [1/2/3]"

switch ($Choice) {
    "1" {
        $RemoveData = $false
    }
    "2" {
        $RemoveData = $true
        Write-Host ""
        Write-Host "  This will permanently delete all your characters and settings!" -ForegroundColor Yellow
        $Confirm = Read-Host "  Are you sure? (y/N)"
        if ($Confirm.ToLower() -ne "y") {
            Write-Host ""
            Write-Host "  Uninstall cancelled. Your data is safe." -ForegroundColor Green
            exit 0
        }
    }
    default {
        Write-Host ""
        Write-Host "  Uninstall cancelled." -ForegroundColor Green
        exit 0
    }
}

# Uninstall ccvault
Write-Step "Removing CCVault..."
if ($uvCmd) {
    try {
        & uv tool uninstall ccvault 2>$null
        Write-Success "CCVault removed"
    } catch {
        Write-Warn "CCVault was not installed via uv tool"
    }
} else {
    Write-Warn "uv not found - CCVault may need manual removal"
}

# Remove data if requested
if ($RemoveData) {
    Write-Step "Removing data..."

    foreach ($dir in @($DataDir, $ConfigDir, $AltDataDir, $AltConfigDir)) {
        if (Test-Path $dir) {
            Remove-Item -Path $dir -Recurse -Force
            Write-Success "Removed: $dir"
        }
    }
}

# Success message
Write-Host @"

  ╔════════════════════════════════════════════════════════════╗
  ║                                                            ║
  ║   CCVault has been uninstalled.                            ║
  ║                                                            ║
  ║   Thank you for trying CCVault!                            ║
  ║                                                            ║
  ║   If you have feedback, we'd love to hear it:              ║
  ║   https://github.com/jaredgiosinuff/dnd-manager/issues     ║
  ║                                                            ║
  ║   To reinstall anytime:                                    ║
  ║   irm https://git.io/ccvault-win | iex                     ║
  ║                                                            ║
  ╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

if (-not $RemoveData) {
    Write-Host "  Your characters are still saved at: $CharLocation" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "  May your future adventures be legendary!" -ForegroundColor Cyan
Write-Host ""

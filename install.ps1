<#
.SYNOPSIS
    CCVault Installer - D&D Character Manager
.DESCRIPTION
    One-line install: irm https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/install.ps1 | iex
#>

$ErrorActionPreference = "Stop"

# Colors and formatting
function Write-Step { param($msg) Write-Host "`n>> " -NoNewline -ForegroundColor Cyan; Write-Host $msg }
function Write-Success { param($msg) Write-Host "   [OK] " -NoNewline -ForegroundColor Green; Write-Host $msg }
function Write-Info { param($msg) Write-Host "   " -NoNewline; Write-Host $msg -ForegroundColor Gray }
function Write-Warn { param($msg) Write-Host "   [!] " -NoNewline -ForegroundColor Yellow; Write-Host $msg }

# ASCII Banner
Write-Host @"

   ██████╗ ██████╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
  ██╔════╝██╔════╝██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
  ██║     ██║     ██║   ██║███████║██║   ██║██║     ██║
  ██║     ██║     ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║
  ╚██████╗╚██████╗ ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║
   ╚═════╝ ╚═════╝  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝

        D&D Character Manager - CLI Master Race

"@ -ForegroundColor Magenta

Write-Host "  The world's finest CLI-based D&D 5e character creator" -ForegroundColor White
Write-Host "  Supports: D&D 2014, D&D 2024, Tales of the Valiant" -ForegroundColor Gray
Write-Host ""

# Check Windows version
Write-Step "Checking system..."
$osVersion = [Environment]::OSVersion.Version
if ($osVersion.Major -lt 10) {
    Write-Warn "Windows 10 or later recommended for best experience"
}
Write-Success "Windows $($osVersion.Major).$($osVersion.Minor) detected"

# Check if running as admin (not required, just informational)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Info "Running as Administrator"
}

# Check for Python
Write-Step "Checking for Python..."
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
$python3Cmd = Get-Command python3 -ErrorAction SilentlyContinue

if ($pythonCmd -or $python3Cmd) {
    $pyCmd = if ($python3Cmd) { "python3" } else { "python" }
    $pyVersion = & $pyCmd --version 2>&1
    Write-Success "Found $pyVersion"
} else {
    Write-Warn "Python not found - uv will handle this"
}

# Install uv if not present
Write-Step "Setting up uv (fast Python package manager)..."
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue

if ($uvCmd) {
    $uvVersion = & uv --version 2>&1
    Write-Success "uv already installed ($uvVersion)"
} else {
    Write-Info "Installing uv..."
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        # Also add cargo bin to current session
        $cargobin = "$env:USERPROFILE\.cargo\bin"
        if (Test-Path $cargobin) {
            $env:Path = "$cargobin;$env:Path"
        }

        # Also check local app data for uv
        $uvLocalPath = "$env:LOCALAPPDATA\uv"
        if (Test-Path $uvLocalPath) {
            $env:Path = "$uvLocalPath;$env:Path"
        }

        Write-Success "uv installed successfully"
    } catch {
        Write-Host "`n   [ERROR] Failed to install uv: $_" -ForegroundColor Red
        Write-Host "`n   Try installing manually: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
        exit 1
    }
}

# Verify uv is available
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvCmd) {
    Write-Host "`n   [ERROR] uv not found in PATH after installation" -ForegroundColor Red
    Write-Host "`n   Please restart your terminal and run this installer again." -ForegroundColor Yellow
    Write-Host "   Or install uv manually: https://docs.astral.sh/uv/" -ForegroundColor Gray
    exit 1
}

# Install ccvault
Write-Step "Installing CCVault..."
try {
    # Uninstall first if exists (clean install)
    & uv tool uninstall ccvault 2>$null

    # Install from GitHub
    & uv tool install "git+https://github.com/jaredgiosinuff/dnd-manager"

    if ($LASTEXITCODE -ne 0) {
        throw "uv tool install failed"
    }

    Write-Success "CCVault installed successfully"
} catch {
    Write-Host "`n   [ERROR] Failed to install CCVault: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Step "Verifying installation..."
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Add uv tools to path for current session
$uvToolsPath = "$env:USERPROFILE\.local\bin"
if (Test-Path $uvToolsPath) {
    $env:Path = "$uvToolsPath;$env:Path"
}

$ccvaultCmd = Get-Command ccvault -ErrorAction SilentlyContinue
if ($ccvaultCmd) {
    Write-Success "ccvault command is available"
} else {
    Write-Warn "ccvault not found in PATH yet"
    Write-Info "You may need to restart your terminal"
}

# Success message
Write-Host @"

  ╔════════════════════════════════════════════════════════════╗
  ║                                                            ║
  ║   Installation complete!                                   ║
  ║                                                            ║
  ║   To start CCVault, open a new terminal and run:           ║
  ║                                                            ║
  ║      ccvault                                                ║
  ║                                                            ║
  ║   Quick commands:                                          ║
  ║      ccvault new "Gandalf" --class Wizard                  ║
  ║      ccvault list                                          ║
  ║      ccvault roll 2d6+5                                    ║
  ║      ccvault ask "How does sneak attack work?"             ║
  ║                                                            ║
  ╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "  Welcome to the CLI Master Race!" -ForegroundColor Cyan
Write-Host "  May your rolls be ever in your favor." -ForegroundColor Gray
Write-Host ""

# Offer to launch now
$launch = Read-Host "  Launch CCVault now? (Y/n)"
if ($launch -eq "" -or $launch.ToLower() -eq "y") {
    Write-Host ""
    if ($ccvaultCmd) {
        & ccvault
    } else {
        # Try direct path
        $directPath = "$env:USERPROFILE\.local\bin\ccvault.exe"
        if (Test-Path $directPath) {
            & $directPath
        } else {
            Write-Host "  Please restart your terminal first, then run: ccvault" -ForegroundColor Yellow
        }
    }
}

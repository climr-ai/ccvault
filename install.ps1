# CCVault Windows Installer
# Run: irm https://raw.githubusercontent.com/jaredgiosinuff/dnd-manager/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "Installing CCVault - D&D Character Manager" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Check if uv is installed
$uvPath = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvPath) {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Host "Installing ccvault..." -ForegroundColor Yellow
uv tool install git+https://github.com/jaredgiosinuff/dnd-manager

Write-Host ""
Write-Host "Done! Run 'ccvault' to start." -ForegroundColor Green
Write-Host ""
Write-Host "Note: If 'ccvault' is not found, restart your terminal or run:" -ForegroundColor Gray
Write-Host '  $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User")' -ForegroundColor Gray

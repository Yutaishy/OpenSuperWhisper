# Scaffold script for repository structure standardization
# Creates and validates standard directory structure

Write-Host "Starting repository structure scaffold..." -ForegroundColor Cyan

# Define standard directories
$dirs = @(
    "src",
    "pkg",
    "scripts",
    "tools",
    "configs",
    "docs",
    "tests",
    "build",
    "dist",
    "dist/linux/amd64",
    "dist/linux/arm64",
    "dist/darwin/amd64",
    "dist/darwin/arm64",
    "dist/windows/amd64",
    "dist/windows/arm64",
    ".github/workflows",
    ".github/ISSUE_TEMPLATE"
)

# Create directories if they don't exist
foreach ($dir in $dirs) {
    $path = Join-Path $PSScriptRoot ".." $dir
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "→ Exists: $dir" -ForegroundColor Yellow
    }
}

# Move existing code to appropriate locations
$oldPath = Join-Path $PSScriptRoot ".." "OpenSuperWhisper"
$newPath = Join-Path $PSScriptRoot ".." "src" "OpenSuperWhisper"

if ((Test-Path $oldPath) -and !(Test-Path $newPath)) {
    Move-Item -Path $oldPath -Destination (Join-Path $PSScriptRoot ".." "src") -Force
    Write-Host "✓ Moved OpenSuperWhisper to src/" -ForegroundColor Green
}

# Clean up unnecessary directories
$cleanupDirs = @(
    "%APPDATA%",
    "archive/npm_cache",
    "archive/windows_appdata",
    "archive/temp_files",
    "archive/old_logs"
)

foreach ($dir in $cleanupDirs) {
    $path = Join-Path $PSScriptRoot ".." $dir
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Removed: $dir" -ForegroundColor Green
    }
}

# Validate naming conventions
Write-Host ""
Write-Host "Checking naming conventions..." -ForegroundColor Cyan

# Find files with problematic names
$problematic = Get-ChildItem -Recurse -File | Where-Object {
    $_.Name -match '[A-Z]' -or $_.Name -match '\s' -or $_.Name -match '[^a-zA-Z0-9._-]'
} | Where-Object { 
    $_.FullName -notmatch "\.git" -and $_.FullName -notmatch "node_modules"
} | Select-Object -First 20

if ($problematic) {
    Write-Host "⚠ Files with non-standard names found:" -ForegroundColor Yellow
    $problematic | Select-Object -First 10 | ForEach-Object { Write-Host $_.Name }
}

# Check for large files
Write-Host ""
Write-Host "Checking for large files..." -ForegroundColor Cyan

$largeFiles = Get-ChildItem -Recurse -File | Where-Object {
    $_.Length -gt 10MB
} | Where-Object {
    $_.FullName -notmatch "\.git" -and $_.FullName -notmatch "node_modules"
}

if ($largeFiles) {
    Write-Host "⚠ Large files found (>10MB):" -ForegroundColor Yellow
    $largeFiles | ForEach-Object { Write-Host "$($_.Name) - $([math]::Round($_.Length/1MB, 2))MB" }
}

# Report summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Scaffold completed!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review and update .gitignore"
Write-Host "2. Move remaining files to appropriate directories"
Write-Host "3. Update import paths in code"
Write-Host "4. Run tests to ensure everything works"
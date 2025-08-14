# Universal build script for OpenSuperWhisper (Windows PowerShell)
# Handles all OS/architecture combinations

param(
    [string]$OSTarget = "",
    [string]$ArchTarget = "",
    [string]$Version = ""
)

# Configuration
$AppName = "opensuperwhisper"
$BuildDate = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$BuildDir = "build"
$DistDir = "dist"
$SrcDir = "src"

# Get version from git or use default
if ([string]::IsNullOrEmpty($Version)) {
    try {
        $Version = git describe --tags --always 2>$null
        if ([string]::IsNullOrEmpty($Version)) {
            $Version = "dev"
        }
    } catch {
        $Version = "dev"
    }
}

# Print banner
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "OpenSuperWhisper Build System" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Cyan
Write-Host "Date: $BuildDate" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Detect OS and architecture if not specified
if ([string]::IsNullOrEmpty($OSTarget)) {
    if ($IsWindows -or $PSVersionTable.Platform -eq "Win32NT") {
        $OSTarget = "windows"
    } elseif ($IsMacOS) {
        $OSTarget = "darwin"
    } elseif ($IsLinux) {
        $OSTarget = "linux"
    } else {
        $OSTarget = "windows"  # Default to Windows on older PowerShell
    }
}

if ([string]::IsNullOrEmpty($ArchTarget)) {
    if ([Environment]::Is64BitOperatingSystem) {
        $ArchTarget = "amd64"
    } else {
        $ArchTarget = "x86"
    }
    
    # Check for ARM
    $processor = (Get-WmiObject Win32_Processor).Name
    if ($processor -match "ARM") {
        $ArchTarget = "arm64"
    }
}

# Normalize architecture names
switch ($ArchTarget) {
    "x86_64" { $ArchTarget = "amd64" }
    "aarch64" { $ArchTarget = "arm64" }
}

# Set binary extension based on OS
$BinaryExt = ""
if ($OSTarget -eq "windows") {
    $BinaryExt = ".exe"
}

Write-Host "Building for: $OSTarget/$ArchTarget" -ForegroundColor Blue
Write-Host ""

# Create build directories
$OutputDir = Join-Path $DistDir $OSTarget $ArchTarget "$AppName-$Version-$OSTarget-$ArchTarget"
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null

Write-Host "✓ Created output directory: $OutputDir" -ForegroundColor Green

# Check Python availability
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Python 3 is required but not installed" -ForegroundColor Red
    exit 1
}

# Create virtual environment if needed
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $python.Source -m venv venv
}

# Activate virtual environment
$venvActivate = ""
if (Test-Path "venv\Scripts\Activate.ps1") {
    $venvActivate = "venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\bin\Activate.ps1") {
    $venvActivate = "venv\bin\Activate.ps1"
}

if ($venvActivate) {
    & $venvActivate
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pyinstaller

# Build Python application with PyInstaller
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow

$PyInstallerOpts = @(
    "--name=${AppName}${BinaryExt}",
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    "--distpath=$OutputDir",
    "--workpath=$BuildDir",
    "--specpath=$BuildDir"
)

# Add OS-specific options
switch ($OSTarget) {
    "darwin" {
        $PyInstallerOpts += "--osx-bundle-identifier=com.opensuperwhisper.app"
        $PyInstallerOpts += "--icon=assets/ios/AppIcon.appiconset/Icon-AppStore-1024.png"
        if (Test-Path "entitlements.plist") {
            $PyInstallerOpts += "--osx-entitlements-file=entitlements.plist"
        }
    }
    "windows" {
        $PyInstallerOpts += "--icon=assets/windows/osw.ico"
        if (Test-Path "version_info.txt") {
            $PyInstallerOpts += "--version-file=version_info.txt"
        }
    }
    "linux" {
        $PyInstallerOpts += "--icon=assets/web/icon-512.png"
    }
}

# Add hidden imports
$HiddenImports = @(
    "pynput",
    "pyperclip",
    "PySide6",
    "sounddevice",
    "numpy",
    "requests",
    "faster_whisper"
)

foreach ($import in $HiddenImports) {
    $PyInstallerOpts += "--hidden-import=$import"
}

# Run PyInstaller
python -m PyInstaller $PyInstallerOpts run_app.py

# Copy additional files
Write-Host ""
Write-Host "Copying additional files..." -ForegroundColor Yellow

# Copy configuration templates
if (Test-Path "configs") {
    New-Item -ItemType Directory -Path "$OutputDir\configs" -Force | Out-Null
    Get-ChildItem -Path "configs" -Include "*.example", "*.template" -Recurse | ForEach-Object {
        Copy-Item $_.FullName -Destination "$OutputDir\configs\"
    }
}

# Copy style guides
if (Test-Path "style_guides") {
    Copy-Item -Path "style_guides" -Destination $OutputDir -Recurse -Force
}

# Copy documentation
$docs = @("README.md", "LICENSE", "CHANGELOG.md")
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Copy-Item $doc -Destination $OutputDir
    }
}

# Create version file
$versionContent = @"
OpenSuperWhisper
Version: $Version
Build Date: $BuildDate
Platform: $OSTarget/$ArchTarget
"@
Set-Content -Path "$OutputDir\version.txt" -Value $versionContent

# Package the build
Write-Host ""
Write-Host "Creating archive..." -ForegroundColor Yellow

$ArchiveName = "$AppName-$Version-$OSTarget-$ArchTarget"
$ArchiveDir = Join-Path $DistDir $OSTarget $ArchTarget

Push-Location $ArchiveDir

try {
    if ($OSTarget -eq "windows") {
        # Create ZIP for Windows
        $ZipFile = "$ArchiveName.zip"
        if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
            Compress-Archive -Path "$AppName-$Version-$OSTarget-$ArchTarget" -DestinationPath $ZipFile -Force
            Write-Host "✓ Created: $ZipFile" -ForegroundColor Green
        }
    } else {
        # Create tar.gz for Unix-like systems
        $TarFile = "$ArchiveName.tar.gz"
        if (Get-Command tar -ErrorAction SilentlyContinue) {
            tar czf $TarFile "$AppName-$Version-$OSTarget-$ArchTarget"
            Write-Host "✓ Created: $TarFile" -ForegroundColor Green
        }
    }

    # Generate checksums
    Write-Host ""
    Write-Host "Generating checksums..." -ForegroundColor Yellow

    $files = Get-ChildItem -Filter "*.zip", "*.tar.gz" -ErrorAction SilentlyContinue
    $sha256Content = ""
    
    foreach ($file in $files) {
        $hash = Get-FileHash -Path $file.FullName -Algorithm SHA256
        $sha256Content += "$($hash.Hash.ToLower())  $($file.Name)`n"
        
        # Individual checksum file
        Set-Content -Path "$($file.Name).sha256" -Value "$($hash.Hash.ToLower())  $($file.Name)"
        Write-Host "✓ Created: $($file.Name).sha256" -ForegroundColor Green
    }
    
    # Combined SHA256SUMS file
    if ($sha256Content) {
        Set-Content -Path "SHA256SUMS" -Value $sha256Content.TrimEnd()
    }
}
finally {
    Pop-Location
}

# Clean up build directory
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow
Remove-Item -Path $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✓ Cleaned build directory" -ForegroundColor Green

# Final report
Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output location:"
Write-Host "  $OutputDir"
Write-Host ""
Write-Host "Archive location:"
Write-Host "  $ArchiveDir\$ArchiveName.*"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test the executable in $OutputDir"
Write-Host "2. Verify the archive contents"
Write-Host "3. Run dependency checks with scripts\check-deps.ps1"
Write-Host "4. Upload to release page when ready"
# Quality gate check script for OpenSuperWhisper (PowerShell)
# Runs lint, format checks, and tests

$ErrorActionPreference = "Continue"
$ExitCode = 0

# Print banner
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "OpenSuperWhisper Quality Gate" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Function to print section header
function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 40) -ForegroundColor Blue
    Write-Host "▶ $Title" -ForegroundColor Blue
    Write-Host ("=" * 40) -ForegroundColor Blue
}

# Function to check tool availability
function Test-Tool {
    param(
        [string]$Command,
        [string]$Package
    )
    
    $tool = Get-Command $Command -ErrorAction SilentlyContinue
    if (-not $tool) {
        Write-Host "⚠ $Command not found, installing..." -ForegroundColor Yellow
        pip install -q $Package
    }
}

# Get Python command
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Python 3 is required but not installed" -ForegroundColor Red
    exit 1
}

# Activate virtual environment if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\bin\Activate.ps1") {
    & "venv\bin\Activate.ps1"
}

# ==========================================
# 1. Code Formatting Check
# ==========================================
Write-Section "Code Formatting (Black)"

Test-Tool "black" "black"

$blackResult = & black --check --diff src/ tests/ *.py 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Code formatting check passed" -ForegroundColor Green
} else {
    Write-Host "✗ Code formatting issues found" -ForegroundColor Red
    Write-Host "  Run 'black src/ tests/ *.py' to fix" -ForegroundColor Yellow
    $ExitCode = 1
}

# ==========================================
# 2. Import Sorting Check
# ==========================================
Write-Section "Import Sorting (isort)"

Test-Tool "isort" "isort"

$isortResult = & isort --check-only --diff src/ tests/ *.py 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Import sorting check passed" -ForegroundColor Green
} else {
    Write-Host "✗ Import sorting issues found" -ForegroundColor Red
    Write-Host "  Run 'isort src/ tests/ *.py' to fix" -ForegroundColor Yellow
    $ExitCode = 1
}

# ==========================================
# 3. Linting (Flake8)
# ==========================================
Write-Section "Linting (Flake8)"

Test-Tool "flake8" "flake8"

# Create flake8 config if not exists
if (-not (Test-Path ".flake8")) {
    @"
[flake8]
max-line-length = 120
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,venv,env,.venv
max-complexity = 10
"@ | Set-Content -Path ".flake8"
}

$flake8Result = & flake8 src/ tests/ *.py 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Linting check passed" -ForegroundColor Green
} else {
    Write-Host "✗ Linting issues found" -ForegroundColor Red
    $ExitCode = 1
}

# ==========================================
# 4. Type Checking (mypy)
# ==========================================
Write-Section "Type Checking (mypy)"

Test-Tool "mypy" "mypy"

$mypyResult = & mypy --ignore-missing-imports --no-strict-optional src/ 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Type checking passed" -ForegroundColor Green
} else {
    Write-Host "⚠ Type checking warnings found" -ForegroundColor Yellow
    # Don't fail on type warnings
}

# ==========================================
# 5. Security Scan (bandit)
# ==========================================
Write-Section "Security Scan (Bandit)"

Test-Tool "bandit" "bandit"

$banditResult = & bandit -r src/ -ll 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Security scan passed" -ForegroundColor Green
} else {
    Write-Host "⚠ Security warnings found" -ForegroundColor Yellow
    # Don't fail on low-severity issues
}

# ==========================================
# 6. Unit Tests
# ==========================================
Write-Section "Unit Tests (pytest)"

Test-Tool "pytest" "pytest pytest-cov"

# Run tests with coverage
if ((Test-Path "tests") -and (Get-ChildItem "tests\*.py" -ErrorAction SilentlyContinue)) {
    $pytestResult = & pytest tests/ `
        --cov=src `
        --cov-report=term-missing `
        --cov-report=html `
        --cov-fail-under=60 `
        -v
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ All tests passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Some tests failed" -ForegroundColor Red
        $ExitCode = 1
    }
} else {
    Write-Host "⚠ No tests found" -ForegroundColor Yellow
}

# ==========================================
# 7. Documentation Check
# ==========================================
Write-Section "Documentation Check"

# Check for required documentation files
$RequiredDocs = @("README.md", "LICENSE", "CHANGELOG.md")
$MissingDocs = @()

foreach ($doc in $RequiredDocs) {
    if (-not (Test-Path $doc)) {
        $MissingDocs += $doc
    }
}

if ($MissingDocs.Count -eq 0) {
    Write-Host "✓ All required documentation present" -ForegroundColor Green
} else {
    Write-Host "✗ Missing documentation files:" -ForegroundColor Red
    foreach ($doc in $MissingDocs) {
        Write-Host "    - $doc"
    }
    $ExitCode = 1
}

# ==========================================
# 8. Dependency Check
# ==========================================
Write-Section "Dependency Security Check"

Test-Tool "safety" "safety"

# Check for known vulnerabilities
$safetyResult = & safety check --json 2>$null
if ($safetyResult -match '"vulnerabilities": \[\]') {
    Write-Host "✓ No known vulnerabilities in dependencies" -ForegroundColor Green
} else {
    Write-Host "⚠ Vulnerabilities found in dependencies" -ForegroundColor Yellow
    & safety check 2>$null
    # Don't fail build for dependency issues
}

# ==========================================
# 9. License Check
# ==========================================
Write-Section "License Compatibility Check"

Test-Tool "pip-licenses" "pip-licenses"

# List all licenses
Write-Host "Dependency licenses:"
& pip-licenses --format=markdown --with-authors | Select-Object -First 20

# ==========================================
# Summary
# ==========================================
Write-Host ""
Write-Host ("=" * 40) -ForegroundColor Blue
Write-Host "Summary" -ForegroundColor Blue
Write-Host ("=" * 40) -ForegroundColor Blue

if ($ExitCode -eq 0) {
    Write-Host "✓ All quality checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Code coverage report: htmlcov\index.html"
} else {
    Write-Host "✗ Some quality checks failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the issues above before committing."
    Write-Host ""
    Write-Host "Quick fix commands:"
    Write-Host "  black src/ tests/ *.py        # Fix formatting"
    Write-Host "  isort src/ tests/ *.py        # Fix imports"
    Write-Host "  flake8 src/ tests/ *.py       # Show lint issues"
}

exit $ExitCode
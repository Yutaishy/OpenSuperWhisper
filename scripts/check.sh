#!/bin/bash
#
# Quality gate check script for OpenSuperWhisper
# Runs lint, format checks, and tests

set -e

# Configuration
PYTHON=${PYTHON:-python3}
EXIT_CODE=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print banner
echo "========================================="
echo "OpenSuperWhisper Quality Gate"
echo "========================================="
echo ""

# Function to print section header
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check tool availability
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${YELLOW}⚠ $1 not found, installing...${NC}"
        pip install -q $2
    fi
}

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

# ==========================================
# 1. Code Formatting Check
# ==========================================
print_section "Code Formatting (Black)"

check_tool "black" "black"

if black --check --diff src/ tests/ *.py 2>/dev/null; then
    echo -e "${GREEN}✓ Code formatting check passed${NC}"
else
    echo -e "${RED}✗ Code formatting issues found${NC}"
    echo -e "${YELLOW}  Run 'black src/ tests/ *.py' to fix${NC}"
    EXIT_CODE=1
fi

# ==========================================
# 2. Import Sorting Check
# ==========================================
print_section "Import Sorting (isort)"

check_tool "isort" "isort"

if isort --check-only --diff src/ tests/ *.py 2>/dev/null; then
    echo -e "${GREEN}✓ Import sorting check passed${NC}"
else
    echo -e "${RED}✗ Import sorting issues found${NC}"
    echo -e "${YELLOW}  Run 'isort src/ tests/ *.py' to fix${NC}"
    EXIT_CODE=1
fi

# ==========================================
# 3. Linting (Flake8)
# ==========================================
print_section "Linting (Flake8)"

check_tool "flake8" "flake8"

# Create flake8 config if not exists
if [ ! -f ".flake8" ]; then
    cat > .flake8 << EOF
[flake8]
max-line-length = 120
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,venv,env,.venv
max-complexity = 10
EOF
fi

if flake8 src/ tests/ *.py 2>/dev/null; then
    echo -e "${GREEN}✓ Linting check passed${NC}"
else
    echo -e "${RED}✗ Linting issues found${NC}"
    EXIT_CODE=1
fi

# ==========================================
# 4. Type Checking (mypy)
# ==========================================
print_section "Type Checking (mypy)"

check_tool "mypy" "mypy"

if mypy --ignore-missing-imports --no-strict-optional src/ 2>/dev/null; then
    echo -e "${GREEN}✓ Type checking passed${NC}"
else
    echo -e "${YELLOW}⚠ Type checking warnings found${NC}"
    # Don't fail on type warnings
fi

# ==========================================
# 5. Security Scan (bandit)
# ==========================================
print_section "Security Scan (Bandit)"

check_tool "bandit" "bandit"

if bandit -r src/ -ll 2>/dev/null; then
    echo -e "${GREEN}✓ Security scan passed${NC}"
else
    echo -e "${YELLOW}⚠ Security warnings found${NC}"
    # Don't fail on low-severity issues
fi

# ==========================================
# 6. Unit Tests
# ==========================================
print_section "Unit Tests (pytest)"

check_tool "pytest" "pytest pytest-cov"

# Run tests with coverage
if [ -d "tests" ] && [ "$(ls -A tests/*.py 2>/dev/null)" ]; then
    if pytest tests/ \
        --cov=src \
        --cov-report=term-missing \
        --cov-report=html \
        --cov-fail-under=60 \
        -v; then
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        EXIT_CODE=1
    fi
else
    echo -e "${YELLOW}⚠ No tests found${NC}"
fi

# ==========================================
# 7. Documentation Check
# ==========================================
print_section "Documentation Check"

# Check for required documentation files
REQUIRED_DOCS=("README.md" "LICENSE" "CHANGELOG.md")
MISSING_DOCS=()

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ ! -f "$doc" ]; then
        MISSING_DOCS+=("$doc")
    fi
done

if [ ${#MISSING_DOCS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required documentation present${NC}"
else
    echo -e "${RED}✗ Missing documentation files:${NC}"
    for doc in "${MISSING_DOCS[@]}"; do
        echo "    - $doc"
    done
    EXIT_CODE=1
fi

# ==========================================
# 8. Dependency Check
# ==========================================
print_section "Dependency Security Check"

check_tool "safety" "safety"

# Check for known vulnerabilities
if safety check --json 2>/dev/null | grep -q '"vulnerabilities": \[\]'; then
    echo -e "${GREEN}✓ No known vulnerabilities in dependencies${NC}"
else
    echo -e "${YELLOW}⚠ Vulnerabilities found in dependencies${NC}"
    safety check 2>/dev/null || true
    # Don't fail build for dependency issues
fi

# ==========================================
# 9. License Check
# ==========================================
print_section "License Compatibility Check"

check_tool "pip-licenses" "pip-licenses"

# List all licenses
echo "Dependency licenses:"
pip-licenses --format=markdown --with-authors | head -20

# ==========================================
# Summary
# ==========================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All quality checks passed!${NC}"
    echo ""
    echo "Code coverage report: htmlcov/index.html"
else
    echo -e "${RED}✗ Some quality checks failed${NC}"
    echo ""
    echo "Please fix the issues above before committing."
    echo ""
    echo "Quick fix commands:"
    echo "  black src/ tests/ *.py        # Fix formatting"
    echo "  isort src/ tests/ *.py        # Fix imports"
    echo "  flake8 src/ tests/ *.py       # Show lint issues"
fi

exit $EXIT_CODE
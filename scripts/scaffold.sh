#!/bin/bash
#
# Scaffold script for repository structure standardization
# Creates and validates standard directory structure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Starting repository structure scaffold..."

# Define standard directories
DIRS=(
    "src"
    "pkg"
    "scripts"
    "tools"
    "configs"
    "docs"
    "tests"
    "build"
    "dist"
    "dist/linux/amd64"
    "dist/linux/arm64"
    "dist/darwin/amd64"
    "dist/darwin/arm64"
    "dist/windows/amd64"
    "dist/windows/arm64"
    ".github/workflows"
    ".github/ISSUE_TEMPLATE"
)

# Create directories if they don't exist
for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "${GREEN}✓${NC} Created: $dir"
    else
        echo -e "${YELLOW}→${NC} Exists: $dir"
    fi
done

# Move existing code to appropriate locations
if [ -d "OpenSuperWhisper" ] && [ ! -d "src/OpenSuperWhisper" ]; then
    mv OpenSuperWhisper src/
    echo -e "${GREEN}✓${NC} Moved OpenSuperWhisper to src/"
fi

# Clean up unnecessary directories
CLEANUP_DIRS=(
    "%APPDATA%"
    "archive/npm_cache"
    "archive/windows_appdata"
    "archive/temp_files"
    "archive/old_logs"
)

for dir in "${CLEANUP_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo -e "${GREEN}✓${NC} Removed: $dir"
    fi
done

# Validate naming conventions
echo ""
echo "Checking naming conventions..."

# Find files with problematic names
PROBLEMATIC=$(find . -type f -name "*[A-Z]*" -o -name "*[ ]*" -o -name "*[^a-zA-Z0-9._/-]*" 2>/dev/null | grep -v ".git" | grep -v "node_modules" | head -20 || true)

if [ ! -z "$PROBLEMATIC" ]; then
    echo -e "${YELLOW}⚠${NC} Files with non-standard names found:"
    echo "$PROBLEMATIC" | head -10
fi

# Check for large files
echo ""
echo "Checking for large files..."
LARGE_FILES=$(find . -type f -size +10M 2>/dev/null | grep -v ".git" | grep -v "node_modules" || true)

if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠${NC} Large files found (>10MB):"
    echo "$LARGE_FILES"
fi

# Report summary
echo ""
echo "========================================="
echo -e "${GREEN}Scaffold completed!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review and update .gitignore"
echo "2. Move remaining files to appropriate directories"
echo "3. Update import paths in code"
echo "4. Run tests to ensure everything works"
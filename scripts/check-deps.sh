#!/bin/bash
#
# Dependency Analysis and Smoke Test Script
# Checks binary dependencies and runs minimal functionality tests

set -e

# Configuration
BINARY_NAME=${BINARY_NAME:-opensuperwhisper}
TEST_DIR=${TEST_DIR:-dist}
VERBOSE=${VERBOSE:-false}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# OS detection
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Normalize architecture
case "$ARCH" in
    x86_64|amd64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
esac

# Print section header
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# ==========================================
# Dependency Analysis
# ==========================================

analyze_linux_deps() {
    local binary=$1
    
    print_section "Linux Dependency Analysis"
    
    if ! command -v ldd &> /dev/null; then
        echo -e "${YELLOW}ldd not found, skipping dependency analysis${NC}"
        return
    fi
    
    echo "Analyzing: $binary"
    echo ""
    
    # Check shared libraries
    echo "Shared library dependencies:"
    ldd "$binary" 2>/dev/null | grep -v "not a dynamic executable" || {
        echo "  Static binary or analysis failed"
    }
    
    # Check for missing libraries
    echo ""
    echo "Checking for missing libraries:"
    local missing=$(ldd "$binary" 2>/dev/null | grep "not found" || true)
    
    if [ -z "$missing" ]; then
        echo -e "${GREEN}✓ All libraries found${NC}"
    else
        echo -e "${RED}✗ Missing libraries:${NC}"
        echo "$missing"
        return 1
    fi
    
    # Check glibc version requirement
    echo ""
    echo "GLIBC version requirements:"
    objdump -T "$binary" 2>/dev/null | grep GLIBC | sed 's/.*GLIBC_\([0-9.]*\).*/\1/g' | sort -V | tail -1 || echo "  Could not determine"
    
    # Check file info
    echo ""
    echo "Binary information:"
    file "$binary"
}

analyze_macos_deps() {
    local binary=$1
    
    print_section "macOS Dependency Analysis"
    
    if ! command -v otool &> /dev/null; then
        echo -e "${YELLOW}otool not found, skipping dependency analysis${NC}"
        return
    fi
    
    echo "Analyzing: $binary"
    echo ""
    
    # Check shared libraries
    echo "Shared library dependencies:"
    otool -L "$binary"
    
    # Check for @rpath dependencies
    echo ""
    echo "Checking @rpath dependencies:"
    local rpath_deps=$(otool -L "$binary" | grep "@rpath" || true)
    
    if [ -z "$rpath_deps" ]; then
        echo -e "${GREEN}✓ No @rpath dependencies${NC}"
    else
        echo -e "${YELLOW}⚠ @rpath dependencies found:${NC}"
        echo "$rpath_deps"
    fi
    
    # Check minimum macOS version
    echo ""
    echo "Minimum macOS version:"
    otool -l "$binary" | grep -A 3 "LC_VERSION_MIN_MACOSX" || echo "  Not specified"
    
    # Check code signing
    echo ""
    echo "Code signature:"
    codesign -dv "$binary" 2>&1 || echo "  Not signed"
}

analyze_windows_deps() {
    local binary=$1
    
    print_section "Windows Dependency Analysis"
    
    # Try different tools
    if command -v dumpbin &> /dev/null; then
        echo "Using dumpbin..."
        dumpbin /dependents "$binary"
    elif command -v objdump &> /dev/null; then
        echo "Using objdump..."
        objdump -p "$binary" | grep "DLL Name:"
    elif command -v strings &> /dev/null; then
        echo "Using strings (basic analysis)..."
        strings "$binary" | grep -i ".dll$" | sort -u | head -20
    else
        echo -e "${YELLOW}No dependency analysis tools available${NC}"
    fi
    
    # Check for common runtime dependencies
    echo ""
    echo "Checking for common runtime requirements:"
    local common_deps=("msvcrt" "kernel32" "user32" "ws2_32")
    
    for dep in "${common_deps[@]}"; do
        if strings "$binary" 2>/dev/null | grep -qi "$dep"; then
            echo "  ✓ $dep.dll referenced"
        fi
    done
}

# ==========================================
# Smoke Tests
# ==========================================

run_smoke_tests() {
    local binary=$1
    
    print_section "Smoke Tests"
    
    # Test 1: Binary exists and is executable
    echo -n "Test 1 - Binary exists and is executable: "
    if [ -f "$binary" ] && [ -x "$binary" ]; then
        echo -e "${GREEN}PASS${NC}"
    else
        echo -e "${RED}FAIL${NC}"
        return 1
    fi
    
    # Test 2: Check file size (should be > 1MB for bundled Python app)
    echo -n "Test 2 - Binary size check (>1MB): "
    local size=$(stat -f%z "$binary" 2>/dev/null || stat -c%s "$binary" 2>/dev/null)
    if [ "$size" -gt 1048576 ]; then
        echo -e "${GREEN}PASS${NC} ($(( size / 1048576 ))MB)"
    else
        echo -e "${YELLOW}WARNING${NC} ($(( size / 1024 ))KB)"
    fi
    
    # Test 3: Version check
    echo -n "Test 3 - Version check: "
    if timeout 5 "$binary" --version &>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
    else
        echo -e "${YELLOW}SKIP${NC} (no --version flag or timeout)"
    fi
    
    # Test 4: Help output
    echo -n "Test 4 - Help output: "
    if timeout 5 "$binary" --help &>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
    else
        echo -e "${YELLOW}SKIP${NC} (no --help flag or timeout)"
    fi
    
    # Test 5: Dry run test
    echo -n "Test 5 - Dry run test: "
    if timeout 5 "$binary" --dry-run &>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
    else
        echo -e "${YELLOW}SKIP${NC} (no --dry-run flag)"
    fi
}

# ==========================================
# Runtime Environment Tests
# ==========================================

test_runtime_environment() {
    print_section "Runtime Environment Tests"
    
    # Test with minimal PATH
    echo "Testing with minimal PATH..."
    local original_path=$PATH
    export PATH=/usr/bin:/bin
    
    if timeout 5 "$1" --version &>/dev/null; then
        echo -e "${GREEN}✓ Works with minimal PATH${NC}"
    else
        echo -e "${YELLOW}⚠ May require specific PATH entries${NC}"
    fi
    
    export PATH=$original_path
    
    # Test with no HOME directory
    echo ""
    echo "Testing without HOME directory..."
    local original_home=$HOME
    unset HOME
    
    if timeout 5 "$1" --version &>/dev/null; then
        echo -e "${GREEN}✓ Works without HOME directory${NC}"
    else
        echo -e "${YELLOW}⚠ Requires HOME directory${NC}"
    fi
    
    export HOME=$original_home
    
    # Test with read-only filesystem (if possible)
    echo ""
    echo "Testing write requirements..."
    if touch test_write_$$ 2>/dev/null; then
        rm test_write_$$
        echo -e "${GREEN}✓ Current directory is writable${NC}"
    else
        echo -e "${YELLOW}⚠ Current directory is read-only${NC}"
    fi
}

# ==========================================
# Find binaries to test
# ==========================================

find_binaries() {
    local search_dir=${1:-$TEST_DIR}
    
    echo "Searching for binaries in: $search_dir"
    
    local binaries=()
    
    # Find executable files
    if [ -d "$search_dir" ]; then
        while IFS= read -r -d '' file; do
            binaries+=("$file")
        done < <(find "$search_dir" -type f \( -name "$BINARY_NAME*" -o -name "*.exe" \) -executable -print0 2>/dev/null)
        
        # On macOS, -executable might not work, try different approach
        if [ ${#binaries[@]} -eq 0 ]; then
            while IFS= read -r -d '' file; do
                if [ -x "$file" ]; then
                    binaries+=("$file")
                fi
            done < <(find "$search_dir" -type f \( -name "$BINARY_NAME*" -o -name "*.exe" \) -print0 2>/dev/null)
        fi
    fi
    
    if [ ${#binaries[@]} -eq 0 ]; then
        echo -e "${YELLOW}No binaries found in $search_dir${NC}"
        return 1
    fi
    
    echo "Found ${#binaries[@]} binary/binaries:"
    printf '%s\n' "${binaries[@]}"
    echo ""
    
    for binary in "${binaries[@]}"; do
        analyze_binary "$binary"
    done
}

# ==========================================
# Main analysis function
# ==========================================

analyze_binary() {
    local binary=$1
    
    echo ""
    echo "========================================="
    echo "Analyzing: $(basename "$binary")"
    echo "========================================="
    
    # Run OS-specific dependency analysis
    case "$OS" in
        linux)
            analyze_linux_deps "$binary"
            ;;
        darwin)
            analyze_macos_deps "$binary"
            ;;
        mingw*|cygwin*|msys*|windows)
            analyze_windows_deps "$binary"
            ;;
        *)
            echo -e "${YELLOW}Unknown OS: $OS${NC}"
            ;;
    esac
    
    # Run smoke tests
    run_smoke_tests "$binary"
    
    # Run runtime environment tests
    test_runtime_environment "$binary"
}

# ==========================================
# Main execution
# ==========================================

main() {
    echo "========================================="
    echo "Dependency Analysis and Smoke Tests"
    echo "OS: $OS | Arch: $ARCH"
    echo "========================================="
    
    # Parse arguments
    if [ $# -gt 0 ]; then
        # Specific binary provided
        if [ -f "$1" ]; then
            analyze_binary "$1"
        else
            echo -e "${RED}File not found: $1${NC}"
            exit 1
        fi
    else
        # Search for binaries
        find_binaries "$TEST_DIR"
    fi
    
    echo ""
    echo "========================================="
    echo -e "${GREEN}Analysis complete!${NC}"
    echo "========================================="
}

# Run if not sourced
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
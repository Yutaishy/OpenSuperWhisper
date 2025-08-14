#!/bin/bash
#
# Universal build script for OpenSuperWhisper
# Handles all OS/architecture combinations

set -e

# Configuration
APP_NAME="opensuperwhisper"
VERSION=${VERSION:-$(git describe --tags --always 2>/dev/null || echo "dev")}
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BUILD_DIR="build"
DIST_DIR="dist"
SRC_DIR="src"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print banner
echo "========================================="
echo "OpenSuperWhisper Build System"
echo "Version: $VERSION"
echo "Date: $BUILD_DATE"
echo "========================================="
echo ""

# Parse arguments
OS_TARGET=${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}
ARCH_TARGET=${2:-$(uname -m)}

# Normalize architecture names
case "$ARCH_TARGET" in
    x86_64|amd64)
        ARCH_TARGET="amd64"
        ;;
    aarch64|arm64)
        ARCH_TARGET="arm64"
        ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH_TARGET${NC}"
        exit 1
        ;;
esac

# Normalize OS names
case "$OS_TARGET" in
    darwin|macos)
        OS_TARGET="darwin"
        BINARY_EXT=""
        ;;
    linux)
        OS_TARGET="linux"
        BINARY_EXT=""
        ;;
    windows|win32|mingw*)
        OS_TARGET="windows"
        BINARY_EXT=".exe"
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS_TARGET${NC}"
        exit 1
        ;;
esac

echo -e "${BLUE}Building for: ${OS_TARGET}/${ARCH_TARGET}${NC}"
echo ""

# Create build directories
OUTPUT_DIR="${DIST_DIR}/${OS_TARGET}/${ARCH_TARGET}/${APP_NAME}-${VERSION}-${OS_TARGET}-${ARCH_TARGET}"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$BUILD_DIR"

echo -e "${GREEN}✓${NC} Created output directory: $OUTPUT_DIR"

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi

echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q pyinstaller

# Build Python application with PyInstaller
echo ""
echo -e "${YELLOW}Building executable...${NC}"

PYINSTALLER_OPTS=(
    "--name=${APP_NAME}${BINARY_EXT}"
    "--onefile"
    "--windowed"
    "--clean"
    "--noconfirm"
    "--distpath=${OUTPUT_DIR}"
    "--workpath=${BUILD_DIR}"
    "--specpath=${BUILD_DIR}"
)

# Add OS-specific options
case "$OS_TARGET" in
    darwin)
        PYINSTALLER_OPTS+=(
            "--osx-bundle-identifier=com.opensuperwhisper.app"
            "--icon=assets/ios/AppIcon.appiconset/Icon-AppStore-1024.png"
        )
        if [ -f "entitlements.plist" ]; then
            PYINSTALLER_OPTS+=("--osx-entitlements-file=entitlements.plist")
        fi
        ;;
    windows)
        PYINSTALLER_OPTS+=(
            "--icon=assets/windows/osw.ico"
        )
        if [ -f "version_info.txt" ]; then
            PYINSTALLER_OPTS+=("--version-file=version_info.txt")
        fi
        ;;
    linux)
        PYINSTALLER_OPTS+=(
            "--icon=assets/web/icon-512.png"
        )
        ;;
esac

# Add hidden imports for all required modules
PYINSTALLER_OPTS+=(
    "--hidden-import=pynput"
    "--hidden-import=pyperclip"
    "--hidden-import=PySide6"
    "--hidden-import=sounddevice"
    "--hidden-import=numpy"
    "--hidden-import=requests"
    "--hidden-import=faster_whisper"
)

# Run PyInstaller
python -m PyInstaller "${PYINSTALLER_OPTS[@]}" src/run_app.py

# Copy additional files
echo ""
echo -e "${YELLOW}Copying additional files...${NC}"

# Copy configuration templates
if [ -d "configs" ]; then
    mkdir -p "${OUTPUT_DIR}/configs"
    find configs -name "*.example" -o -name "*.template" | while read -r file; do
        cp "$file" "${OUTPUT_DIR}/configs/"
    done
fi

# Copy style guides
if [ -d "style_guides" ]; then
    cp -r style_guides "${OUTPUT_DIR}/"
fi

# Copy documentation
cp README.md "${OUTPUT_DIR}/" 2>/dev/null || true
cp LICENSE "${OUTPUT_DIR}/" 2>/dev/null || true
cp CHANGELOG.md "${OUTPUT_DIR}/" 2>/dev/null || true

# Create version file
cat > "${OUTPUT_DIR}/version.txt" << EOF
OpenSuperWhisper
Version: ${VERSION}
Build Date: ${BUILD_DATE}
Platform: ${OS_TARGET}/${ARCH_TARGET}
EOF

# Package the build
echo ""
echo -e "${YELLOW}Creating archive...${NC}"

ARCHIVE_NAME="${APP_NAME}-${VERSION}-${OS_TARGET}-${ARCH_TARGET}"
cd "${DIST_DIR}/${OS_TARGET}/${ARCH_TARGET}"

case "$OS_TARGET" in
    windows)
        # Create ZIP for Windows
        if command -v zip &> /dev/null; then
            zip -r "${ARCHIVE_NAME}.zip" "${APP_NAME}-${VERSION}-${OS_TARGET}-${ARCH_TARGET}"
            echo -e "${GREEN}✓${NC} Created: ${ARCHIVE_NAME}.zip"
        fi
        ;;
    *)
        # Create tar.gz for Unix-like systems
        tar czf "${ARCHIVE_NAME}.tar.gz" "${APP_NAME}-${VERSION}-${OS_TARGET}-${ARCH_TARGET}"
        echo -e "${GREEN}✓${NC} Created: ${ARCHIVE_NAME}.tar.gz"
        ;;
esac

# Generate checksums
echo ""
echo -e "${YELLOW}Generating checksums...${NC}"

if [ "$OS_TARGET" = "windows" ] && [ -f "${ARCHIVE_NAME}.zip" ]; then
    sha256sum "${ARCHIVE_NAME}.zip" > "${ARCHIVE_NAME}.zip.sha256"
    echo -e "${GREEN}✓${NC} Created: ${ARCHIVE_NAME}.zip.sha256"
elif [ -f "${ARCHIVE_NAME}.tar.gz" ]; then
    sha256sum "${ARCHIVE_NAME}.tar.gz" > "${ARCHIVE_NAME}.tar.gz.sha256"
    echo -e "${GREEN}✓${NC} Created: ${ARCHIVE_NAME}.tar.gz.sha256"
fi

# Create SHA256SUMS file for all archives in this directory
sha256sum *.{zip,tar.gz} 2>/dev/null > SHA256SUMS || true

cd - > /dev/null

# Clean up build directory
echo ""
echo -e "${YELLOW}Cleaning up...${NC}"
rm -rf "${BUILD_DIR}"
echo -e "${GREEN}✓${NC} Cleaned build directory"

# Final report
echo ""
echo "========================================="
echo -e "${GREEN}Build completed successfully!${NC}"
echo "========================================="
echo ""
echo "Output location:"
echo "  ${OUTPUT_DIR}"
echo ""
echo "Archive location:"
echo "  ${DIST_DIR}/${OS_TARGET}/${ARCH_TARGET}/${ARCHIVE_NAME}.*"
echo ""
echo "Next steps:"
echo "1. Test the executable in ${OUTPUT_DIR}"
echo "2. Verify the archive contents"
echo "3. Run dependency checks with scripts/check-deps.sh"
echo "4. Upload to release page when ready"
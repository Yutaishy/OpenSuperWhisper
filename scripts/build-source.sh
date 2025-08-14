#!/bin/bash
#
# Create source distribution for platforms where PyInstaller fails in CI
# This creates a portable package with all source code and a launcher script

set -e

# Configuration
APP_NAME="opensuperwhisper"
VERSION=${VERSION:-$(git describe --tags --always 2>/dev/null || echo "dev")}
OS_TARGET=${1:-$(uname -s | tr '[:upper:]' '[:lower:]')}
ARCH_TARGET=${2:-$(uname -m)}

# Normalize architecture names
case "$ARCH_TARGET" in
    x86_64|amd64) ARCH_TARGET="amd64" ;;
    aarch64|arm64) ARCH_TARGET="arm64" ;;
esac

# Normalize OS names
case "$OS_TARGET" in
    darwin|macos) OS_TARGET="darwin" ;;
    windows|win32|mingw*) OS_TARGET="windows" ;;
esac

echo "Creating source distribution for $OS_TARGET/$ARCH_TARGET"

# Create distribution directory
DIST_NAME="${APP_NAME}-${VERSION}-${OS_TARGET}-${ARCH_TARGET}-source"
OUTPUT_DIR="dist/${OS_TARGET}/${ARCH_TARGET}/${DIST_NAME}"
mkdir -p "$OUTPUT_DIR"

# Copy source code
echo "Copying source files..."
cp -r src/* "$OUTPUT_DIR/"
cp requirements.txt "$OUTPUT_DIR/"
cp README.md "$OUTPUT_DIR/" 2>/dev/null || true
cp LICENSE "$OUTPUT_DIR/" 2>/dev/null || true
cp CHANGELOG.md "$OUTPUT_DIR/" 2>/dev/null || true

# Create launcher scripts
if [ "$OS_TARGET" = "windows" ]; then
    # Windows batch launcher
    cat > "$OUTPUT_DIR/run.bat" << 'EOF'
@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt
echo Starting OpenSuperWhisper...
python run_app.py
pause
EOF
else
    # Unix launcher
    cat > "$OUTPUT_DIR/run.sh" << 'EOF'
#!/bin/bash
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt
echo "Starting OpenSuperWhisper..."
python3 run_app.py
EOF
    chmod +x "$OUTPUT_DIR/run.sh"
fi

# Create setup instructions
cat > "$OUTPUT_DIR/SETUP.md" << EOF
# OpenSuperWhisper Source Distribution

## Requirements
- Python 3.11 or higher
- pip

## Installation
1. Install Python from https://python.org
2. Run the launcher script:
   - Windows: Double-click run.bat
   - macOS/Linux: Run ./run.sh

## Manual Setup
\`\`\`bash
pip install -r requirements.txt
python run_app.py
\`\`\`
EOF

# Create archive
cd "dist/${OS_TARGET}/${ARCH_TARGET}"
if [ "$OS_TARGET" = "windows" ]; then
    # Create ZIP for Windows
    if command -v zip &> /dev/null; then
        zip -r "${DIST_NAME}.zip" "${DIST_NAME}"
        echo "Created: ${DIST_NAME}.zip"
    fi
else
    # Create tar.gz for Unix
    tar czf "${DIST_NAME}.tar.gz" "${DIST_NAME}"
    echo "Created: ${DIST_NAME}.tar.gz"
fi

# Generate checksum
sha256sum "${DIST_NAME}".* > "${DIST_NAME}.sha256"

echo "Source distribution created successfully!"
echo "Location: dist/${OS_TARGET}/${ARCH_TARGET}/${DIST_NAME}.*"
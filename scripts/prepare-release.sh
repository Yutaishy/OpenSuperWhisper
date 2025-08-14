#!/bin/bash
#
# Release preparation script
# Creates release assets and documentation

set -e

# Configuration
VERSION=${1:-$(git describe --tags --always 2>/dev/null || echo "v0.0.0")}
RELEASE_DIR="release-${VERSION}"
PLATFORMS=("linux/amd64" "linux/arm64" "darwin/amd64" "darwin/arm64" "windows/amd64")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print banner
echo "========================================="
echo "Release Preparation"
echo "Version: $VERSION"
echo "========================================="

# Function to print section
print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Create release directory
print_section "Creating release directory"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"
echo -e "${GREEN}✓ Created $RELEASE_DIR${NC}"

# ==========================================
# Build for all platforms
# ==========================================
print_section "Building for all platforms"

for platform in "${PLATFORMS[@]}"; do
    IFS='/' read -r os arch <<< "$platform"
    echo ""
    echo "Building for $os/$arch..."
    
    if [ -f "scripts/build.sh" ]; then
        chmod +x scripts/build.sh
        scripts/build.sh "$os" "$arch" || {
            echo -e "${YELLOW}⚠ Build failed for $os/$arch${NC}"
            continue
        }
    fi
done

# ==========================================
# Collect release assets
# ==========================================
print_section "Collecting release assets"

# Find all built archives
for platform in "${PLATFORMS[@]}"; do
    IFS='/' read -r os arch <<< "$platform"
    
    # Find archives
    for archive in dist/"$os"/"$arch"/*.{zip,tar.gz} 2>/dev/null; do
        if [ -f "$archive" ]; then
            cp "$archive" "$RELEASE_DIR/"
            echo -e "${GREEN}✓ Copied $(basename "$archive")${NC}"
        fi
    done
    
    # Find checksums
    for checksum in dist/"$os"/"$arch"/*.sha256 2>/dev/null; do
        if [ -f "$checksum" ]; then
            cp "$checksum" "$RELEASE_DIR/"
            echo -e "${GREEN}✓ Copied $(basename "$checksum")${NC}"
        fi
    done
done

# ==========================================
# Generate combined SHA256SUMS
# ==========================================
print_section "Generating combined checksums"

cd "$RELEASE_DIR"
sha256sum *.{zip,tar.gz} 2>/dev/null > SHA256SUMS || true
cd - > /dev/null

if [ -f "$RELEASE_DIR/SHA256SUMS" ]; then
    echo -e "${GREEN}✓ Created SHA256SUMS${NC}"
fi

# ==========================================
# Generate release notes
# ==========================================
print_section "Generating release notes"

cat > "$RELEASE_DIR/RELEASE_NOTES.md" << EOF
# OpenSuperWhisper ${VERSION}

Release Date: $(date -u +"%Y-%m-%d")

## 📦 Installation

### Quick Install

#### Linux/macOS
\`\`\`bash
# Download and extract
curl -L https://github.com/\${GITHUB_REPOSITORY}/releases/download/${VERSION}/opensuperwhisper-${VERSION}-\$(uname -s | tr '[:upper:]' '[:lower:]')-\$(uname -m).tar.gz | tar xz

# Run
./opensuperwhisper
\`\`\`

#### Windows
\`\`\`powershell
# Download
Invoke-WebRequest -Uri "https://github.com/\${GITHUB_REPOSITORY}/releases/download/${VERSION}/opensuperwhisper-${VERSION}-windows-amd64.zip" -OutFile "opensuperwhisper.zip"

# Extract
Expand-Archive -Path "opensuperwhisper.zip" -DestinationPath "."

# Run
.\opensuperwhisper.exe
\`\`\`

### Docker
\`\`\`bash
docker pull ghcr.io/\${GITHUB_REPOSITORY}:${VERSION}
docker run -p 8000:8000 ghcr.io/\${GITHUB_REPOSITORY}:${VERSION}
\`\`\`

## 🎯 What's New

$(if [ -f CHANGELOG.md ]; then
    # Extract changes for this version
    sed -n "/^## ${VERSION}/,/^## /p" CHANGELOG.md | sed '$d' | tail -n +2
else
    echo "- See commit history for changes"
fi)

## 📊 Supported Platforms

| Platform | Architecture | File |
|----------|-------------|------|
| Linux | x86_64 | opensuperwhisper-${VERSION}-linux-amd64.tar.gz |
| Linux | ARM64 | opensuperwhisper-${VERSION}-linux-arm64.tar.gz |
| macOS | Intel | opensuperwhisper-${VERSION}-darwin-amd64.tar.gz |
| macOS | Apple Silicon | opensuperwhisper-${VERSION}-darwin-arm64.tar.gz |
| Windows | x86_64 | opensuperwhisper-${VERSION}-windows-amd64.zip |

## ✅ Verification

### Verify checksums
\`\`\`bash
# Linux/macOS
sha256sum -c SHA256SUMS

# Windows
CertUtil -hashfile opensuperwhisper-${VERSION}-windows-amd64.zip SHA256
\`\`\`

### Verify signatures (if available)
\`\`\`bash
cosign verify ghcr.io/\${GITHUB_REPOSITORY}:${VERSION}
\`\`\`

## 📋 System Requirements

- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 500MB free space
- **OS**: 
  - Linux: Ubuntu 20.04+, Debian 10+, RHEL 8+, or compatible
  - macOS: 10.15 (Catalina) or later
  - Windows: Windows 10 version 1909+ or Windows 11

## 🐛 Known Issues

$(if [ -f "docs/KNOWN_ISSUES.md" ]; then
    cat docs/KNOWN_ISSUES.md
else
    echo "- No known issues at this time"
fi)

## 📖 Documentation

- [Installation Guide](https://github.com/\${GITHUB_REPOSITORY}/blob/main/docs/INSTALLATION.md)
- [Configuration](https://github.com/\${GITHUB_REPOSITORY}/blob/main/docs/CONFIGURATION.md)
- [API Reference](https://github.com/\${GITHUB_REPOSITORY}/blob/main/docs/API.md)
- [Troubleshooting](https://github.com/\${GITHUB_REPOSITORY}/blob/main/docs/TROUBLESHOOTING.md)

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue:
https://github.com/\${GITHUB_REPOSITORY}/issues

## 📄 License

This software is released under the MIT License.
See [LICENSE](https://github.com/\${GITHUB_REPOSITORY}/blob/main/LICENSE) for details.

---
*Generated on $(date -u +"%Y-%m-%d %H:%M:%S") UTC*
EOF

echo -e "${GREEN}✓ Created RELEASE_NOTES.md${NC}"

# ==========================================
# Generate install script
# ==========================================
print_section "Generating install scripts"

# Unix install script
cat > "$RELEASE_DIR/install.sh" << 'EOF'
#!/bin/bash
# OpenSuperWhisper installer script

set -e

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

# Normalize architecture
case "$ARCH" in
    x86_64|amd64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

VERSION="${VERSION:-latest}"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"

echo "Installing OpenSuperWhisper..."
echo "OS: $OS | Arch: $ARCH | Version: $VERSION"

# Download URL
if [ "$VERSION" = "latest" ]; then
    URL="https://github.com/${GITHUB_REPOSITORY}/releases/latest/download/opensuperwhisper-$OS-$ARCH.tar.gz"
else
    URL="https://github.com/${GITHUB_REPOSITORY}/releases/download/$VERSION/opensuperwhisper-$VERSION-$OS-$ARCH.tar.gz"
fi

# Download and install
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Downloading from $URL..."
curl -L "$URL" | tar xz -C "$TEMP_DIR"

echo "Installing to $INSTALL_DIR..."
sudo install -m 755 "$TEMP_DIR/opensuperwhisper" "$INSTALL_DIR/"

echo "✓ Installation complete!"
echo "Run 'opensuperwhisper --help' to get started"
EOF

chmod +x "$RELEASE_DIR/install.sh"
echo -e "${GREEN}✓ Created install.sh${NC}"

# Windows install script
cat > "$RELEASE_DIR/install.ps1" << 'EOF'
# OpenSuperWhisper installer script for Windows

param(
    [string]$Version = "latest",
    [string]$InstallDir = "$env:LOCALAPPDATA\OpenSuperWhisper"
)

Write-Host "Installing OpenSuperWhisper..." -ForegroundColor Cyan
Write-Host "Version: $Version | Install Dir: $InstallDir"

# Create install directory
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# Download URL
if ($Version -eq "latest") {
    $url = "https://github.com/$env:GITHUB_REPOSITORY/releases/latest/download/opensuperwhisper-windows-amd64.zip"
} else {
    $url = "https://github.com/$env:GITHUB_REPOSITORY/releases/download/$Version/opensuperwhisper-$Version-windows-amd64.zip"
}

# Download
$zipFile = "$env:TEMP\opensuperwhisper.zip"
Write-Host "Downloading from $url..."
Invoke-WebRequest -Uri $url -OutFile $zipFile

# Extract
Write-Host "Extracting..."
Expand-Archive -Path $zipFile -DestinationPath $InstallDir -Force

# Add to PATH
$path = [Environment]::GetEnvironmentVariable("Path", "User")
if ($path -notlike "*$InstallDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$path;$InstallDir", "User")
    Write-Host "Added to PATH"
}

# Cleanup
Remove-Item $zipFile

Write-Host "✓ Installation complete!" -ForegroundColor Green
Write-Host "Restart your terminal and run 'opensuperwhisper --help' to get started"
EOF

echo -e "${GREEN}✓ Created install.ps1${NC}"

# ==========================================
# Create verification script
# ==========================================
print_section "Creating verification script"

cat > "$RELEASE_DIR/verify-release.sh" << EOF
#!/bin/bash
# Release verification script

echo "Verifying OpenSuperWhisper ${VERSION} release assets..."
echo ""

# Check SHA256
if command -v sha256sum &> /dev/null; then
    echo "Verifying checksums..."
    sha256sum -c SHA256SUMS
else
    echo "sha256sum not found, skipping checksum verification"
fi

echo ""
echo "Release contents:"
ls -lh *.{zip,tar.gz} 2>/dev/null

echo ""
echo "✓ Verification complete"
EOF

chmod +x "$RELEASE_DIR/verify-release.sh"
echo -e "${GREEN}✓ Created verify-release.sh${NC}"

# ==========================================
# Summary
# ==========================================
print_section "Release preparation complete!"

echo ""
echo "Release assets in: $RELEASE_DIR/"
echo ""
echo "Contents:"
ls -la "$RELEASE_DIR" | tail -n +2

echo ""
echo "Total size: $(du -sh "$RELEASE_DIR" | cut -f1)"
echo ""
echo "Next steps:"
echo "1. Review RELEASE_NOTES.md"
echo "2. Test installation scripts"
echo "3. Create GitHub release with: gh release create ${VERSION} ${RELEASE_DIR}/*"
echo "4. Push Docker images with: scripts/docker-build.sh"
echo ""
echo -e "${GREEN}Ready for release!${NC}"
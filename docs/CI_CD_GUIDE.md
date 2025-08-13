# CI/CD Guide for OpenSuperWhisper

## Overview

This document describes the continuous integration and deployment pipeline for OpenSuperWhisper, including automated builds, testing, signing, and release distribution.

## Workflows

### 1. Test Build Workflow (`test-build.yml`)

**Trigger**: Push to main/develop branches, pull requests, or manual dispatch

**Purpose**: Validate that the application builds successfully on all target platforms

**Platforms**:
- Linux (Ubuntu 20.04) - x64
- Windows (Windows Server 2022) - x64  
- macOS (macOS 14) - ARM64 (Apple Silicon)
- macOS (macOS 13) - x64 (Intel)

**Key Features**:
- Matrix build strategy for parallel execution
- Dependency caching for faster builds
- Build verification steps
- Test artifact upload (1-day retention)

### 2. Release Workflow (`release.yml`)

**Trigger**: Push of tags matching `v*.*.*` pattern

**Purpose**: Create production releases with signed binaries

**Process**:
1. Build executables for all platforms
2. Code signing (if certificates configured)
3. Generate SBOM (Software Bill of Materials)
4. Create build attestations
5. Package and create checksums
6. Upload to GitHub Release
7. Send Discord notification

## Setup Instructions

### Prerequisites

1. **Python 3.12** must be specified in `pyproject.toml`
2. **PyInstaller 6.0+** for executable creation
3. Platform-specific dependencies documented in workflows

### Required Secrets

Configure these in GitHub repository settings:

#### Windows Code Signing (Optional)
- `WINDOWS_CERT_BASE64`: Base64-encoded PFX certificate
- `WINDOWS_CERT_PASSWORD`: Certificate password

#### macOS Code Signing (Optional)
- `APPLE_DEVELOPER_ID`: Developer ID for signing
- `APPLE_APP_PASSWORD`: App-specific password for notarization
- `APPLE_TEAM_ID`: Apple Developer Team ID

#### Discord Notifications (Optional)
- `DISCORD_WEBHOOK`: Discord webhook URL for release announcements

### Creating a Release

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.6.15"  # Increment as needed
   ```

2. **Update CHANGELOG.md** with release notes

3. **Create and push tag**:
   ```bash
   git tag v0.6.15
   git push origin v0.6.15
   ```

4. **Monitor workflow** at Actions tab in GitHub

5. **Verify release** at Releases page

## Platform-Specific Notes

### Windows
- Uses `onedir` mode to prevent DLL access violations
- Excludes UPX compression to avoid antivirus false positives
- SmartScreen warnings expected for unsigned builds

### macOS
- Separate builds for Intel (x64) and Apple Silicon (ARM64)
- Notarization requires Apple Developer account
- DMG format preferred for distribution with stapling

### Linux
- Built on Ubuntu 20.04 for glibc compatibility
- Requires PortAudio runtime dependency
- Distributed as tar.gz archive

## Build Configuration

### PyInstaller Settings

Key configurations in `build_executable.py`:
- `--onedir`: Creates a directory bundle (more reliable)
- `--windowed`: No console window
- `--noupx`: Disabled to prevent false positives
- Platform-specific icon files
- Extensive hidden imports for PySide6

### Dependency Management

Critical dependencies:
- PySide6 for GUI
- openai for API integration
- sounddevice for audio recording
- cryptography for secure storage

## Security Considerations

### Code Signing

**Windows**:
- Uses SHA256 for signing
- Timestamp server ensures long-term validity
- SignTool or Azure Trusted Signing

**macOS**:
- Runtime hardening enabled
- Notarization for Gatekeeper approval
- Stapling for offline verification

**Linux**:
- SHA256 checksums provided
- Optional Sigstore integration possible

### SBOM Generation

- CycloneDX format for standardization
- Includes all Python dependencies
- Attached to each release

### Build Attestations

- SLSA-compliant provenance
- GitHub-native attestation format
- Cryptographically signed

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies installed
   - Review platform-specific requirements

2. **Signing Failures**
   - Ensure secrets properly configured
   - Check certificate expiration
   - Verify entitlements (macOS)

3. **Release Creation Issues**
   - Confirm tag format matches pattern
   - Check GitHub permissions
   - Verify artifact upload completed

### Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller>=6.0

# Build executable
python build_executable.py OpenSuperWhisper

# Check output
ls -la dist/OpenSuperWhisper/
```

## Monitoring

### Workflow Status
- GitHub Actions tab shows real-time progress
- Email notifications for failures
- Workflow run retention: 90 days

### Release Metrics
- Download counts visible on Releases page
- SBOM provides dependency tracking
- Attestations ensure build integrity

## Best Practices

1. **Version Management**
   - Follow semantic versioning
   - Tag only from stable branches
   - Update changelog before release

2. **Testing**
   - Run test build before creating release
   - Verify on clean environment
   - Test signed binaries when possible

3. **Documentation**
   - Keep README current
   - Document breaking changes
   - Include migration guides

## Support

For CI/CD issues:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Open issue with workflow run link
4. Contact maintainers if urgent

## References

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [PyInstaller Manual](https://pyinstaller.org/documentation.html)
- [Apple Notarization Guide](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
- [Windows Authenticode Signing](https://docs.microsoft.com/windows/win32/seccrypto/signtool)
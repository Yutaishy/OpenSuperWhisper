# Release Checklist for OpenSuperWhisper

## Pre-Release Checklist

### 1. Code Preparation
- [ ] All features for release are merged to main branch
- [ ] All tests are passing
- [ ] Code has been reviewed and approved
- [ ] No critical bugs in issue tracker

### 2. Version Update
- [ ] Update version in `pyproject.toml`
- [ ] Update version badge in `README.md`
- [ ] Update `CHANGELOG.md` with release notes

### 3. Testing
- [ ] Run test build workflow manually for all platforms
- [ ] Download and test artifacts from test build
- [ ] Verify application starts on clean system
- [ ] Test core functionality (recording, transcription, formatting)

### 4. Documentation
- [ ] README.md is up to date
- [ ] API documentation is current
- [ ] Installation instructions are accurate
- [ ] Known issues are documented

## Release Process

### 1. Create Release Tag
```bash
# Ensure you're on main branch with latest changes
git checkout main
git pull origin main

# Create annotated tag
git tag -a v0.6.15 -m "Release v0.6.15: <brief description>"

# Push tag to trigger release workflow
git push origin v0.6.15
```

### 2. Monitor Release Workflow
- Go to [Actions tab](https://github.com/Yutaishy/OpenSuperWhisper/actions)
- Watch "Release" workflow progress
- Verify all platform builds succeed
- Check that artifacts are uploaded

### 3. Verify GitHub Release
- Go to [Releases page](https://github.com/Yutaishy/OpenSuperWhisper/releases)
- Confirm release is created with correct tag
- Verify all platform downloads are present:
  - `windows-x64.zip` + `.sha256`
  - `macos-arm64.dmg` + `.sha256`
  - `macos-x64.dmg` + `.sha256`
  - `linux-x64.tar.gz` + `.sha256`
  - SBOM files for each platform

### 4. Post-Release Testing
- [ ] Download each platform archive
- [ ] Verify SHA256 checksums match
- [ ] Test installation on clean VMs if available
- [ ] Confirm Discord notification was sent (if configured)

## Platform-Specific Verification

### Windows
- [ ] Download `windows-x64.zip`
- [ ] Extract to test directory
- [ ] Run `OpenSuperWhisper.exe`
- [ ] Verify no antivirus warnings (or document if present)
- [ ] Test with Windows Defender enabled

### macOS
- [ ] Download appropriate DMG (ARM64 or x64)
- [ ] Mount DMG
- [ ] Drag to Applications
- [ ] First launch: Right-click → Open
- [ ] Grant microphone and accessibility permissions
- [ ] Verify notarization: `spctl -a -vv /Applications/OpenSuperWhisper.app`

### Linux
- [ ] Download `linux-x64.tar.gz`
- [ ] Extract: `tar -xzf linux-x64.tar.gz`
- [ ] Install dependencies: `sudo apt-get install libportaudio2`
- [ ] Run: `./OpenSuperWhisper/OpenSuperWhisper`
- [ ] Verify audio recording works

## Troubleshooting

### Build Failures
1. Check workflow logs for specific error
2. Verify all secrets are configured correctly
3. Ensure dependencies haven't changed
4. Test locally with same Python version

### Signing Issues
- **Windows**: Certificate may be expired or invalid
- **macOS**: Check Apple Developer account status
- **Both**: Signing is optional, builds work without it

### Release Not Created
1. Verify tag format matches `v*.*.*`
2. Check permissions for GITHUB_TOKEN
3. Ensure workflow has write access to releases

### Missing Artifacts
1. Check individual build job logs
2. Verify artifact upload steps completed
3. Check for disk space issues in runners

## Rollback Procedure

If critical issues are found post-release:

1. **Mark as Pre-release**:
   - Edit release on GitHub
   - Check "This is a pre-release"
   - Save changes

2. **Create Hotfix**:
   ```bash
   git checkout -b hotfix/v0.6.15.1
   # Make fixes
   git commit -m "Fix: <description>"
   git push origin hotfix/v0.6.15.1
   ```

3. **New Release**:
   ```bash
   git checkout main
   git merge hotfix/v0.6.15.1
   git tag -a v0.6.15.1 -m "Hotfix release"
   git push origin v0.6.15.1
   ```

## Security Considerations

### Secrets Management
- Never commit API keys or certificates
- Rotate secrets regularly
- Use GitHub Secrets for sensitive data
- Document which secrets are required

### Code Signing Status
- **Windows**: Optional, reduces SmartScreen warnings
- **macOS**: Recommended for distribution
- **Linux**: SHA256 checksums provided

### Vulnerability Scanning
- Dependabot alerts enabled
- Regular dependency updates
- SBOM included for supply chain visibility

## Communication

### Release Announcement Template
```markdown
🚀 OpenSuperWhisper v0.6.15 Released!

## What's New
- Feature 1
- Feature 2
- Bug fixes

## Downloads
- [Windows](link)
- [macOS ARM64](link)
- [macOS Intel](link)
- [Linux](link)

## Changelog
See full changelog: [CHANGELOG.md](link)

## Feedback
Report issues: [GitHub Issues](link)
```

### Channels to Update
- [ ] GitHub Release notes
- [ ] Discord announcement (automatic if webhook configured)
- [ ] Project README version badge
- [ ] Social media (if applicable)

## Next Steps After Release

1. **Monitor Feedback**
   - Watch GitHub Issues for bug reports
   - Check Discord for user feedback
   - Monitor download statistics

2. **Plan Next Release**
   - Create milestone for next version
   - Triage and prioritize issues
   - Update project board

3. **Maintenance**
   - Address critical bugs quickly
   - Update dependencies regularly
   - Keep documentation current

## Useful Commands

```bash
# View recent tags
git tag -l --sort=-v:refname | head -5

# Delete local tag (if needed)
git tag -d v0.6.15

# Delete remote tag (use with caution)
git push origin --delete v0.6.15

# Create release branch
git checkout -b release/v0.6.15

# View release workflow runs
gh run list --workflow=release.yml

# Download artifacts from workflow
gh run download <run-id>

# Create release manually (if automation fails)
gh release create v0.6.15 --title "v0.6.15" --notes-file RELEASE_NOTES.md
```

## References

- [CI/CD Guide](CI_CD_GUIDE.md)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [GitHub Releases](https://docs.github.com/repositories/releasing-projects-on-github)
- [Semantic Versioning](https://semver.org/)
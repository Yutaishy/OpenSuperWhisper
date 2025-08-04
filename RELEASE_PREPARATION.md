# OpenSuperWhisper v0.6.14 Release Preparation

## Date: 2025-08-04

This document summarizes the release preparation for v0.6.14.

## 🎯 Release Overview

### Version: v0.6.14
- **Type**: Production Release with Executable Builds
- **Key Changes**: 
  - Fixed CI/CD build errors (Docker, Ruff, mypy)
  - Added executable builds for all platforms
  - Improved Windows GUI test handling in CI

## ✅ Pre-Release Checklist

### 1. Version Consistency ✅
- [x] pyproject.toml: `version = "0.6.14"`
- [x] run_app.py: `OpenSuperWhisper v0.6.14`
- [x] README.md: Badge shows v0.6.14
- [x] CHANGELOG.md: v0.6.14 entry added
- [x] .claude/CLAUDE.md: Updated to v0.6.14

### 2. Directory Structure ✅
- [x] Removed inappropriate `%APPDATA%/` folder from root
- [x] Updated .gitignore to prevent Windows-specific folders
- [x] Maintained clean project structure
- [x] Archive folder properly organized

### 3. Build Verification ✅
- [x] Docker image builds successfully
- [x] Windows executable created and uploaded
- [x] macOS executable created and uploaded
- [x] Linux executable created and uploaded

### 4. Documentation ✅
- [x] CHANGELOG.md updated with all fixes
- [x] Build workflow documented in `.claude/docs/BUILD_RELEASE_WORKFLOW.md`
- [x] CI/CD error patterns documented in global knowledge base

### 5. GitHub Release ✅
- [x] Tag created: v0.6.14
- [x] Release notes prepared
- [x] All 3 platform executables attached:
  - OpenSuperWhisper-Windows.zip
  - OpenSuperWhisper-macOS.zip
  - OpenSuperWhisper-Linux.zip

## 📁 Final Directory Structure

```
voice_input_v2/
├── OpenSuperWhisper/        # Main application code ✅
├── tests/                   # Archived (in archive/release_preparation/)
├── docs/                    # Project documentation ✅
├── .claude/                 # Project management ✅
│   └── docs/               # Project-specific docs ✅
├── assets/                  # Application assets ✅
├── brand/                   # Brand materials ✅
├── style_guides/           # Style configuration ✅
├── archive/                # Development archives ✅
├── logs/                   # Active logs (gitignored) ✅
├── run_app.py              # Main entry point ✅
├── web_server.py           # Web API server ✅
├── build_executable.py     # Build script ✅
├── requirements.txt        # Dependencies ✅
├── pyproject.toml          # Project config ✅
├── Dockerfile              # Docker config ✅
├── README.md               # Project description ✅
├── CHANGELOG.md            # Version history ✅
├── LICENSE                 # MIT License ✅
├── SECURITY.md             # Security policy ✅
├── CODE_OF_CONDUCT.md      # Community guidelines ✅
├── CONTRIBUTING.md         # Contribution guide ✅
└── RELEASE_PREPARATION.md  # This file ✅
```

## 🚀 Release Status

**READY FOR RELEASE** - All checks passed, executables built, documentation updated.

---
Last updated: 2025-08-04 12:00 JST
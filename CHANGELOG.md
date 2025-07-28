# CHANGELOG

## [Unreleased]

## [0.6.8] - 2025-07-28 (SSL Certificate Fix for API Connections)
### Fixed
- **Critical SSL/TLS Issue**: Fixed OpenAI API connection errors in bundled executables
  - ✅ Added proper SSL certificate bundling with `--collect-all=certifi`
  - ✅ Included OpenAI package dependencies with `--collect-all=openai`
  - ✅ Added explicit imports for ssl, urllib3, and requests modules
  - ✅ Resolved "Processing failed: ASR transcription failed: Connection error"

### Enhanced
- **Build Configuration**: Improved PyInstaller settings for network connectivity
  - Ensures SSL certificates are properly bundled in onedir mode
  - Fixed regression from v0.6.6 where onedir transition broke API connections
  - All platforms now include complete SSL/TLS support

### Technical
- Modified build_executable.py to include certifi and SSL dependencies
- Added hidden imports for networking libraries
- Ensures proper HTTPS connections to OpenAI API endpoints

## [0.6.7] - 2025-07-28 (Windows DLL Testing and Validation)
### Fixed
- **Windows Build Configuration**: Removed `--strip` option on Windows to prevent DLL loading issues
  - ✅ Strip option now only applied to non-Windows platforms
  - ✅ Minimized Windows-specific PyInstaller settings for better compatibility
  - ✅ Added automated executable testing in CI/CD pipeline
  - ✅ Implemented `--version` flag for quick validation testing

### Enhanced
- **CI/CD Testing**: Added Windows executable validation step in GitHub Actions
  - Tests for DLL loading errors before release
  - Catches "Failed to load Python DLL" errors automatically
  - Ensures executables are functional before distribution
- **Build Reliability**: Improved Windows build stability and compatibility

### Technical
- Modified build_executable.py to conditionally apply strip option
- Added PowerShell test script in workflow for Windows executable validation
- Implemented version argument handling in run_app.py

## [0.6.6] - 2025-07-28 (Windows DLL Access Violation Fix)
### Fixed
- **Windows Critical Issue:** Resolved Python DLL access violation error ("メモリ ロケーションへのアクセスが無効です")
  - ✅ Changed all platforms to onedir mode for maximum compatibility
  - ✅ Eliminated onefile mode that caused DLL loading issues in temporary directories
  - ✅ Updated GitHub Actions workflow to handle onedir builds consistently
  - ✅ Windows executable now runs reliably without memory access violations

### Enhanced
- **Cross-Platform Consistency:** Unified build approach across Windows, macOS, and Linux
- **Distribution Reliability:** Directory-based distribution prevents DLL isolation issues
- **Build Process:** Improved GitHub Actions workflow for onedir mode handling

## [0.6.5] - 2025-07-28 (Complete Windows Fix Release)
### Fixed
- **Windows Artifact Issue:** Fixed Windows ZIP not being included in releases
  - ✅ Corrected artifact upload path for Windows onefile builds
  - ✅ All three platforms (Windows, macOS, Linux) now properly included in releases
  - ✅ Windows single-file executable working without DLL errors

### Enhanced
- **Documentation:** Updated README.md to reflect Windows onefile distribution
- **Third-party Ready:** Repository fully prepared for public release

## [0.6.4] - 2025-07-28 (Windows DLL Fix Release)
### Fixed
- **Windows Critical Issue:** Fixed Python DLL loading error causing "LoadLibrary: メモリ ロケーションへのアクセスが無効です"
  - ✅ Changed Windows build from onedir to onefile mode for better DLL compatibility
  - ✅ Added Windows-specific PyInstaller configurations for stability
  - ✅ Fixed ZIP file naming consistency in release workflow
  - ✅ Windows executable now runs without DLL access violations

### Enhanced
- **Windows Build:** Improved Windows-specific build process with better error handling
- **Distribution:** Single-file Windows executable for easier deployment

## [0.6.3] - 2025-07-28 (Complete Cross-Platform Release)
### Fixed
- **Windows Release Issue:** Fixed ZIP file naming inconsistency in GitHub Actions workflow
  - ✅ Windows builds now properly included in releases (OpenSuperWhisper.exe.zip → OpenSuperWhisper-Windows.zip)
  - ✅ All three platforms (Windows, macOS, Linux) now available in releases

## [0.6.2] - 2025-07-28 (macOS Build Fix Release)
### Fixed
- **macOS PyInstaller Build:** Fixed framework collision error when building on macOS ARM64
  - ✅ Excluded problematic Qt3D and multimedia modules on macOS to prevent framework conflicts
  - ✅ Limited PySide6 inclusion to essential modules only (QtCore, QtGui, QtWidgets, QtNetwork)
  - ✅ Maintained `--collect-all=PySide6` for Windows and Linux platforms
  - ✅ Resolved "File exists" error in Qt framework Resources directory
  - ✅ Added Pillow dependency to GitHub Actions for icon conversion

### Enhanced
- **Dependencies:** Added Pillow to core requirements for cross-platform icon support
- **Documentation:** Updated README.md with clearer download instructions and platform-specific guidance
- **CI/CD:** Improved GitHub Actions with better error reporting and platform-specific handling
- **Release Process:** All three platforms (Windows, macOS, Linux) now build successfully

## [0.6.1] - 2025-07-28 (Security Enhancement Release)
### Fixed
- **Antivirus False Positives:** Resolved Microsoft Defender and other AV software blocking executables
  - ✅ **UPX Compression Disabled**: Removed UPX compression globally to prevent AV false positives
  - ✅ **Onedir Distribution**: Changed from onefile to onedir mode for improved security scanning
  - ✅ **Debug Stripping**: Added `--strip` flag to remove debug information that triggers heuristics
  - ✅ **Module Exclusions**: Excluded unnecessary modules that can trigger security warnings

### Enhanced
- **Distribution Method:** ZIP archives containing application folder for better compatibility
- **Build Security:** Comprehensive security-focused PyInstaller configuration
- **Cross-Platform Compatibility:** Improved distribution format for all platforms

### Technical
- **Build Mode:** Changed from `--onefile` to `--onedir` for security
- **Compression:** Disabled UPX globally with `--noupx` flag
- **Artifacts:** GitHub Actions now creates platform-specific ZIP files
- **Module Optimization:** Excluded development and unused modules

### Important Notes
- **Windows Users**: Extract ZIP and run the executable from the extracted folder
- **Security**: This release specifically addresses antivirus software compatibility
- **Distribution**: Each platform now receives a ZIP file instead of a single executable

## [0.6.0] - 2025-07-28 (Brand Identity Release)
### Added
- **Complete Brand Identity:** Professional icon system with Wave + Quote design
  - ✅ Multi-platform icon support (Windows ICO, iOS AppIcon.appiconset, Android mipmap)
  - ✅ Web icons and PWA manifest for future web deployment
  - ✅ GitHub social preview image for enhanced repository presentation
- **Application Icon Integration:** Consistent branding across all windows
  - ✅ Main window icon integration
  - ✅ Recording indicator window icon
  - ✅ First-run wizard window icon
  - ✅ PyInstaller executable icon configuration
- **Brand Asset Management:** Complete brand guidelines and assets
  - ✅ Master icon files (2048px background, 1024px foreground glyph)
  - ✅ Color palette documentation (#0EA5E9 → #14B8A6 gradient)
  - ✅ Artwork licensing and usage guidelines
  - ✅ Platform-specific icon specifications

### Enhanced
- **Visual Polish:** Professional appearance with consistent iconography
- **Build System:** Integrated icon assets into automated build pipeline
- **Developer Experience:** Complete brand asset organization for future development

### Technical
- **Icon Generation:** Comprehensive multi-platform icon pack
- **Cross-Platform Build:** Added Pillow dependency for automatic icon conversion
- **Platform-Specific Icons:** Windows ICO, macOS/Linux PNG with PyInstaller auto-conversion
- **Color Scheme:** Cyan-to-teal gradient with light cyan accents
- **File Organization:** Structured assets/ and brand/ directories

### Fixed
- **macOS Build Issue:** Resolved "only ('icns',) images may be used as icons" error
- **Icon Compatibility:** Platform-specific icon paths for seamless builds
- **Dependencies:** Added Pillow>=9.0.0 for PyInstaller icon processing

## [0.5.0] - 2025-07-27 (Production Release)
### Added
- **Complete CI/CD Pipeline:** Full GitHub Actions integration
  - ✅ Cross-platform testing (Windows, macOS, Linux)
  - ✅ Automated builds and releases
  - ✅ Security vulnerability scanning
  - ✅ Code quality enforcement (ruff, mypy)
- **Production-Ready Status:** Project elevated to stable/production
- **GitHub Actions Badges:** Live CI/CD status indicators in README
- **Release Automation:** Automated executable generation for all platforms

### Fixed
- **Linux EGL Dependencies:** Resolved Qt GUI issues in headless CI environments
- **Windows PowerShell Compatibility:** Fixed shell script execution errors
- **Unicode Encoding:** Resolved Windows cp1252 character encoding issues
- **Type Safety:** Complete mypy compliance with proper type annotations
- **Code Quality:** Full ruff linting compliance with modern Python standards

### Changed
- **Project Structure:** Cleaned up development artifacts and cache files
- **Version Management:** Updated to semantic versioning v0.5.0
- **Documentation:** Enhanced with CI/CD badges and status indicators

## [0.4.0] - 2025-07-27
### Added
- **Advanced Preset Management:** Complete CRUD operations for formatting prompts
  - ➕ Add new presets with custom names and content
  - ✏️ Edit existing preset names (default presets protected)
  - 💾 Save/update prompt content for existing presets
  - 🗑️ Delete custom presets with confirmation dialogs
- **Enhanced UI:** Added four management buttons to preset toolbar
- **Built-in Preset Library:** Professional presets for meetings, technical docs, and blog articles
- **Smart Preset Protection:** Default presets cannot be edited or deleted
- **Real-time UI Updates:** Dropdown automatically reflects preset changes

### Fixed
- **Preset Validation:** Prevents duplicate names and empty content
- **UI Consistency:** Proper signal blocking during programmatic updates
- **Data Persistence:** All preset changes automatically saved to settings

## [0.3.0] - 2025-07-27 (GitHub Release Ready)
### Added
- **Enhanced Recording Indicator:** Clear text display showing "Recording", "Processing", and "Completed" states
- **Improved UX:** Larger indicator (160x50) with professional styling and better visibility
- **Background Processing:** Heavy transcription/formatting now runs in separate threads to prevent GUI freezing
- **Improved Audio Quality:** Enhanced audio format handling and normalization for better transcription accuracy
- **Robust Hotkey System:** Multi-layer debouncing prevents accidental double-triggers
- **Clean Output Processing:** Automatic removal of unwanted formatting artifacts (TRANSCRIPT tags)
- **Professional Dark Theme:** Clean, modern UI design replacing previous cluttered interface
- **GitHub CI/CD:** Automated testing and building pipeline with multi-platform support
- **Production Structure:** Proper project structure with separated requirements and development tools

### Fixed
- **GUI Responsiveness:** Eliminated freezing when using global hotkeys
- **Audio Format Issues:** Proper float64 to int16 conversion prevents corrupted audio files
- **Hotkey Reliability:** Resolved duplicate triggering and immediate stop issues
- **Output Cleanliness:** Ensured formatted text contains no processing artifacts
- **Import Issues:** Fixed relative import problems for proper module loading

### Changed
- **Removed Debug Output:** Production-ready code with minimal console output
- **Optimized Performance:** Better resource management and cleanup
- **Enhanced Error Handling:** More graceful failure recovery
- **Clean Project Structure:** Organized files for GitHub publication with proper documentation

## [0.2.0] - 2025-07-26
### Added
- **Global Hotkey System:** `Ctrl+Space` now works everywhere (even when app is minimized)
  - Multi-layer fallback system: Windows API → pynput → direct polling
  - Cross-platform keyboard monitoring with 50ms response time
- **Auto-Clipboard Integration:** Results automatically copied to clipboard for instant `Ctrl+V` paste
  - Smart selection: formatted text when available, raw when formatting disabled
  - Visual feedback with "📋 Copied to clipboard!" notifications
- **Always-On-Top Recording Indicator:** Blinking red dot overlay during recording
  - Visible on all monitors and applications
  - Click-to-stop functionality with window restoration
  - Smooth fade animations and hover effects
- **Modern Dark Theme:** High-contrast UI with accessibility focus
  - Professional color scheme with blue accent highlights
  - Enhanced button styling and visual hierarchy
  - Improved text editor fonts and spacing

### Changed
- **Removed Vocabulary System:** Eliminated Janome dependency and vocabulary dialogs for streamlined workflow
- **Enhanced UI State Management:** Fixed processing status synchronization issues
- **Updated Dependencies:** Added pynput for reliable cross-platform hotkey support
- **Improved Error Handling:** UI state properly resets on transcription/formatting errors

### Fixed
- **Processing Status:** UI now correctly shows "Ready" state after completion
- **Recording Indicator Sync:** Indicator properly hides when processing completes
- **Hotkey Reliability:** Multiple fallback systems ensure shortcuts always work

## [0.1.0] - 2025-07-26
### Added
- Two-stage transcription pipeline:
  - **Stage 1:** OpenAI ASR integration (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`) for audio transcription.
  - **Stage 2:** OpenAI Chat Completion integration (`gpt-4o-mini` or other GPT models) for formatting and refining transcriptions.
- Real-time audio recording via microphone with Start/Stop controls.
- **UI Enhancements:** 
  - New tabs to display **Raw** vs **Formatted** transcription results side by side.
  - Model selection combo boxes for both ASR and formatting stages.
  - Toggle switch to enable/disable post-formatting (Stage 2).
  - Multi-line prompt editor for customizing formatting instructions.
  - Menu option to load a YAML/JSON style guide, which is applied during formatting.
  - Vocabulary approval dialog powered by Janome to capture new terms; added terms are saved to a custom dictionary.
  - Basic error message dialogs for API errors or missing API key.
- **Persistent Settings:** Application now uses QSettings to save user preferences (last used models, window size, prompt text, etc.) between sessions.
- **Logging:** Implemented logging of operations to `logs/` directory. Each session's key events (transcribed text, formatted text, selected models, errors) are recorded with timestamps.
- **Testing:** Added pytest test suite covering ASR and formatting functions (with monkeypatched OpenAI calls), vocabulary extraction, and config persistence.
- **Dev Tools:** Configured Black and Ruff with pre-commit hooks for code style and quality enforcement. Added PyInstaller build configuration for generating onefile Windows executable.

### Changed
- Project restructured from original (which was macOS-only Swift) to a Python PySide6 application for cross-platform support (targeting Windows).
- Updated README with new usage instructions, setup, and features.
- Bumped minimum Python requirement to 3.12.

### Fixed
- N/A (first release in Python rewrite).
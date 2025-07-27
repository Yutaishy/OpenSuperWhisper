# CHANGELOG

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
- **Color Scheme:** Cyan-to-teal gradient with light cyan accents
- **File Organization:** Structured assets/ and brand/ directories

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
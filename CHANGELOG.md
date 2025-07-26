# CHANGELOG

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
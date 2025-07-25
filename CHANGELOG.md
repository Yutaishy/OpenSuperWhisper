# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-07-25

### Added
- 2-stage architecture (ASR → o4-mini formatting) with OpenAI ASR (`whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`) and PostFormatter (`o4-mini`).
- GUI (PyQt6) with Raw / Formatted tabs, settings dialogs, vocabulary review, style guide loader.
- Core modules: `ASRClient` abstraction, `OpenAIASRClient`, `PostFormatter`, `VocabularyExtractor`, `style_loader`, `logging_helper`.
- Logging to local session directories (raw.txt, formatted.json, prompt.txt, meta.json).
- Configuration defaults and status labels resources.
- Unit tests (pytest) and optional integration test (`RUN_REAL_API_TEST`).
- Development tooling: ruff, black, pre-commit hooks, jsonschema.
- Build scripts and PyInstaller spec for Windows one-file binary.

### Changed
- Project version bumped to 0.2.0 (Semantic Versioning start).

### Removed
- N/A 
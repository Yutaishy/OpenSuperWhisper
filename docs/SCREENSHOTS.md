# OpenSuperWhisper Screenshots Guide

## Required Screenshots for Documentation

### 1. Main Application Window
- **Filename**: `screenshots/main-window.png`
- **Description**: Main GUI with recording button, transcription area, and settings
- **Key Elements**:
  - Recording button (idle state)
  - Transcription text area (empty)
  - Formatted text area (empty)
  - Preset dropdown
  - Status bar

### 2. Recording in Progress
- **Filename**: `screenshots/recording-active.png`
- **Description**: Application during active recording
- **Key Elements**:
  - Recording button (active/red state)
  - Timer showing recording duration
  - Recording indicator overlay
  - Real-time transcription appearing

### 3. Transcription Complete
- **Filename**: `screenshots/transcription-complete.png`
- **Description**: Completed transcription with formatted output
- **Key Elements**:
  - Raw transcription text
  - Formatted text output
  - "Copied to clipboard" notification
  - Status showing API models used

### 4. Settings Dialog
- **Filename**: `screenshots/settings-dialog.png`
- **Description**: API key and model settings
- **Key Elements**:
  - API key input field (masked)
  - ASR model dropdown
  - Chat model dropdown
  - Apply formatting checkbox

### 5. Preset Management
- **Filename**: `screenshots/preset-management.png`
- **Description**: Custom preset creation and management
- **Key Elements**:
  - Preset dropdown with custom presets
  - Add preset button
  - Edit preset dialog
  - Preset prompt text area

### 6. Web API Interface
- **Filename**: `screenshots/web-api-docs.png`
- **Description**: FastAPI documentation interface
- **URL**: `http://localhost:8000/docs`
- **Key Elements**:
  - API endpoints list
  - Interactive API testing interface
  - Request/response examples

### 7. Docker Running
- **Filename**: `screenshots/docker-running.png`
- **Description**: Terminal showing Docker container running
- **Command**: `docker run -p 8000:8000 ghcr.io/yutaishy/opensuperwhisper:latest`
- **Key Elements**:
  - Container startup logs
  - API server listening message
  - Health check confirmation

### 8. Cross-Platform Support
- **Filename**: `screenshots/cross-platform.png`
- **Description**: Application running on different OS
- **Variations**:
  - Windows 11 with dark theme
  - Ubuntu 22.04 with GNOME
  - macOS Sonoma

## Demo GIF Requirements

### 1. Recording Workflow
- **Filename**: `demo/recording-workflow.gif`
- **Duration**: 15-20 seconds
- **Steps**:
  1. Click record button
  2. Speak for 5 seconds
  3. Stop recording
  4. Show transcription appearing
  5. Show formatted text
  6. Show clipboard notification

### 2. Real-time Transcription
- **Filename**: `demo/realtime-transcription.gif`
- **Duration**: 30 seconds
- **Steps**:
  1. Start long recording
  2. Show chunks being processed
  3. Show real-time text appearing
  4. Continue for multiple chunks
  5. Complete transcription

### 3. API Usage
- **Filename**: `demo/api-usage.gif`
- **Duration**: 10 seconds
- **Steps**:
  1. Show curl command
  2. Upload audio file
  3. Receive JSON response
  4. Show formatted output

## Screenshot Specifications

### Technical Requirements
- **Format**: PNG for static images, GIF for animations
- **Resolution**: 1920x1080 or 2560x1440
- **Color Depth**: 24-bit RGB
- **Compression**: Optimized for web (< 500KB per image)

### Visual Guidelines
- Use default OS theme (no custom themes)
- Ensure text is readable (minimum 12pt font)
- Hide personal information (API keys, emails)
- Use sample text that demonstrates features
- Maintain consistent window size across screenshots

## Tools for Screenshot Creation

### Windows
- **Built-in**: Windows + Shift + S (Snipping Tool)
- **Third-party**: ShareX, Greenshot
- **GIF Recording**: ScreenToGif, LICEcap

### macOS
- **Built-in**: Cmd + Shift + 4 (Screenshot)
- **Third-party**: CleanShot X, Shottr
- **GIF Recording**: Gifox, GIPHY Capture

### Linux
- **Built-in**: GNOME Screenshot, Spectacle (KDE)
- **Third-party**: Flameshot, Shutter
- **GIF Recording**: Peek, SimpleScreenRecorder

## Upload Instructions

1. Create `assets/screenshots/` directory
2. Name files according to the guide above
3. Optimize images using:
   ```bash
   # PNG optimization
   optipng -o5 screenshots/*.png
   
   # GIF optimization
   gifsicle -O3 --colors 256 demo/*.gif -o optimized.gif
   ```
4. Update README.md with image links
5. Commit and push to repository

## Sample Markdown for README

```markdown
## Screenshots

### Main Application
![Main Window](assets/screenshots/main-window.png)

### Recording in Action
![Recording Active](assets/screenshots/recording-active.png)

### Transcription Results
![Transcription Complete](assets/screenshots/transcription-complete.png)

## Demo

### Complete Workflow
![Recording Workflow](assets/demo/recording-workflow.gif)

### Real-time Processing
![Real-time Transcription](assets/demo/realtime-transcription.gif)
```

## Alternative: Automated Screenshots (Future)

For future automation, consider:
- Selenium for web UI screenshots
- PyAutoGUI for desktop screenshots
- Playwright for cross-browser testing
- GitHub Actions for CI screenshot generation

---

**Note**: Screenshots are essential for user adoption. They provide visual confirmation of features and build trust in the software quality.
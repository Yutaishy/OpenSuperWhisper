# 🎤 OpenSuperWhisper

<p align="center">
  <img src="assets/windows/osw.ico" alt="OpenSuperWhisper Icon" width="128" height="128">
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://openai.com"><img src="https://img.shields.io/badge/OpenAI-Whisper%20%7C%20GPT-green.svg" alt="OpenAI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/test-build.yml"><img src="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/test-build.yml/badge.svg" alt="Test Build"></a>
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/release.yml"><img src="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/release.yml/badge.svg" alt="Release"></a>
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/releases/latest"><img src="https://img.shields.io/github/v/release/Yutaishy/OpenSuperWhisper?color=green" alt="Latest Release"></a>
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/releases"><img src="https://img.shields.io/github/downloads/Yutaishy/OpenSuperWhisper/total" alt="Downloads"></a>
  <img src="https://img.shields.io/badge/Version-0.6.14-orange.svg" alt="Version">
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/pkgs/container/opensuperwhisper"><img src="https://img.shields.io/badge/Docker-Available-blue.svg" alt="Docker"></a>
</p>

**Two-Stage Voice Transcription Pipeline with AI-Powered Text Formatting**

OpenSuperWhisper is a cross-platform desktop application that transforms speech into polished, professional text through a sophisticated two-stage pipeline: first transcribing audio with OpenAI's Whisper models, then intelligently formatting the results using GPT models with customizable style guides.

<p align="center">
  <img src="assets/social_preview_1280x640.jpg" alt="OpenSuperWhisper Preview" width="640" height="320">
</p>

## ✨ Key Features

### 🎙️ **Smart Audio Recording**
- **Global hotkey support** (`Ctrl+Space` works everywhere, even when minimized)
- **Real-time recording** with visual timer and status indicators  
- **Always-on-top recording indicator** with blinking animation
- **High-quality audio capture** (16kHz, mono, int16 format)
- **Cross-platform compatibility** with sounddevice integration

### 🚀 **Real-time Transcription (v0.6.13+)**
- **Long recording support** - 10+ minutes without interruption
- **Chunk-based processing** - Automatic 60-120 second chunks for optimal performance
- **Live transcription** - See results while still recording
- **Memory efficient** - Process large recordings without memory issues
- **Smart silence detection** - Natural chunk boundaries at pauses

### 🧠 **Two-Stage AI Pipeline**
- **Stage 1**: OpenAI Whisper transcription (`whisper-1`, `gpt-4o-transcribe`)
- **Stage 2**: GPT-powered text formatting (`gpt-4o-mini`, `gpt-4`, `o1`, `o1-mini`, `o3`, `o4-mini`, `o4-mini-high`)
- **Advanced preset management** - create, edit, and customize formatting prompts
- **Built-in presets** for meetings, technical docs, blog articles, and more
- **YAML/JSON style guides** for consistent formatting rules

### 📋 **Seamless Workflow Integration**
- **Automatic clipboard copy** - results instantly available with `Ctrl+V`
- **Smart result selection** - copies formatted text when available, raw when not
- **Background operation** - record anywhere while working in other apps
- **Visual feedback** - "📋 Copied to clipboard!" notifications

### 💾 **Professional UI & Settings**
- **Modern dark theme** with high contrast and accessibility
- **Dual monitor support** with always-on-top indicators
- **Persistent settings** via QSettings (Windows Registry integration)
- **API key management** through secure UI dialogs
- **Comprehensive logging** for debugging and analysis

### 📦 **Production Ready**
- **All Platforms**: Directory-based distribution with all dependencies for maximum compatibility
- **Cross-OS CI smoke tests** to validate build and executable startup on Windows, macOS, and Linux
- **Professional error handling** and user feedback
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **v0.6.8**: Fixed SSL certificate bundling for API connections

## 🚀 Quick Start

### Option 1: Download Release (Recommended)

**📥 [Download Latest Release](https://github.com/Yutaishy/OpenSuperWhisper/releases/latest)**

Choose your platform:
- **Windows**: `OpenSuperWhisper-Windows.zip`
- **macOS**: `OpenSuperWhisper-macOS.zip`
- **Linux**: `OpenSuperWhisper-Linux.zip`

⚠️ **Important**: Download the platform-specific ZIP files above, NOT the "Source code" archives. The source code archives do not contain the pre-built executables.

**Setup:**
1. Extract the ZIP file to your desired location
2. Run the executable from the extracted folder
   - macOS: First launch via right-click → Open to bypass Gatekeeper
   - macOS: Allow Microphone and Accessibility (for global hotkey)
3. Set your OpenAI API key via **Settings → Set OpenAI API Key...**
4. Click **🎤 Record** and start speaking!

### Option 2: Docker (API Server Mode)

**🐳 Run as Web API Server with Docker:**

```bash
# Quick start
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here ghcr.io/yutaishy/opensuperwhisper:latest

# With custom port and settings
docker run -p 3000:8000 -e OPENAI_API_KEY=sk-... -e PORT=8000 ghcr.io/yutaishy/opensuperwhisper:latest
```

**API Usage:**
- **Health Check**: `GET http://localhost:8000/`
- **Transcribe Audio**: `POST http://localhost:8000/transcribe` (upload audio file)
- **Format Text**: `POST http://localhost:8000/format-text` (JSON payload)
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)

**Example API Call:**
```bash
# Upload and transcribe audio file
curl -X POST "http://localhost:8000/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_audio.wav" \
  -F "asr_model=whisper-1" \
  -F "apply_formatting=true" \
  -F "chat_model=gpt-4o-mini"
```

### Option 3: Run from Source
```bash
# Clone repository
git clone https://github.com/Yutaishy/OpenSuperWhisper.git
cd OpenSuperWhisper

# Install dependencies (runtime)
pip install -r requirements.txt

# OR install as editable package with development tools
pip install -e ".[dev]"

# Run GUI application
python run_app.py

# OR run as Web API server
python web_server.py
```

### Platform Permissions
- Windows: Microphone access on first use. If global hotkey fails, run as administrator once.
- macOS: System Settings → Privacy & Security → Microphone/Accessibility → enable for OpenSuperWhisper.
- Linux: Ensure `portaudio` is available; packaged on most distros. If not, install `portaudio19-dev`.

## 📋 System Requirements

- **Python 3.12+** (for source installation)
- **OpenAI API key** (get one at [platform.openai.com](https://platform.openai.com))
- **Microphone access** for audio recording
- **Windows 10+** / **macOS 10.15+** / **Ubuntu 20.04+**

### Dependencies
- **Core Runtime**: `PySide6`, `openai`, `sounddevice`, `numpy`, `pynput`, `PyYAML`, `cryptography`, `Pillow`
- **Development**: `pytest`, `pytest-cov`, `black`, `ruff`, `mypy`, `types-PyYAML`, `pyinstaller`

## 🎯 Use Cases

### 📝 **Meeting Notes & Minutes**
```
Input: "Um, so today we discussed the, uh, quarterly budget and..."
Output: "Today we discussed the quarterly budget and identified three key priorities for cost optimization."
```

### 💻 **Coding & Development**
```
Input: "I need to create a function that checks if a user is authenticated..."
Output: "Create an authentication validation function that verifies user credentials and returns authorization status."
```

### 🎤 **Content Creation**
```
Input: "Hey guys, welcome back to my channel..."
Output: "Welcome to today's episode where we'll explore innovative approaches to..."
```

### 🚀 **Real-time Workflow Integration**
1. **Press `Ctrl+Space`** anywhere (even in other apps)
2. **Speak your thoughts** while working
3. **Press `Ctrl+Space`** again to stop
4. **Press `Ctrl+V`** to instantly paste polished text

## ⚙️ Configuration

### API Key Setup
1. Open **Settings → Set OpenAI API Key...**
2. Enter your API key (starts with `sk-`)
3. Key is securely stored and automatically loaded

### Advanced Preset Management
OpenSuperWhisper now includes powerful preset management capabilities:

- **➕ Add Preset**: Create new formatting prompts with custom names
- **✏️ Edit Preset**: Rename existing custom presets (default presets protected)
- **💾 Save Preset**: Update prompt content for existing presets
- **🗑️ Delete Preset**: Remove custom presets (with confirmation)

**Built-in Presets Include**:
- **Default Editor**: General text cleanup and formatting
- **Meeting Minutes**: Structured minutes with action items and decisions
- **Technical Documentation**: Technical writing with proper terminology
- **Blog Article**: Engaging content with natural flow

**Creating Custom Presets**:
1. Click the **➕** button next to the preset dropdown
2. Enter a unique preset name
3. Write your custom formatting prompt
4. The preset is automatically saved and available immediately

### Style Guide Integration
Load YAML or JSON style guides for consistent formatting:

```yaml
tone: professional
avoid:
  - filler words
  - repetition
formatting:
  - Use Oxford commas
  - Bold important terms
terminology:
  - customer: client
  - buy: purchase
```

## 🧪 Development & Testing

### Running Tests
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run comprehensive test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=OpenSuperWhisper
```

### Building Executable
```bash
# Install development dependencies
pip install -e ".[dev]"

# Recommended: use the provided build script (onedir for all platforms)
python build_executable.py OpenSuperWhisper

# Or directly with PyInstaller (onedir mode)
pyinstaller --onedir --windowed run_app.py --name OpenSuperWhisper
```

### Code Quality
```bash
# Format code
black OpenSuperWhisper/ tests/

# Lint code
ruff check OpenSuperWhisper/ tests/

# Type checking
mypy OpenSuperWhisper/
```

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Audio Input   │───▶│  OpenAI Whisper  │───▶│   Raw Transcription │
│  (sounddevice)  │    │   (ASR Stage)     │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ Formatted Text  │◀───│  OpenAI GPT      │◀───│   Custom Prompt +   │
│   (Final)       │    │ (Format Stage)   │    │   Style Guide       │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## 🎨 Brand & Design

OpenSuperWhisper features a professional **Wave + Quote** icon design that represents the core functionality of audio-to-text transcription.

### Visual Identity
- **Design Concept**: Audio waves transforming into quotation marks, symbolizing speech-to-text conversion
- **Color Palette**: 
  - Primary gradient: `#0EA5E9` → `#14B8A6` (cyan to teal)
  - Accent: `#E6FBFF` (light cyan)
- **Typography**: Modern, clean sans-serif fonts for accessibility

### Brand Assets
- **Icons**: Complete multi-platform icon pack in [`assets/`](assets/)
  - Windows: [`osw.ico`](assets/windows/osw.ico) (16px to 256px)
  - iOS: [`AppIcon.appiconset`](assets/ios/AppIcon.appiconset/) (all required sizes)
  - Android: [`mipmap-*`](assets/android/) density variations
  - Web: [`favicon.ico`](assets/web/favicon.ico) + PWA icons
- **Master Files**: Source assets in [`brand/icon/wave-quote/`](brand/icon/wave-quote/)
  - [`master_2048.png`](brand/icon/wave-quote/master_2048.png) - High-resolution master
  - [`fg_glyph_1024.png`](brand/icon/wave-quote/fg_glyph_1024.png) - Foreground glyph only
- **Guidelines**: Complete specifications in [`brand/icon/wave-quote/palette.md`](brand/icon/wave-quote/palette.md)

### Usage Guidelines
The OpenSuperWhisper brand assets are provided for use within this project and official distributions. See [`brand/icon/LICENSE-ARTWORK.md`](brand/icon/LICENSE-ARTWORK.md) for detailed usage terms.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [Wiki](../../wiki)
- **Issues**: [Bug Reports & Feature Requests](../../issues)
- **Releases**: [Download Latest](../../releases)
- **OpenAI API**: [Get API Key](https://platform.openai.com)

## 🔒 Security & Antivirus Compatibility

### Windows Security / Microsoft Defender
OpenSuperWhisper v0.6.4+ is specifically designed to minimize false positives from antivirus software. However, if you encounter security warnings:

#### If Windows Defender blocks the application:
1. **Check Protection History**: Windows Security → Virus & threat protection → Protection history
2. **Allow the file**: Find the blocked item and select "Allow on device" or "Restore"
3. **Unblock downloaded file**: Right-click the ZIP file → Properties → Check "Unblock" → OK

#### For other antivirus software:
- Add the extracted application folder to your antivirus exclusion list temporarily
- Check your antivirus quarantine and restore the application if needed

### Installation Instructions
1. **Download** the appropriate ZIP file for your platform from [Releases](../../releases)
2. **Extract** the entire ZIP file to a folder (e.g., `C:\Program Files\OpenSuperWhisper\`)
3. **Run** the executable from the extracted folder
4. **Set up** your OpenAI API key via Settings → Set OpenAI API Key...

### Security Measures
- **No UPX compression**: Eliminates primary cause of false positives
- **Onedir distribution**: Allows better antivirus scanning
- **Open source**: All code is publicly auditable on GitHub
- **SHA-256 hashes**: Provided in each release for integrity verification

### Still having issues?
If you continue to experience security warnings, please [report the issue](../../issues/new) with:
- Your antivirus software name and version
- The exact warning message
- The file's SHA-256 hash

## 💬 Support

Having issues? Check our [troubleshooting guide](../../wiki/Troubleshooting) or [open an issue](../../issues/new).

---

**Made with ❤️ using OpenAI's cutting-edge AI models**

*Transform your voice into perfect text with the power of AI*
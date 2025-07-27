# 🎤 OpenSuperWhisper

<p align="center">
  <img src="assets/windows/osw.ico" alt="OpenSuperWhisper Icon" width="128" height="128">
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://openai.com"><img src="https://img.shields.io/badge/OpenAI-Whisper%20%7C%20GPT-green.svg" alt="OpenAI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/test.yml"><img src="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/test.yml/badge.svg" alt="CI/CD"></a>
  <a href="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/build-release.yml"><img src="https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/build-release.yml/badge.svg" alt="Build"></a>
  <img src="https://img.shields.io/badge/Tests-18%20Passing-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.6.0-orange.svg" alt="Version">
</p>

**Two-Stage Voice Transcription Pipeline with AI-Powered Text Formatting**

OpenSuperWhisper is a cross-platform desktop application that transforms speech into polished, professional text through a sophisticated two-stage pipeline: first transcribing audio with OpenAI's Whisper models, then intelligently formatting the results using GPT models with customizable style guides.

<p align="center">
  <img src="assets/misc/social_preview_1280x640.jpg" alt="OpenSuperWhisper Preview" width="640" height="320">
</p>

## ✨ Key Features

### 🎙️ **Smart Audio Recording**
- **Global hotkey support** (`Ctrl+Space` works everywhere, even when minimized)
- **Real-time recording** with visual timer and status indicators  
- **Always-on-top recording indicator** with blinking animation
- **High-quality audio capture** (16kHz, mono, int16 format)
- **Cross-platform compatibility** with sounddevice integration

### 🧠 **Two-Stage AI Pipeline**
- **Stage 1**: OpenAI Whisper transcription (`whisper-1`, `gpt-4o-transcribe`)
- **Stage 2**: GPT-powered text formatting (`gpt-4o-mini`, `gpt-4`, `o3`, `o4-mini`)
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
- **Single-file Windows executable** via PyInstaller
- **Comprehensive test suite** (18 tests, 100% core coverage)
- **Professional error handling** and user feedback
- **Cross-platform compatibility** (Windows, macOS, Linux)

## 🚀 Quick Start

### Option 1: Download Release (Recommended)
1. Download the latest `OpenSuperWhisper.exe` from [Releases](../../releases)
2. Set your OpenAI API key via **Settings → Set OpenAI API Key...**
3. Click **🎤 Record** and start speaking!

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/Yutaishy/OpenSuperWhisper.git
cd OpenSuperWhisper

# Install dependencies
pip install -r requirements.txt

# Run application
python run_app.py
```

## 📋 System Requirements

- **Python 3.12+** (for source installation)
- **OpenAI API key** (get one at [platform.openai.com](https://platform.openai.com))
- **Microphone access** for audio recording
- **Windows 10+** / **macOS 10.15+** / **Ubuntu 20.04+**

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
pip install -r requirements-dev.txt

# Build single-file executable
pyinstaller --onefile --windowed run_app.py --name OpenSuperWhisper
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

## 💬 Support

Having issues? Check our [troubleshooting guide](../../wiki/Troubleshooting) or [open an issue](../../issues/new).

---

**Made with ❤️ using OpenAI's cutting-edge AI models**

*Transform your voice into perfect text with the power of AI*
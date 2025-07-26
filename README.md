# 🎤 OpenSuperWhisper

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-Whisper%20%7C%20GPT-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-18%20Passing-brightgreen.svg)](#testing)

**Two-Stage Voice Transcription Pipeline with AI-Powered Text Formatting**

OpenSuperWhisper is a cross-platform desktop application that transforms speech into polished, professional text through a sophisticated two-stage pipeline: first transcribing audio with OpenAI's Whisper models, then intelligently formatting the results using GPT models with customizable style guides.

![OpenSuperWhisper Demo](https://img.shields.io/badge/Demo-Available-blue.svg)

## ✨ Key Features

### 🎙️ **Smart Audio Recording**
- **Real-time recording** with visual timer and status indicators
- **Keyboard shortcuts** (`Ctrl+Space` to record, `Ctrl+S` to save)
- **High-quality audio capture** (16kHz, mono, int16 format)
- **Cross-platform compatibility** with sounddevice integration

### 🧠 **Two-Stage AI Pipeline**
- **Stage 1**: OpenAI Whisper transcription (`whisper-1`, `gpt-4o-transcribe`)
- **Stage 2**: GPT-powered text formatting (`gpt-4o-mini`, `gpt-4`)
- **Customizable prompts** for specific use cases (meetings, articles, notes)
- **YAML/JSON style guides** for consistent formatting rules

### 🌐 **Japanese Language Support**
- **Morphological analysis** with Janome for vocabulary extraction
- **Custom dictionary building** with user approval workflow
- **Automatic terminology management** for technical terms

### 💾 **Professional UI & Settings**
- **Modern PySide6 interface** with tabbed results view
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
git clone https://github.com/Yutaishy/voice_input.git
cd voice_input

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py
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

### 📚 **Academic Writing**
```
Input: "The research shows that machine learning algorithms can..."
Output: "The research demonstrates that machine learning algorithms possess the capability to..."
```

### 🎤 **Content Creation**
```
Input: "Hey guys, welcome back to my channel..."
Output: "Welcome to today's episode where we'll explore innovative approaches to..."
```

## ⚙️ Configuration

### API Key Setup
1. Open **Settings → Set OpenAI API Key...**
2. Enter your API key (starts with `sk-`)
3. Key is securely stored and automatically loaded

### Custom Formatting Prompts
Edit the **Formatting Prompt** text area for specific use cases:

**For Technical Documentation**:
```
Transform this transcript into clear technical documentation with proper terminology, numbered steps, and code formatting where appropriate.
```

**For Meeting Minutes**:
```
Convert this meeting discussion into structured minutes with action items, decisions, and participant names clearly identified.
```

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
pip install pytest black ruff

# Run comprehensive test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=OpenSuperWhisper
```

### Building Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --windowed run.py --name OpenSuperWhisper
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
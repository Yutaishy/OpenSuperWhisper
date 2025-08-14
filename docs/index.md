---
layout: default
title: OpenSuperWhisper Documentation
---

# OpenSuperWhisper Documentation

## Two-Stage Voice Transcription Pipeline with AI-Powered Text Formatting

OpenSuperWhisper transforms speech into polished, professional text through a sophisticated two-stage pipeline: first transcribing audio with OpenAI's Whisper models, then intelligently formatting the results using GPT models with customizable style guides.

[![Latest Release](https://img.shields.io/github/v/release/Yutaishy/OpenSuperWhisper?color=green)](https://github.com/Yutaishy/OpenSuperWhisper/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Yutaishy/OpenSuperWhisper/total)](https://github.com/Yutaishy/OpenSuperWhisper/releases)
[![CI/CD](https://github.com/Yutaishy/OpenSuperWhisper/actions/workflows/ci.yml/badge.svg)](https://github.com/Yutaishy/OpenSuperWhisper/actions)

## Quick Start

### Download Latest Release

| Platform | Download | Size |
|----------|----------|------|
| Windows (64-bit) | [Download](https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-windows-amd64.zip) | 72 MB |
| Linux (64-bit) | [Download](https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-linux-amd64.tar.gz) | 95 MB |
| Linux (ARM64) | [Download](https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-linux-arm64.tar.gz) | 95 MB |
| macOS | [Source](https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-darwin-amd64-source.tar.gz) | 64 KB |
| Docker | `docker pull ghcr.io/yutaishy/opensuperwhisper:latest` | - |

### Installation

1. Download the appropriate package for your platform
2. Extract the archive to your desired location
3. Run the executable
4. Set your OpenAI API key via Settings

For detailed instructions, see the [Installation Guide](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/INSTALLATION.md).

## Key Features

### Real-time Transcription
- **Long recording support** - 10+ minutes without interruption
- **Chunk-based processing** - Automatic 60-120 second chunks
- **Live transcription** - See results while recording
- **Memory efficient** - Process large recordings smoothly

### Two-Stage AI Pipeline
- **Stage 1**: OpenAI Whisper transcription
- **Stage 2**: GPT-powered text formatting
- **Custom presets** for different use cases
- **Style guides** for consistent formatting

### Seamless Integration
- **Global hotkey** (`Ctrl+Space`) works everywhere
- **Automatic clipboard** copy
- **Background operation**
- **Visual feedback** and notifications

## Documentation

### User Guides
- [Installation Guide](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/INSTALLATION.md)
- [API Documentation](API.md)
- [Screenshots Guide](SCREENSHOTS.md)

### Developer Resources
- [Contributing Guide](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/CONTRIBUTING.md)
- [CI/CD Guide](CI_CD_GUIDE.md)
- [Testing Guide](TESTING_BEST_PRACTICES.md)

### Technical Documentation
- [Real-time Transcription](REALTIME_TRANSCRIPTION_IMPLEMENTATION_LOG.md)
- [Release Process](RELEASE_CHECKLIST.md)
- [Architecture Overview](#architecture)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Audio Input   │───▶│  OpenAI Whisper  │───▶│   Raw Transcription │
│  (sounddevice)  │    │   (ASR Stage)    │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ Formatted Text  │◀───│  OpenAI GPT      │◀───│   Custom Prompt +   │
│   (Final)       │    │ (Format Stage)   │    │   Style Guide       │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## API Usage

### Basic Transcription

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.wav" \
  -F "apply_formatting=true"
```

### Text Formatting

```bash
curl -X POST "http://localhost:8000/format-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "your text here", "chat_model": "gpt-4o-mini"}'
```

For complete API documentation, see the [API Reference](API.md).

## Use Cases

### Meeting Notes
Transform rambling discussions into structured minutes with action items and decisions clearly identified.

### Technical Documentation
Convert spoken technical explanations into properly formatted documentation with correct terminology.

### Content Creation
Turn casual speech into polished blog posts, articles, or social media content.

### Coding & Development
Dictate code ideas and have them formatted with proper syntax and structure.

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **RAM**: 4GB
- **CPU**: Dual-core 2GHz
- **Network**: 1Mbps for API calls
- **Storage**: 100MB

### Recommended
- **RAM**: 8GB for optimal performance
- **CPU**: Quad-core for faster processing
- **SSD** for better application responsiveness

## Performance

Based on our benchmarks:
- **Audio Processing**: < 2ms for 60s audio
- **Chunk Processing**: ~2ms per chunk
- **JSON Operations**: < 0.2ms round-trip
- **Memory Usage**: ~2MB per minute of audio

See [Benchmark Results](https://github.com/Yutaishy/OpenSuperWhisper#performance) for details.

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/Yutaishy/OpenSuperWhisper.git
cd OpenSuperWhisper

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Support

- **Issues**: [GitHub Issues](https://github.com/Yutaishy/OpenSuperWhisper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Yutaishy/OpenSuperWhisper/discussions)
- **Wiki**: [Project Wiki](https://github.com/Yutaishy/OpenSuperWhisper/wiki)

## License

OpenSuperWhisper is released under the MIT License. See [LICENSE](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/LICENSE) for details.

## Acknowledgments

Built with:
- [OpenAI Whisper](https://openai.com/research/whisper) for speech recognition
- [OpenAI GPT](https://openai.com/gpt) for text formatting
- [PySide6](https://www.qt.io/qt-for-python) for the GUI
- [FastAPI](https://fastapi.tiangolo.com/) for the API server

---

**Transform your voice into perfect text with the power of AI** 🎤✨

*Last updated: August 2024*
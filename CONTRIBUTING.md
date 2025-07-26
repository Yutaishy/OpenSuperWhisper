# Contributing to OpenSuperWhisper

Thank you for your interest in contributing to OpenSuperWhisper! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/voice_input.git
   cd voice_input
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development tools
   pip install pytest black ruff mypy pre-commit
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🧪 Development Workflow

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=OpenSuperWhisper --cov-report=html

# Run specific test file
pytest tests/test_asr_api.py -v
```

### Code Quality
```bash
# Format code
black OpenSuperWhisper/ tests/

# Lint code
ruff check OpenSuperWhisper/ tests/

# Type checking
mypy OpenSuperWhisper/

# Run all quality checks
pre-commit run --all-files
```

### Testing Your Changes
```bash
# Test the application
python run.py

# Build and test executable
pyinstaller --onefile --windowed run.py --name OpenSuperWhisper
./dist/OpenSuperWhisper.exe
```

## 📝 Contribution Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Use Ruff for linting
- Add type hints where appropriate
- Write docstrings for public functions and classes

### Commit Messages
Use conventional commit format:
```
feat: add new feature
fix: resolve bug in transcription
docs: update README
test: add test for formatter
refactor: improve API structure
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   pytest tests/
   pre-commit run --all-files
   ```

4. **Submit pull request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all tests pass
   - Request review from maintainers

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, dependencies
- **Steps to reproduce**: Clear, step-by-step instructions
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs**: Relevant error messages or log files
- **Screenshots**: If applicable

Use the bug report template:
```markdown
## Bug Description
Brief description of the issue

## Environment
- OS: Windows 11 / macOS 13 / Ubuntu 22.04
- Python: 3.12.x
- OpenSuperWhisper: v1.0.0

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Logs/Screenshots
Paste relevant logs or add screenshots
```

## 💡 Feature Requests

For new features, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and problem being solved
3. **Propose a solution** with implementation details
4. **Consider alternatives** and trade-offs

Feature request template:
```markdown
## Feature Description
Brief description of the proposed feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other approaches were considered?

## Additional Context
Any other relevant information
```

## 🧩 Areas for Contribution

### High Priority
- **Performance optimization** for large audio files
- **Additional language support** beyond Japanese
- **Real-time transcription** streaming
- **Voice activity detection** for automatic recording
- **Cloud storage integration** for transcriptions

### Medium Priority
- **Plugin system** for custom formatters
- **Batch processing** for multiple files
- **Advanced audio preprocessing** (noise reduction, etc.)
- **Export formats** (PDF, DOCX, etc.)
- **Keyboard customization** for shortcuts

### Documentation
- **Video tutorials** for common use cases
- **API documentation** for developers
- **Troubleshooting guides** for common issues
- **Translation** of documentation

## 🔧 Architecture Overview

### Core Components
- **`asr_api.py`**: OpenAI Whisper integration
- **`formatter_api.py`**: GPT-based text formatting
- **`ui_mainwindow.py`**: PySide6 GUI components
- **`config.py`**: Settings management
- **`vocabulary.py`**: Japanese word extraction
- **`prompt_manager.py`**: Style guide handling

### Key Design Principles
- **Modularity**: Each component has a single responsibility
- **Testability**: All core logic is unit tested
- **Configuration**: User preferences persist across sessions
- **Error handling**: Graceful degradation with user feedback
- **Logging**: Comprehensive logging for debugging

## 📚 Resources

### External Documentation
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [pytest Documentation](https://docs.pytest.org/)
- [Janome Documentation](https://mocobeta.github.io/janome/)

### Project Structure
```
OpenSuperWhisper/
├── OpenSuperWhisper/     # Main package
│   ├── asr_api.py       # Audio transcription
│   ├── formatter_api.py # Text formatting
│   ├── ui_mainwindow.py # GUI interface
│   ├── config.py        # Settings management
│   ├── vocabulary.py    # Word extraction
│   └── prompt_manager.py # Style guides
├── tests/               # Test suite
├── style_guides/        # Example style guides
├── requirements.txt     # Dependencies
└── run.py              # Entry point
```

## 🤝 Community

### Communication
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Request Reviews**: Code feedback and collaboration

### Code of Conduct
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the project's goals

## 📄 License

By contributing to OpenSuperWhisper, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to OpenSuperWhisper!** 🎉

Your contributions help make voice transcription more accessible and powerful for everyone.
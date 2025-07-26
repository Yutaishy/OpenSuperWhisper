# OpenSuperWhisper (Two-Stage Voice Transcription Tool)

OpenSuperWhisper is a cross-platform voice transcription application that uses OpenAI's state-of-the-art models to transcribe audio and then polish the transcription according to your desired style. It offers real-time recording, advanced formatting with a style guide, vocabulary assistance, and more.

## Features

- 🎙 **Real-time Audio Recording and Transcription:** Press the record button (or use the shortcut `Ctrl+Space`) to start recording from your microphone, then press stop to transcribe instantly using OpenAI Whisper or GPT-4o models.
- 📝 **Two-Stage Transcription Pipeline:** First, get raw text via OpenAI ASR (Whisper API or GPT-4o Transcribe). Second, automatically format and correct that text using a GPT-based model (Chat Completion) with your custom prompt and style rules.
- 💡 **Custom Formatting Prompt & Style Guide:** Tailor the output by editing the formatting prompt in the UI. Load a YAML or JSON style guide file to enforce specific writing style, terminology, or formatting conventions in the final text.
- 📖 **Vocabulary Extraction & Dictionary:** After transcription, the app highlights new or uncommon words (especially Japanese nouns using Janome). You can choose to add these to your custom vocabulary. The app remembers these, helping maintain consistency.
- 💾 **Persistent Settings:** Your preferences (selected models, toggle states, prompt text, window size, etc.) are saved automatically. Next time you open the app, it recalls your last-used settings.
- 📂 **Logging:** All transcriptions and formatting results are logged (with timestamps and model info) in the `logs/` directory. This helps review past sessions or debug issues.
- 🧪 **Fully Tested Codebase:** The project includes unit and integration tests (using pytest) to ensure reliability of the transcription and formatting pipeline.
- 🖥 **One-File Executable for Windows:** Easily run OpenSuperWhisper on Windows without setting up a Python environment – just use the provided single EXE (built with PyInstaller).

## Installation

**Prerequisites:**
- Python 3.12 (if running from source). On Windows, ensure Python and pip/uv are in your PATH.
- An OpenAI API key for using the transcription and formatting services. Set it as an environment variable `OPENAI_API_KEY` before running the app.
- (Windows) Microphone access for recording.

**Using uv (Fast Python Package Manager):**
1. Clone this repository or download the source code.
2. In a terminal, navigate to the project directory (`voice_input_v2/`).
3. Install dependencies with [uv](https://github.com/astral-sh/uv):
   ```bash
   uv pip install -r requirements.txt
   ```
   This will install PySide6 (Qt for GUI), openai, janome, sounddevice, and other requirements.  
4. (Optional) Install dev tools for testing and formatting:
   ```bash
   uv pip install black ruff pytest pre-commit
   ```

**Running from Source:**
```bash
python -m OpenSuperWhisper.main
```
The application window should appear. If your OpenAI API key is set, you're ready to transcribe.

**Using the Windows EXE:**
Download the latest release and double-click to run. No installation needed.

Make sure to set your OPENAI_API_KEY in the environment. You can do this by creating a simple batch file like:
```batch
@echo off
set OPENAI_API_KEY=sk-...YourKeyHere...
start OpenSuperWhisper.exe
```

## Usage Guide

1. **Recording Audio:** Press the Record button (🎤) or use `Ctrl+Space` to start recording your voice. You'll see a timer showing recording duration. Speak clearly into your microphone. Press Stop to finish. The audio will be sent to OpenAI and transcribed in a few seconds. The raw text appears in the "Raw Transcription" tab.

2. **Review Raw Transcription:** Check if the raw text captured your speech correctly. You can copy this text or even edit it in place if you spot obvious errors.

3. **Vocabulary Check (Japanese):** If you transcribed Japanese and the system finds new words, a "New Vocabulary" dialog will pop up listing terms it thinks are important or uncommon. Review the list, uncheck any words you don't want to save, and click OK to add the checked words to your custom vocabulary list.

4. **Formatting & Styling:** By default, the app will automatically proceed to Stage 2 formatting after transcription. The text, along with your custom prompt and style guide, is sent to the OpenAI chat model for polishing. The Formatted Text tab will then display the result.

5. **Custom Prompt:** You can customize the instructions for formatting in the "Formatting Prompt" text box. Edit this text to guide how the second-stage model should output text.

6. **Style Guide:** If you have a style guide, click Load Style Guide and select your YAML or JSON file. Once loaded, the content of the style guide will be used by the formatting model.

7. **Model Selection:** At the top, you can choose which models to use for transcription and formatting.

8. **Viewing and Copying Results:** You can switch between the Raw and Formatted tabs to compare the outputs. Once you're satisfied, you can select the text and copy it, or use the Save button (💾) or `Ctrl+S` to save the transcription to a text file.

## Configuration & Preferences

All your settings are saved automatically via QSettings (on Windows, in the registry). This includes window size, last used models, prompt text, style guide path, etc. No need to manually edit config files. If you ever want to reset everything, you can use the "Settings → Reset to Defaults" menu option.

The custom vocabulary you build is stored in a text file `user_dict.txt` in the application directory. You can edit this file manually to remove entries or add new ones.

## Testing

If you are running from source and want to ensure everything works, we have a comprehensive test suite. After installing dev requirements, simply run:

```bash
pytest
```

All unit tests and integration tests should pass.

## Building the Executable (for developers)

To build the executable yourself:

1. Install PyInstaller: `uv pip install pyinstaller`
2. Run PyInstaller:
   ```bash
   pyinstaller --onefile --windowed --name OpenSuperWhisper OpenSuperWhisper/main.py
   ```
3. The output will be in the `dist` directory.

## License

This project is licensed under the MIT License.
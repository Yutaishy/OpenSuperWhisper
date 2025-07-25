#!/usr/bin/env pwsh
# Build Open Super Whisper into a single EXE
pyinstaller --clean --noconfirm --onefile --windowed --name open-super-whisper --add-data "assets/prompts;assets/prompts" --add-data "project_styles;project_styles" src/__main__.py 
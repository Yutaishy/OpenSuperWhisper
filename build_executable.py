#!/usr/bin/env python3
"""
Build script for creating executable with PyInstaller
"""
import sys
import os
import PyInstaller.__main__

def main():
    executable_name = sys.argv[1] if len(sys.argv) > 1 else "OpenSuperWhisper"
    
    args = [
        f'--name={executable_name}',
        '--onefile',
        '--windowed',
        '--collect-all=OpenSuperWhisper',
        '--collect-all=PySide6',
        '--hidden-import=OpenSuperWhisper',
        '--hidden-import=OpenSuperWhisper.ui_mainwindow',
        '--hidden-import=OpenSuperWhisper.asr_api',
        '--hidden-import=OpenSuperWhisper.formatter_api',
        '--hidden-import=OpenSuperWhisper.config',
        '--hidden-import=OpenSuperWhisper.logger',
        '--hidden-import=OpenSuperWhisper.global_hotkey',
        '--hidden-import=OpenSuperWhisper.direct_hotkey',
        '--hidden-import=OpenSuperWhisper.simple_hotkey',
        '--hidden-import=OpenSuperWhisper.recording_indicator',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--distpath=dist',
        'run_app.py'
    ]
    
    print(f"Building executable: {executable_name}")
    print(f"PyInstaller args: {' '.join(args)}")
    
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Build script for creating executable with PyInstaller
"""
import sys
import os
import platform
import PyInstaller.__main__

def main():
    executable_name = sys.argv[1] if len(sys.argv) > 1 else "OpenSuperWhisper"
    
    # Base arguments - Security-focused configuration
    args = [
        f'--name={executable_name}',
        '--onedir',  # Changed from onefile to reduce false positives
        '--windowed',
        '--noupx',  # Disable UPX compression globally to prevent false positives
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
        '--hidden-import=OpenSuperWhisper.first_run',
        '--hidden-import=OpenSuperWhisper.security',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=cryptography',
        '--hidden-import=cryptography.fernet',
        '--hidden-import=yaml',
        '--hidden-import=tempfile',
        '--distpath=dist',
        '--clean',  # Clean build directory
        'run_app.py'
    ]
    
    # Add CI-specific optimizations and security enhancements
    if os.getenv('CI'):
        print("CI environment detected - adding CI-specific optimizations")
        args.extend([
            '--log-level=WARN',  # Reduce verbosity for CI
            '--noconfirm',  # Don't ask for confirmation
        ])
    
    # Security and compatibility improvements (all environments)
    args.extend([
        '--exclude-module=tkinter',  # Exclude unnecessary modules that may trigger AV
        '--exclude-module=matplotlib',
        '--exclude-module=test',
        '--exclude-module=unittest',
        '--exclude-module=IPython',
        '--exclude-module=jupyter',
        '--exclude-module=notebook',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        '--exclude-module=sklearn',
        '--strip',  # Strip debug information to reduce false positives
    ])
    
    # Platform-specific adjustments
    if platform.system() == 'Linux':
        print("Linux platform detected - adding Linux-specific settings")
        args.extend([
            '--icon=assets/ios/AppIcon.appiconset/Icon-AppStore-1024.png',
            '--hidden-import=PySide6.QtDBus',
            # Try to find libportaudio.so.2 in common locations
            '--collect-all=sounddevice',
        ])
        # Try to add portaudio library if it exists
        portaudio_paths = [
            '/usr/lib/x86_64-linux-gnu/libportaudio.so.2',
            '/usr/lib/libportaudio.so.2',
            '/lib/x86_64-linux-gnu/libportaudio.so.2'
        ]
        for path in portaudio_paths:
            if os.path.exists(path):
                args.append(f'--add-binary={path}:.')
                break
    
    elif platform.system() == 'Darwin':  # macOS
        print("macOS platform detected - adding macOS-specific settings")
        # Use PNG icon for macOS (PyInstaller can convert with Pillow)
        args.extend([
            '--icon=assets/ios/AppIcon.appiconset/Icon-AppStore-1024.png',
            '--osx-bundle-identifier=com.yutaishy.opensuperwhisper',
            '--collect-all=sounddevice',
        ])
    
    elif platform.system() == 'Windows':
        print("Windows platform detected - adding Windows-specific settings")
        args.extend([
            '--icon=assets/windows/osw.ico',
            '--collect-all=sounddevice',
        ])
        # Add win32 imports if available
        try:
            import win32api
            args.extend([
                '--hidden-import=win32api',
                '--hidden-import=win32con', 
                '--hidden-import=win32gui',
            ])
            print("Added win32 imports")
        except ImportError:
            print("win32 modules not available, skipping")
    
    print(f"Building executable: {executable_name}")
    print(f"Platform: {platform.system()}")
    print(f"PyInstaller args: {' '.join(args)}")
    
    try:
        PyInstaller.__main__.run(args)
        print(f"Successfully built executable: {executable_name}")
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
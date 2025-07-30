#!/usr/bin/env python3
"""
Build script for creating executable with PyInstaller
"""
import os
import platform
import sys

import PyInstaller.__main__


def main():
    executable_name = sys.argv[1] if len(sys.argv) > 1 else "OpenSuperWhisper"

    # Base arguments - Security-focused configuration
    args = [
        f'--name={executable_name}',
        '--onedir',  # Use onedir for all platforms to prevent DLL access violations
        '--windowed',
        '--noupx',  # Disable UPX compression globally to prevent false positives
        '--collect-all=OpenSuperWhisper',
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
        '--hidden-import=certifi',
        '--hidden-import=ssl',
        '--hidden-import=urllib3',
        '--hidden-import=requests',
        '--collect-all=certifi',
        '--collect-all=openai',
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
    ])

    # Only strip on non-Windows platforms (may cause DLL issues on Windows)
    if platform.system() != 'Windows':
        args.append('--strip')

    # Platform-specific adjustments
    if platform.system() == 'Linux':
        print("Linux platform detected - adding Linux-specific settings")
        args.extend([
            '--icon=assets/ios/AppIcon.appiconset/Icon-AppStore-1024.png',
            '--hidden-import=PySide6.QtDBus',
            # Try to find libportaudio.so.2 in common locations
            '--collect-all=sounddevice',
            '--collect-all=PySide6',  # Linux can handle collect-all
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
        # Check if icon file exists before adding it
        icon_path = 'assets/ios/AppIcon.appiconset/Icon-AppStore-1024.png'
        if os.path.exists(icon_path):
            args.extend([
                f'--icon={icon_path}',
                '--osx-bundle-identifier=com.yutaishy.opensuperwhisper',
                '--collect-all=sounddevice',
                # Exclude problematic Qt3D modules that cause framework conflicts on macOS
                '--exclude-module=PySide6.Qt3DAnimation',
                '--exclude-module=PySide6.Qt3DCore',
                '--exclude-module=PySide6.Qt3DExtras',
                '--exclude-module=PySide6.Qt3DInput',
                '--exclude-module=PySide6.Qt3DLogic',
                '--exclude-module=PySide6.Qt3DRender',
                '--exclude-module=PySide6.QtCharts',
                '--exclude-module=PySide6.QtDataVisualization',
                '--exclude-module=PySide6.QtLocation',
                '--exclude-module=PySide6.QtMultimedia',
                '--exclude-module=PySide6.QtMultimediaWidgets',
                '--exclude-module=PySide6.QtNetworkAuth',
                '--exclude-module=PySide6.QtPdf',
                '--exclude-module=PySide6.QtPdfWidgets',
                '--exclude-module=PySide6.QtPositioning',
                '--exclude-module=PySide6.QtQuick',
                '--exclude-module=PySide6.QtQuick3D',
                '--exclude-module=PySide6.QtQuickControls2',
                '--exclude-module=PySide6.QtQuickWidgets',
                '--exclude-module=PySide6.QtRemoteObjects',
                '--exclude-module=PySide6.QtScxml',
                '--exclude-module=PySide6.QtSensors',
                '--exclude-module=PySide6.QtSpatialAudio',
                '--exclude-module=PySide6.QtSql',
                '--exclude-module=PySide6.QtStateMachine',
                '--exclude-module=PySide6.QtSvg',
                '--exclude-module=PySide6.QtSvgWidgets',
                '--exclude-module=PySide6.QtTest',
                '--exclude-module=PySide6.QtTextToSpeech',
                '--exclude-module=PySide6.QtUiTools',
                '--exclude-module=PySide6.QtWebChannel',
                '--exclude-module=PySide6.QtWebEngine',
                '--exclude-module=PySide6.QtWebEngineCore',
                '--exclude-module=PySide6.QtWebEngineWidgets',
                '--exclude-module=PySide6.QtWebSockets',
                # Only include essential PySide6 modules needed for the app
                '--hidden-import=PySide6.QtCore',
                '--hidden-import=PySide6.QtGui',
                '--hidden-import=PySide6.QtWidgets',
                '--hidden-import=PySide6.QtNetwork',
            ])
        else:
            print(f"Warning: Icon file not found at {icon_path}, building without icon")
            args.extend([
                '--osx-bundle-identifier=com.yutaishy.opensuperwhisper',
                '--collect-all=sounddevice',
                # Exclude problematic Qt3D modules that cause framework conflicts on macOS
                '--exclude-module=PySide6.Qt3DAnimation',
                '--exclude-module=PySide6.Qt3DCore',
                '--exclude-module=PySide6.Qt3DExtras',
                '--exclude-module=PySide6.Qt3DInput',
                '--exclude-module=PySide6.Qt3DLogic',
                '--exclude-module=PySide6.Qt3DRender',
                '--exclude-module=PySide6.QtCharts',
                '--exclude-module=PySide6.QtDataVisualization',
                '--exclude-module=PySide6.QtLocation',
                '--exclude-module=PySide6.QtMultimedia',
                '--exclude-module=PySide6.QtMultimediaWidgets',
                '--exclude-module=PySide6.QtNetworkAuth',
                '--exclude-module=PySide6.QtPdf',
                '--exclude-module=PySide6.QtPdfWidgets',
                '--exclude-module=PySide6.QtPositioning',
                '--exclude-module=PySide6.QtQuick',
                '--exclude-module=PySide6.QtQuick3D',
                '--exclude-module=PySide6.QtQuickControls2',
                '--exclude-module=PySide6.QtQuickWidgets',
                '--exclude-module=PySide6.QtRemoteObjects',
                '--exclude-module=PySide6.QtScxml',
                '--exclude-module=PySide6.QtSensors',
                '--exclude-module=PySide6.QtSpatialAudio',
                '--exclude-module=PySide6.QtSql',
                '--exclude-module=PySide6.QtStateMachine',
                '--exclude-module=PySide6.QtSvg',
                '--exclude-module=PySide6.QtSvgWidgets',
                '--exclude-module=PySide6.QtTest',
                '--exclude-module=PySide6.QtTextToSpeech',
                '--exclude-module=PySide6.QtUiTools',
                '--exclude-module=PySide6.QtWebChannel',
                '--exclude-module=PySide6.QtWebEngine',
                '--exclude-module=PySide6.QtWebEngineCore',
                '--exclude-module=PySide6.QtWebEngineWidgets',
                '--exclude-module=PySide6.QtWebSockets',
                # Only include essential PySide6 modules needed for the app
                '--hidden-import=PySide6.QtCore',
                '--hidden-import=PySide6.QtGui',
                '--hidden-import=PySide6.QtWidgets',
                '--hidden-import=PySide6.QtNetwork',
            ])

    elif platform.system() == 'Windows':
        print("Windows platform detected - adding Windows-specific settings (onedir mode)")
        args.extend([
            '--icon=assets/windows/osw.ico',
            '--collect-all=sounddevice',
            '--collect-all=PySide6',  # Windows can handle collect-all
            '--add-data=assets;assets',  # Include assets for Windows
        ])
        # Add win32 imports if available
        try:
            import importlib.util
            if importlib.util.find_spec('win32api'):
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

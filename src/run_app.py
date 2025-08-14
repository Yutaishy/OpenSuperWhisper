#!/usr/bin/env python3
"""
Safe version of OpenSuperWhisper with proper error handling
"""
import os
import signal
import sys

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Handle --version flag for CI/CD testing (source of truth from package)
if len(sys.argv) > 1 and sys.argv[1] == '--version':
    try:
        from OpenSuperWhisper import __version__ as OSW_VERSION
        print(f"OpenSuperWhisper v{OSW_VERSION}")
    except Exception:
        # Fallbacks in order: installed package metadata -> pyproject.toml -> unknown
        try:
            from importlib.metadata import version as pkg_version  # type: ignore

            print(f"OpenSuperWhisper v{pkg_version('opensuperwhisper')}")
        except Exception:
            try:
                import tomllib  # Python 3.11+
                from pathlib import Path

                pyproject_text = Path('pyproject.toml').read_text(encoding='utf-8')
                data = tomllib.loads(pyproject_text)
                v = data.get('project', {}).get('version', 'unknown')
                print(f"OpenSuperWhisper v{v}")
            except Exception:
                print("OpenSuperWhisper vunknown")
    sys.exit(0)

def signal_handler(sig, frame):
    print("\nApplication interrupted, exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main() -> None:
    try:
        from PySide6.QtWidgets import QApplication

        from OpenSuperWhisper.ui_mainwindow import MainWindow

        print("Starting OpenSuperWhisper...")

        # Create application
        app = QApplication(sys.argv)

        # Create main window
        window = MainWindow()
        window.show()

        print("Application started successfully!")
        print(f"Window title: {window.windowTitle()}")
        print(f"Realtime mode: {window.realtime_mode}")
        print("Press Ctrl+C to exit")

        # Run event loop
        sys.exit(app.exec())

    except KeyboardInterrupt:
        print("\nApplication closed by user")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Application ended")


if __name__ == "__main__":
    main()


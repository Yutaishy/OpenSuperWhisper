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
        # Fallback to pyproject version if import fails
        print("OpenSuperWhisper v0.6.14")
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


#!/usr/bin/env python3
"""
OpenSuperWhisper Application Launcher
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add OpenSuperWhisper directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OpenSuperWhisper'))

from PySide6.QtWidgets import QApplication

from OpenSuperWhisper.ui_mainwindow import MainWindow


def main():
    # Check for version argument
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print("OpenSuperWhisper v0.6.11")
        sys.exit(0)

    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

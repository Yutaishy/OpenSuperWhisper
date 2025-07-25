"""Package entry point for Open Super Whisper.

This module launches the PyQt GUI when executed as a module or packaged.
"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> None:  # noqa: D401
    """Launch the GUI application."""
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
"""Dialog to select style guide YAML / JSON file."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)


class StyleGuideDialog(QDialog):
    """スタイルガイドファイルを選択し、設定へ保存するダイアログ。"""

    def __init__(self, settings: QSettings, parent: Optional[QWidget] = None) -> None:  # noqa: D401
        super().__init__(parent)
        self.setWindowTitle("Load Style Guide")
        self._settings = settings

        layout = QFormLayout(self)

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setText(self._settings.value("style_guide/path", ""))
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_file)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        layout.addRow("Style Guide File", path_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _browse_file(self) -> None:  # noqa: D401
        path, _ = QFileDialog.getOpenFileName(self, "Select Style Guide", "", "YAML/JSON (*.yml *.yaml *.json)")
        if path:
            self.path_edit.setText(path)

    def _on_accept(self) -> None:  # noqa: D401
        self._settings.setValue("style_guide/path", self.path_edit.text())
        self.accept() 
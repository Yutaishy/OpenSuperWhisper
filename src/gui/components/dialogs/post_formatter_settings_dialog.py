"""Dialog for configuring PostFormatter parameters."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QWidget,
)


class PostFormatterSettingsDialog(QDialog):
    """設定ダイアログ: PostFormatter の各種パラメータを編集する。"""

    def __init__(self, settings: QSettings, parent: Optional[QWidget] = None) -> None:  # noqa: D401
        super().__init__(parent)
        self.setWindowTitle("Post Formatter Settings (o4-mini)")
        self._settings = settings

        layout = QFormLayout(self)

        # Enable/disable
        self.enabled_checkbox = QCheckBox("Enable Post Formatting")
        self.enabled_checkbox.setChecked(self._settings.value("post_formatter/enabled", True, bool))
        layout.addRow(self.enabled_checkbox)

        # Temperature
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(float(self._settings.value("post_formatter/temperature", 0.0)))
        layout.addRow("Temperature", self.temp_spin)

        # Max tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(0, 4096)
        self.max_tokens_spin.setValue(int(self._settings.value("post_formatter/max_tokens", 0)))
        layout.addRow("Max Tokens (0 = auto)", self.max_tokens_spin)

        # Allow markdown
        self.markdown_checkbox = QCheckBox("Allow Markdown")
        self.markdown_checkbox.setChecked(
            self._settings.value("post_formatter/allow_markdown", False, bool)
        )
        layout.addRow(self.markdown_checkbox)

        # Force style
        self.style_combo = QComboBox()
        self.style_combo.addItem("Auto", "")
        self.style_combo.addItem("です・ます (desu)", "desu")
        self.style_combo.addItem("だ・である (da)", "da")
        current_style = self._settings.value("post_formatter/force_style", "")
        index = self.style_combo.findData(current_style)
        self.style_combo.setCurrentIndex(max(index, 0))
        layout.addRow("Force Style", self.style_combo)

        # System prompt file path
        prompt_layout = QHBoxLayout()
        self.prompt_edit = QLineEdit()
        self.prompt_edit.setText(self._settings.value("post_formatter/system_prompt", ""))
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_prompt_file)
        prompt_layout.addWidget(self.prompt_edit)
        prompt_layout.addWidget(browse_btn)
        layout.addRow("System Prompt File", prompt_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _browse_prompt_file(self) -> None:  # noqa: D401
        path, _ = QFileDialog.getOpenFileName(self, "Select Prompt File", "", "Text (*.txt)")
        if path:
            self.prompt_edit.setText(path)

    def _on_accept(self) -> None:  # noqa: D401
        self._settings.setValue("post_formatter/enabled", self.enabled_checkbox.isChecked())
        self._settings.setValue("post_formatter/temperature", self.temp_spin.value())
        self._settings.setValue("post_formatter/max_tokens", self.max_tokens_spin.value())
        self._settings.setValue("post_formatter/allow_markdown", self.markdown_checkbox.isChecked())
        self._settings.setValue("post_formatter/force_style", self.style_combo.currentData())
        self._settings.setValue("post_formatter/system_prompt", self.prompt_edit.text())
        self.accept() 
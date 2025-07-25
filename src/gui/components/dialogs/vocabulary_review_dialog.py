"""Dialog to review and approve extracted vocabulary words."""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class VocabularyReviewDialog(QDialog):
    """ユーザーに語彙候補を提示して承認させるダイアログ。"""

    def __init__(self, candidate_vocab: List[str], parent: Optional[QWidget] = None) -> None:  # noqa: D401
        super().__init__(parent)
        self.setWindowTitle("Review Vocabulary")
        self._candidate_vocab = candidate_vocab
        self._checkboxes: List[QCheckBox] = []

        scroll = QScrollArea()
        inner_widget = QWidget()
        v_layout = QVBoxLayout(inner_widget)

        for word in candidate_vocab:
            cb = QCheckBox(word)
            self._checkboxes.append(cb)
            v_layout.addWidget(cb)
        v_layout.addStretch()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def selected_words(self) -> List[str]:  # noqa: D401
        """Return list of approved vocab words."""
        return [cb.text() for cb in self._checkboxes if cb.isChecked()] 
"""Main application window (skeleton for Step 7).

NOTE: 本ファイルは Step 7 で大幅に拡張される予定です。
ここではコアクラスの統合とタブ構造のみを実装し、
詳細な設定ダイアログ・エラーハンドリング等は TODO とします。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Set

from PyQt6.QtCore import QSettings, Qt

# Resources
from .resources.config import apply_defaults as _apply_default_settings
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QInputDialog,
    QLineEdit,
)

import os

# Dialogs
from .components.dialogs.post_formatter_settings_dialog import PostFormatterSettingsDialog
from .components.dialogs.style_guide_dialog import StyleGuideDialog
from .components.dialogs.vocabulary_review_dialog import VocabularyReviewDialog

# Absolute imports for frozen env compatibility
from core.asr_openai import OpenAIASRClient
from core.logging_helper import (
    create_session_dir,
    save_formatted_json,
    save_meta,
    save_prompt_text,
    save_raw_text,
)
from core.post_formatter import PostFormatter
from core.style_loader import load_style
from core.vocab_extractor import VocabularyExtractor


class MainWindow(QMainWindow):
    """Main window for Open Super Whisper (simplified)."""

    SETTINGS_ORG = "OpenSuperWhisper"
    SETTINGS_APP = "VoiceInput"

    def __init__(self) -> None:  # noqa: D401
        super().__init__()
        self.setWindowTitle("Open Super Whisper")

        # QSettings
        self.settings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        _apply_default_settings(self.settings)

        # Core components: get API key from env, settings, or prompt
        api_key = (
            os.environ.get("OPENAI_API_KEY")
            or self.settings.value("openai/api_key", "")
        )

        if not api_key:
            api_key, ok = QInputDialog.getText(
                self,
                "OpenAI API Key",
                "OpenAI API キーを入力してください:",
                QLineEdit.Password,
            )
            if not ok or not api_key:
                QMessageBox.critical(self, "API Key Missing", "API キーが設定されていません。")
                sys.exit(1)
            self.settings.setValue("openai/api_key", api_key)

        self.asr_client = OpenAIASRClient(api_key=api_key)
        self.post_formatter = PostFormatter(api_key=api_key)
        self.vocab_extractor = VocabularyExtractor()

        # Session dir
        self.session_dir = create_session_dir()

        # UI setup
        self._init_ui()

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:  # noqa: D401
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        open_action = QAction("Open Audio", self)
        open_action.triggered.connect(self._on_open_audio)
        toolbar.addAction(open_action)

        # Settings menu
        settings_menu = self.menuBar().addMenu("Settings")

        pf_action = settings_menu.addAction("Post Formatter Settings…")
        pf_action.triggered.connect(self._open_post_formatter_settings)

        sg_action = settings_menu.addAction("Load Style Guide…")
        sg_action.triggered.connect(self._open_style_guide_dialog)

        api_action = settings_menu.addAction("API Key…")
        api_action.triggered.connect(self._edit_api_key)

        self.vocab_action = settings_menu.addAction("Review Vocabulary…")
        self.vocab_action.setEnabled(False)
        self.vocab_action.triggered.connect(self._open_vocab_review_dialog)

        # Tabs for Raw / Formatted
        self.tab_widget = QTabWidget()
        self.raw_editor = QPlainTextEdit(readOnly=True)
        self.formatted_editor = QPlainTextEdit(readOnly=True)
        self.tab_widget.addTab(self.raw_editor, "Raw")
        self.tab_widget.addTab(self.formatted_editor, "Formatted")

        self.setCentralWidget(self.tab_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_open_audio(self) -> None:  # noqa: D401
        file_path, _ = QFileDialog.getOpenFileName(self, "Select audio file", "", "Audio (*.wav *.mp3 *.m4a)")
        if not file_path:
            return
        self.perform_transcription(Path(file_path))

    # ------------------------------------------------------------------
    # Core logic (simplified)
    # ------------------------------------------------------------------

    def perform_transcription(self, audio_path: Path) -> None:  # noqa: D401
        self.progress_bar.show()
        self.status_bar.showMessage("Transcribing…")
        QApplication.processEvents()

        try:
            raw_text = self.asr_client.transcribe(str(audio_path))
            save_raw_text(self.session_dir, raw_text)

            self.candidate_vocab: List[str] = self.vocab_extractor.extract(
                raw_text, existing=set()
            )
            if self.candidate_vocab:
                self.vocab_action.setEnabled(True)
            else:
                self.vocab_action.setEnabled(False)
            # Auto-open vocab dialog for now
            if self.candidate_vocab:
                self._open_vocab_review_dialog()

            style_guide = load_style(self.settings.value("style_guide/path"))
            formatted_text = self.post_formatter.format(raw_text, style_guide=style_guide)
            save_formatted_json(self.session_dir, {"text": formatted_text})

            # Save prompt for reference
            save_prompt_text(self.session_dir, "<omitted in skeleton>")
            save_meta(
                self.session_dir,
                {
                    "asr_model": self.asr_client.model_id,
                    "formatter_model": self.post_formatter.model,
                },
            )

            self.raw_editor.setPlainText(raw_text)
            self.formatted_editor.setPlainText(formatted_text)
            self.status_bar.showMessage("Done", 3000)
        except Exception as exc:  # pylint: disable=broad-except
            QMessageBox.critical(self, "Error", str(exc))
            self.status_bar.showMessage("Error", 3000)
        finally:
            self.progress_bar.hide()

    # ------------------------------------------------------------------
    # Dialog open helpers
    # ------------------------------------------------------------------

    def _open_post_formatter_settings(self) -> None:  # noqa: D401
        dlg = PostFormatterSettingsDialog(self.settings, self)
        dlg.exec()

    def _open_style_guide_dialog(self) -> None:  # noqa: D401
        dlg = StyleGuideDialog(self.settings, self)
        dlg.exec()

    def _open_vocab_review_dialog(self) -> None:  # noqa: D401
        if not hasattr(self, "candidate_vocab") or not self.candidate_vocab:
            QMessageBox.information(self, "Vocabulary", "No vocabulary to review.")
            return
        dlg = VocabularyReviewDialog(self.candidate_vocab, self)
        if dlg.exec():
            approved = dlg.selected_words
            if approved:
                existing: List[str] = self.settings.value("vocabulary/list", [])
                self.settings.setValue("vocabulary/list", list(set(existing) | set(approved)))
            # Clear candidate list after review
            self.candidate_vocab = []
            self.vocab_action.setEnabled(False)

    # ------------------------------------------------------------------
    # API Key edit helper
    # ------------------------------------------------------------------

    def _edit_api_key(self) -> None:  # noqa: D401
        current = self.settings.value("openai/api_key", "")
        key, ok = QInputDialog.getText(
            self, "OpenAI API Key", "API キーを入力:", QLineEdit.Password, current
        )
        if ok and key:
            self.settings.setValue("openai/api_key", key)
            QMessageBox.information(self, "API Key", "API キーを更新しました。")


# ----------------------------------------------------------------------
# Entry point for standalone run (for quick test)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec()) 
import os
import sys
import tempfile
import sounddevice as sd
import numpy as np
import wave
import yaml
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QTextEdit, QComboBox, QLabel, 
                               QTabWidget, QCheckBox, QMessageBox, QFileDialog,
                               QDialog, QListWidget, QListWidgetItem, QMenuBar, QMenu,
                               QProgressBar, QLineEdit, QInputDialog)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QAction

from . import asr_api, formatter_api, vocabulary, config, logger

DEFAULT_PROMPT = "Please format the following transcribed text with proper punctuation, capitalization, and clear structure."

class VocabDialog(QDialog):
    def __init__(self, words, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Vocabulary Found")
        self.resize(300, 200)
        layout = QVBoxLayout(self)
        label = QLabel("The following new words were found. Add to custom vocabulary?")
        layout.addWidget(label)
        
        self.listWidget = QListWidget()
        for w in words:
            item = QListWidgetItem(w)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.listWidget.addItem(item)
        layout.addWidget(self.listWidget)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Skip")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_selected_words(self):
        selected = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenSuperWhisper")
        self.resize(800, 600)
        
        self.temp_dir = tempfile.mkdtemp()
        self.is_recording = False
        self.recording = None
        self.fs = 16000
        
        self.loaded_style_text = ""
        self.known_words = vocabulary.load_user_dictionary("user_dict.txt")
        
        # Timer for recording duration display
        self.recording_timer = QTimer()
        self.recording_time = 0
        self.recording_timer.timeout.connect(self.update_recording_time)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
        self.load_settings()
        
    def setup_ui(self):
        # Apply dark theme stylesheet
        self.apply_dark_theme()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Model selection row
        model_layout = QHBoxLayout()
        model_layout.setSpacing(15)
        
        # ASR Model section
        asr_label = QLabel("ASR Model:")
        asr_label.setStyleSheet("font-weight: 600; color: #0078d4;")
        model_layout.addWidget(asr_label)
        self.asr_model_combo = QComboBox()
        self.asr_model_combo.addItems([
            # === Whisper シリーズ（音声専用）===
            "whisper-1",             # 標準Whisper（推奨）
            
            # === GPT-4o 音声転写シリーズ ===  
            "gpt-4o-audio-preview",  # GPT-4o音声プレビュー（最新）
            "gpt-4o-transcribe",     # GPT-4o音声転写
            "gpt-4o-mini-transcribe", # GPT-4o-mini音声転写
            
            # === TTS/音声生成対応モデル ===
            "tts-1",                 # 音声合成（参考）
            "tts-1-hd",              # 高品質音声合成（参考）
            
            # === 実験的モデル ===
            "whisper-large-v3",      # Whisper大型版（カスタム）
            "whisper-medium",        # Whisper中型版（カスタム）
            "whisper-small"          # Whisper小型版（カスタム）
        ])
        model_layout.addWidget(self.asr_model_combo)
        
        # Add spacer
        model_layout.addSpacing(20)
        
        # Formatting Model section  
        format_label = QLabel("Formatting Model:")
        format_label.setStyleSheet("font-weight: 600; color: #0078d4;")
        model_layout.addWidget(format_label)
        self.chat_model_combo = QComboBox()
        self.chat_model_combo.addItems([
            # === テキスト／マルチモーダル会話（Responses API推奨）===
            "gpt-4.1",               # 汎用フラッグシップ
            "gpt-4.1-mini",          # 速度・コスト重視の軽量版
            "gpt-4.1-nano",          # 最小・最安の4.1系
            "gpt-4o",                # omni系・高性能
            "gpt-4o-mini",           # 4oの廉価・高速版
            
            # === 推論特化（Reasoning系）===
            "o3-pro",                # 思考計算量を増やした高精度版
            "o3",                    # 汎用かつ強力な推論モデル
            "o3-mini",               # 小型・低コストの推論モデル
            "o4-mini"                # 最新の小型o系・効率重視
        ])
        model_layout.addWidget(self.chat_model_combo)
        
        layout.addLayout(model_layout)
        
        # Record controls
        record_layout = QHBoxLayout()
        record_layout.setSpacing(12)
        
        self.record_btn = QPushButton("🎤 Record (Ctrl+Space)")
        self.record_btn.setObjectName("record_btn")
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setEnabled(False)
        record_layout.addWidget(self.record_btn)
        record_layout.addWidget(self.stop_btn)
        
        # Recording timer/status
        self.recording_status = QLabel("Ready")
        self.recording_status.setObjectName("recording_status")
        record_layout.addWidget(self.recording_status)
        
        self.post_format_toggle = QCheckBox("Apply Formatting Stage")
        self.post_format_toggle.setChecked(True)
        record_layout.addWidget(self.post_format_toggle)
        
        layout.addLayout(record_layout)
        
        # Tab widget for results
        self.tab_widget = QTabWidget()
        
        self.raw_text_edit = QTextEdit()
        self.raw_text_edit.setPlaceholderText("Raw transcription will appear here...")
        self.tab_widget.addTab(self.raw_text_edit, "Raw Transcription")
        
        self.formatted_text_edit = QTextEdit()
        self.formatted_text_edit.setPlaceholderText("Formatted text will appear here...")
        self.tab_widget.addTab(self.formatted_text_edit, "Formatted Text")
        
        layout.addWidget(self.tab_widget)
        
        # Prompt editor
        layout.addWidget(QLabel("Formatting Prompt:"))
        self.prompt_text_edit = QTextEdit()
        self.prompt_text_edit.setPlainText(DEFAULT_PROMPT)
        self.prompt_text_edit.setMaximumHeight(100)
        layout.addWidget(self.prompt_text_edit)
        
        # Style guide controls
        style_layout = QHBoxLayout()
        style_layout.setSpacing(12)
        
        self.load_style_btn = QPushButton("Load Style Guide...")
        self.load_style_btn.setObjectName("load_style_btn")
        self.style_path_label = QLabel("No style guide loaded")
        self.style_path_label.setObjectName("style_path_label")
        self.save_btn = QPushButton("💾 Save Transcription...")
        self.save_btn.setObjectName("save_btn")
        
        style_layout.addWidget(self.load_style_btn)
        style_layout.addWidget(self.style_path_label)
        style_layout.addWidget(self.save_btn)
        layout.addLayout(style_layout)
        
        # Connect signals
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.load_style_btn.clicked.connect(self.load_style_guide)
        self.save_btn.clicked.connect(self.save_transcription)
        
        # Connect settings save signals
        self.asr_model_combo.currentTextChanged.connect(
            lambda text: config.save_setting(config.KEY_ASR_MODEL, text))
        self.chat_model_combo.currentTextChanged.connect(
            lambda text: config.save_setting(config.KEY_CHAT_MODEL, text))
        self.post_format_toggle.toggled.connect(
            lambda state: config.save_setting(config.KEY_POST_FORMAT, state))
    
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Transcription...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_transcription)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        load_style_action = QAction("Load Style Guide...", self)
        load_style_action.triggered.connect(self.load_style_guide)
        file_menu.addAction(load_style_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        api_key_action = QAction("Set OpenAI API Key...", self)
        api_key_action.triggered.connect(self.set_api_key)
        settings_menu.addAction(api_key_action)
        
        settings_menu.addSeparator()
        
        reset_action = QAction("Reset to Defaults", self)
        reset_action.triggered.connect(self.reset_to_defaults)
        settings_menu.addAction(reset_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_shortcuts(self):
        # Ctrl+Space for record/stop toggle
        self.record_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        self.record_shortcut.activated.connect(self.toggle_recording)
        
    def load_settings(self):
        # Load saved settings
        asr_model = config.load_setting(config.KEY_ASR_MODEL, "whisper-1")
        idx = self.asr_model_combo.findText(asr_model)
        if idx != -1:
            self.asr_model_combo.setCurrentIndex(idx)
            
        chat_model = config.load_setting(config.KEY_CHAT_MODEL, "gpt-4o-mini")
        idx = self.chat_model_combo.findText(chat_model)
        if idx != -1:
            self.chat_model_combo.setCurrentIndex(idx)
            
        post_format_setting = config.load_setting(config.KEY_POST_FORMAT, True)
        # QSettings may return string "true"/"false", convert to bool
        if isinstance(post_format_setting, str):
            post_format_setting = post_format_setting.lower() == 'true'
        self.post_format_toggle.setChecked(bool(post_format_setting))
        
        prompt_text = config.load_setting(config.KEY_PROMPT_TEXT, DEFAULT_PROMPT)
        self.prompt_text_edit.setPlainText(prompt_text)
        
        style_path = config.load_setting(config.KEY_STYLE_GUIDE_PATH, "")
        if style_path and os.path.exists(style_path):
            self.load_style_guide_from_file(style_path)
            
        geom = config.load_setting(config.KEY_WINDOW_GEOMETRY)
        if geom:
            self.restoreGeometry(geom)
    
    def closeEvent(self, event):
        # Save settings on close
        config.save_setting(config.KEY_WINDOW_GEOMETRY, self.saveGeometry())
        config.save_setting(config.KEY_PROMPT_TEXT, self.prompt_text_edit.toPlainText())
        super().closeEvent(event)
    
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def update_recording_time(self):
        self.recording_time += 1
        mins = self.recording_time // 60
        secs = self.recording_time % 60
        self.recording_status.setText(f"🔴 Recording... {mins:02d}:{secs:02d}")
        
    def start_recording(self):
        if self.is_recording:
            return
        self.is_recording = True
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Start recording timer
        self.recording_time = 0
        self.recording_timer.start(1000)  # Update every second
        
        duration = 60  # max duration in seconds
        self.recording = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
        
    def stop_recording(self):
        if not self.is_recording:
            return
        
        sd.stop()
        sd.wait()
        self.is_recording = False
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Stop recording timer
        self.recording_timer.stop()
        self.recording_status.setText("Processing...")
        
        # Trim recording to actual length
        recording = self.recording[:,0]
        nonzero_indices = np.where(recording != 0)[0]
        if len(nonzero_indices) > 0:
            last_index = nonzero_indices[-1]
            recording = recording[:last_index+1]
        
        # Save to WAV file
        wav_path = os.path.join(self.temp_dir, "recorded.wav")
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.fs)
            wf.writeframes(recording.tobytes())
        
        # Transcribe
        try:
            selected_asr_model = self.asr_model_combo.currentText()
            result_text = asr_api.transcribe_audio(wav_path, model=selected_asr_model)
        except Exception as e:
            self.show_error(f"Transcription failed:\n{e}")
            return
            
        self.raw_text_edit.setPlainText(result_text)
        logger.logger.info(f"Transcribed with {selected_asr_model}: {result_text}")
        
        # Check vocabulary
        new_words = vocabulary.extract_new_vocabulary(result_text, self.known_words)
        if new_words:
            dlg = VocabDialog(new_words, parent=self)
            if dlg.exec():
                selected = dlg.get_selected_words()
                if selected:
                    self.known_words.update(selected)
                    vocabulary.save_user_dictionary("user_dict.txt", self.known_words)
                    logger.logger.info(f"Added new vocab: {selected}")
        
        # Format if enabled
        if self.post_format_toggle.isChecked():
            self.run_formatting(result_text)
        
        # Update status
        self.recording_status.setText("Ready")
            
    def run_formatting(self, raw_text: str):
        user_prompt = self.prompt_text_edit.toPlainText().strip()
        style_text = self.loaded_style_text
        model = self.chat_model_combo.currentText()
        
        try:
            formatted = formatter_api.format_text(raw_text, prompt=user_prompt, 
                                                  style_guide=style_text, model=model)
        except Exception as e:
            self.show_error(f"Formatting failed:\n{e}")
            return
            
        self.formatted_text_edit.setPlainText(formatted)
        logger.logger.info(f"Formatted with {model}: {formatted}")
        logger.logger.info(f"Formatting prompt used: {user_prompt}")
        if style_text:
            logger.logger.info(f"Style guide used:\n{style_text}")
    
    def load_style_guide(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Style Guide", "", "YAML Files (*.yaml *.yml);;JSON Files (*.json)")
        if path:
            self.load_style_guide_from_file(path)
            config.save_setting(config.KEY_STYLE_GUIDE_PATH, path)
    
    def load_style_guide_from_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    data = json.load(f)
                    self.loaded_style_text = json.dumps(data, indent=2)
                else:  # YAML
                    data = yaml.safe_load(f)
                    self.loaded_style_text = yaml.dump(data, default_flow_style=False)
            
            self.style_path_label.setText(f"Loaded: {os.path.basename(path)}")
            
        except Exception as e:
            self.show_error(f"Failed to load style guide:\n{e}")
    
    def save_transcription(self):
        # Determine which text to save
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Raw tab
            text_to_save = self.raw_text_edit.toPlainText()
            default_name = "raw_transcription.txt"
        else:  # Formatted tab
            text_to_save = self.formatted_text_edit.toPlainText()
            default_name = "formatted_transcription.txt"
        
        if not text_to_save.strip():
            QMessageBox.information(self, "No Content", "No transcription to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Transcription", default_name,
            "Text Files (*.txt);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_to_save)
                QMessageBox.information(self, "Success", f"Transcription saved to {file_path}")
                logger.logger.info(f"Saved transcription to: {file_path}")
            except Exception as e:
                self.show_error(f"Failed to save file:\n{e}")
    
    def reset_to_defaults(self):
        reply = QMessageBox.question(
            self, "Reset Settings", 
            "This will reset all settings to defaults. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all settings
            config.settings.clear()
            
            # Reset UI to defaults
            self.asr_model_combo.setCurrentText("whisper-1")
            self.chat_model_combo.setCurrentText("gpt-4o-mini")
            self.post_format_toggle.setChecked(True)
            self.prompt_text_edit.setPlainText(DEFAULT_PROMPT)
            self.loaded_style_text = ""
            self.style_path_label.setText("No style guide loaded")
            
            # Reset window geometry
            self.resize(800, 600)
            
            QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
            logger.logger.info("Settings reset to defaults")
    
    def show_about(self):
        about_text = """
        <h3>OpenSuperWhisper v0.1.0</h3>
        <p>Two-Stage Voice Transcription Tool</p>
        <p>A cross-platform voice transcription application that uses OpenAI's 
        state-of-the-art models to transcribe audio and then polish the 
        transcription according to your desired style.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Real-time audio recording and transcription</li>
        <li>Two-stage transcription pipeline (ASR → Formatting)</li>
        <li>Custom formatting prompts & style guides</li>
        <li>Japanese vocabulary extraction with Janome</li>
        <li>Persistent settings and logging</li>
        </ul>
        <p>Licensed under MIT License</p>
        """
        QMessageBox.about(self, "About OpenSuperWhisper", about_text)
    
    def set_api_key(self):
        current_key = config.load_setting(config.KEY_API_KEY, "")
        
        # Show input dialog with masked text for security
        api_key, ok = QInputDialog.getText(
            self, "Set OpenAI API Key", 
            "Enter your OpenAI API key:",
            QLineEdit.Password,
            current_key
        )
        
        if ok and api_key.strip():
            # Basic validation - OpenAI keys start with 'sk-'
            if not api_key.startswith('sk-'):
                QMessageBox.warning(self, "Invalid API Key", 
                                  "OpenAI API keys should start with 'sk-'")
                return
                
            # Save the API key
            config.save_setting(config.KEY_API_KEY, api_key.strip())
            
            # Set environment variable for current session
            os.environ["OPENAI_API_KEY"] = api_key.strip()
            
            QMessageBox.information(self, "API Key Set", 
                                  "OpenAI API key has been saved successfully.")
            logger.logger.info("OpenAI API key updated via UI")
        elif ok:
            QMessageBox.warning(self, "Empty API Key", 
                              "Please enter a valid API key.")
    
    def apply_dark_theme(self):
        """Apply sophisticated dark theme with high contrast and modern aesthetics"""
        dark_style = """
        /* Main Window */
        QMainWindow {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        
        /* Central Widget */
        QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
            font-size: 11pt;
        }
        
        /* Labels */
        QLabel {
            color: #e0e0e0;
            font-weight: 500;
            padding: 2px;
        }
        
        /* Combo Boxes */
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 8px 12px;
            color: #ffffff;
            font-weight: 500;
            min-width: 120px;
        }
        QComboBox:hover {
            border: 1px solid #0078d4;
            background-color: #333333;
        }
        QComboBox:focus {
            border: 2px solid #0078d4;
            background-color: #333333;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #404040;
            background-color: #2d2d2d;
            border-radius: 0px 6px 6px 0px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #e0e0e0;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 6px;
            selection-background-color: #0078d4;
            color: #ffffff;
            padding: 2px;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #0078d4;
            border: none;
            border-radius: 8px;
            color: #ffffff;
            font-weight: 600;
            padding: 12px 20px;
            font-size: 11pt;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }
        
        /* Record Button Special Styling */
        QPushButton#record_btn {
            background-color: #dc3545;
            font-size: 12pt;
            padding: 15px 25px;
        }
        QPushButton#record_btn:hover {
            background-color: #c82333;
        }
        QPushButton#record_btn:pressed {
            background-color: #bd2130;
        }
        
        /* Stop Button */
        QPushButton#stop_btn {
            background-color: #6c757d;
        }
        QPushButton#stop_btn:hover {
            background-color: #5a6268;
        }
        
        /* Save Button */
        QPushButton#save_btn {
            background-color: #28a745;
        }
        QPushButton#save_btn:hover {
            background-color: #218838;
        }
        
        /* Load Style Button */
        QPushButton#load_style_btn {
            background-color: #6f42c1;
        }
        QPushButton#load_style_btn:hover {
            background-color: #5a2d91;
        }
        
        /* Text Edits */
        QTextEdit {
            background-color: #252525;
            border: 1px solid #404040;
            border-radius: 8px;
            color: #ffffff;
            padding: 12px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            line-height: 1.4;
        }
        QTextEdit:focus {
            border: 2px solid #0078d4;
            background-color: #2a2a2a;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #404040;
            border-radius: 8px;
            background-color: #252525;
            margin-top: 5px;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 10px 20px;
            color: #e0e0e0;
            font-weight: 500;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
            color: #ffffff;
            font-weight: 600;
        }
        QTabBar::tab:hover:!selected {
            background-color: #333333;
            color: #ffffff;
        }
        
        /* Checkbox */
        QCheckBox {
            color: #e0e0e0;
            font-weight: 500;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #404040;
            background-color: #2d2d2d;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04LjUgMUwzLjUgNkwxLjUgNCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        QCheckBox::indicator:hover {
            border: 2px solid #0078d4;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #1a1a1a;
            color: #ffffff;
            border-bottom: 1px solid #404040;
            padding: 4px;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 4px;
        }
        QMenuBar::item:selected {
            background-color: #2d2d2d;
        }
        QMenuBar::item:pressed {
            background-color: #0078d4;
        }
        
        /* Menu */
        QMenu {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 6px;
            color: #ffffff;
            padding: 4px;
        }
        QMenu::item {
            padding: 8px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #0078d4;
        }
        QMenu::separator {
            height: 1px;
            background-color: #404040;
            margin: 4px 0px;
        }
        
        /* Status Label */
        QLabel#recording_status {
            color: #ffffff;
            font-weight: 600;
            font-size: 12pt;
            padding: 8px 12px;
            background-color: #2d2d2d;
            border-radius: 6px;
            border: 1px solid #404040;
        }
        
        /* Style Path Label */
        QLabel#style_path_label {
            color: #ffc107;
            font-style: italic;
            background-color: #2d2d2d;
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid #404040;
        }
        """
        
        self.setStyleSheet(dark_style)
    
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
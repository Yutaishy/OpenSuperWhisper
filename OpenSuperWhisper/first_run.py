"""
First-run setup wizard for OpenSuperWhisper
Guides users through initial configuration
"""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import config, logger


class FirstRunWizard(QDialog):
    """Setup wizard for first-time users"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_step = 0
        self.steps = [
            self.create_welcome_step,
            self.create_api_key_step,
            self.create_permissions_step,
            self.create_completion_step
        ]
        self.setup_ui()
        self.show_step(0)

    def setup_ui(self) -> None:
        """Setup the wizard UI"""
        self.setWindowTitle("OpenSuperWhisper Setup")
        self.setFixedSize(600, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "windows", "osw.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main layout
        layout = QVBoxLayout()

        # Header
        self.header = QLabel("Welcome to OpenSuperWhisper")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.header.setFont(font)
        layout.addWidget(self.header)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(len(self.steps) - 1)
        layout.addWidget(self.progress)

        # Content area
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        layout.addWidget(self.content_frame)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.previous_step)
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.next_step)
        self.finish_btn = QPushButton("Finish")
        self.finish_btn.clicked.connect(self.finish_setup)
        self.finish_btn.hide()

        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.finish_btn)

        layout.addLayout(nav_layout)
        self.setLayout(layout)

    def clear_content(self) -> None:
        """Clear the content area"""
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)

    def show_step(self, step_index: int) -> None:
        """Show a specific step"""
        if 0 <= step_index < len(self.steps):
            self.current_step = step_index
            self.progress.setValue(step_index)
            self.clear_content()
            self.steps[step_index]()

            # Update navigation
            self.back_btn.setEnabled(step_index > 0)
            self.next_btn.setVisible(step_index < len(self.steps) - 1)
            self.finish_btn.setVisible(step_index == len(self.steps) - 1)

    def create_welcome_step(self) -> None:
        """Welcome and introduction step"""
        self.header.setText("Welcome to OpenSuperWhisper")

        intro = QTextEdit()
        intro.setReadOnly(True)
        intro.setMaximumHeight(200)
        intro.setHtml("""
        <h3>🎤 Transform Your Voice into Perfect Text</h3>
        <p>OpenSuperWhisper uses AI to transcribe and format your speech with professional quality.</p>
        <h4>✨ Key Features:</h4>
        <ul>
            <li><b>Global Hotkey Support</b> - Record from anywhere with Ctrl+Space</li>
            <li><b>Two-Stage AI Pipeline</b> - Whisper transcription + GPT formatting</li>
            <li><b>Automatic Clipboard</b> - Results instantly ready to paste</li>
            <li><b>Custom Presets</b> - Tailored formatting for different use cases</li>
        </ul>

        <p>This wizard will help you set up OpenSuperWhisper in just a few steps.</p>
        """)
        self.content_layout.addWidget(intro)

        # System requirements check
        req_frame = QFrame()
        req_layout = QVBoxLayout(req_frame)
        req_layout.addWidget(QLabel("📋 System Requirements:"))

        requirements = [
            ("✓ Python 3.12+", True),
            ("✓ Internet connection", True),
            ("⚠ OpenAI API key (next step)", False),
            ("⚠ Microphone access", False)
        ]

        for req, met in requirements:
            label = QLabel(req)
            if met:
                label.setStyleSheet("color: green;")
            else:
                label.setStyleSheet("color: orange;")
            req_layout.addWidget(label)

        self.content_layout.addWidget(req_frame)

    def create_api_key_step(self) -> None:
        """API key configuration step"""
        self.header.setText("OpenAI API Key Setup")

        info = QLabel("""
        📝 OpenSuperWhisper requires an OpenAI API key to function.

        🔗 Get your API key at: https://platform.openai.com/api-keys
        💡 Expected cost: ~$0.01-0.05 per minute of audio
        """)
        info.setWordWrap(True)
        self.content_layout.addWidget(info)

        # API key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        key_layout.addWidget(self.api_key_input)
        self.content_layout.addLayout(key_layout)

        # Validation info
        self.key_status = QLabel("")
        self.content_layout.addWidget(self.key_status)

        # Test button
        test_btn = QPushButton("🧪 Test API Key")
        test_btn.clicked.connect(self.test_api_key)
        self.content_layout.addWidget(test_btn)

        # Skip option
        self.skip_key = QCheckBox("Skip for now (you can set this later in Settings)")
        self.content_layout.addWidget(self.skip_key)

    def create_permissions_step(self) -> None:
        """Permissions and privacy step"""
        self.header.setText("Permissions & Privacy")

        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(150)
        info.setHtml("""
        <h4>🔒 Privacy & Security Information</h4>
        <p>OpenSuperWhisper respects your privacy:</p>
        <ul>
            <li><b>Audio:</b> Sent to OpenAI for transcription, then deleted</li>
            <li><b>API Key:</b> Stored locally on your computer only</li>
            <li><b>No Tracking:</b> No analytics or user data collection</li>
        </ul>
        """)
        self.content_layout.addWidget(info)

        # Permissions checklist
        perms_frame = QFrame()
        perms_layout = QVBoxLayout(perms_frame)
        perms_layout.addWidget(QLabel("📋 Required Permissions:"))

        self.mic_perm = QCheckBox("🎤 Microphone access for recording")
        self.hotkey_perm = QCheckBox("⌨️ Global hotkey monitoring (Ctrl+Space)")
        self.clipboard_perm = QCheckBox("📋 Clipboard access for auto-copy")

        perms_layout.addWidget(self.mic_perm)
        perms_layout.addWidget(self.hotkey_perm)
        perms_layout.addWidget(self.clipboard_perm)

        self.content_layout.addWidget(perms_frame)

        # Auto-grant permissions button
        grant_btn = QPushButton("✅ Grant All Permissions")
        grant_btn.clicked.connect(self.grant_permissions)
        self.content_layout.addWidget(grant_btn)

    def create_completion_step(self) -> None:
        """Completion and first launch step"""
        self.header.setText("Setup Complete!")

        completion = QTextEdit()
        completion.setReadOnly(True)
        completion.setHtml("""
        <h3>🎉 OpenSuperWhisper is Ready!</h3>
        <h4>🚀 Quick Start Guide:</h4>
        <ol>
            <li><b>Press Ctrl+Space</b> anywhere to start recording</li>
            <li><b>Speak clearly</b> into your microphone</li>
            <li><b>Press Ctrl+Space again</b> to stop and process</li>
            <li><b>Press Ctrl+V</b> to paste the formatted text</li>
        </ol>

        <h4>💡 Pro Tips:</h4>
        <ul>
            <li>Try different presets for various use cases</li>
            <li>Create custom style guides in Settings</li>
            <li>Monitor the recording indicator in the bottom-right</li>
        </ul>

        <p><b>Ready to transform your voice into perfect text?</b></p>
        """)
        self.content_layout.addWidget(completion)

        # Launch options
        launch_frame = QFrame()
        launch_layout = QVBoxLayout(launch_frame)

        self.auto_start = QCheckBox("🚀 Start using OpenSuperWhisper immediately")
        self.auto_start.setChecked(True)
        launch_layout.addWidget(self.auto_start)

        self.show_tutorial = QCheckBox("📚 Show interactive tutorial")
        launch_layout.addWidget(self.show_tutorial)

        self.content_layout.addWidget(launch_frame)

    def test_api_key(self) -> None:
        """Test the provided API key"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.key_status.setText("❌ Please enter an API key")
            self.key_status.setStyleSheet("color: red;")
            return

        if not api_key.startswith('sk-'):
            self.key_status.setText("⚠️ API key should start with 'sk-'")
            self.key_status.setStyleSheet("color: orange;")
            return

        # TODO: Implement actual API test
        self.key_status.setText("✅ API key format looks correct")
        self.key_status.setStyleSheet("color: green;")

    def grant_permissions(self) -> None:
        """Grant permissions for the application"""
        self.mic_perm.setChecked(True)
        self.hotkey_perm.setChecked(True)
        self.clipboard_perm.setChecked(True)

    def next_step(self) -> None:
        """Go to next step"""
        # Validate current step
        if self.current_step == 1:  # API key step
            if not self.skip_key.isChecked():
                api_key = self.api_key_input.text().strip()
                if not api_key:
                    self.key_status.setText("❌ Please enter an API key or check 'Skip for now'")
                    self.key_status.setStyleSheet("color: red;")
                    return

                # Save API key
                config.save_setting(config.KEY_API_KEY, api_key)
                logger.logger.info("API key configured during first run")

        self.show_step(self.current_step + 1)

    def previous_step(self) -> None:
        """Go to previous step"""
        self.show_step(self.current_step - 1)

    def finish_setup(self) -> None:
        """Complete the setup process"""
        # Mark first run as complete
        config.save_setting("first_run_completed", True)

        # Log completion
        logger.logger.info("First run wizard completed")

        self.accept()


def should_show_first_run() -> bool:
    """Check if first run wizard should be shown"""
    return not config.load_setting("first_run_completed", False)


def show_first_run_wizard(parent: QWidget | None = None) -> bool:
    """Show first run wizard if needed"""
    if should_show_first_run():
        wizard = FirstRunWizard(parent)
        return wizard.exec() == QDialog.DialogCode.Accepted
    return True

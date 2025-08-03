"""
Recording Status Overlay Indicator
Always-on-top floating indicator for recording status display
"""

import os
import sys
from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget

from . import logger


class RecordingIndicator(QWidget):
    """
    Always-on-top recording status indicator that overlays on screen
    """

    def __init__(self) -> None:
        super().__init__()
        self.is_recording = False
        self.blink_timer = QTimer()
        self.fade_animation: QPropertyAnimation | None = None
        self.parent_window: Any = None
        self.setup_ui()
        self.setup_position()
        self.setup_animations()

    def setup_ui(self) -> None:
        """Setup the indicator UI with modern design"""
        # Window flags for always-on-top overlay (platform-specific)
        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Add platform-specific flags
        if sys.platform.startswith('linux'):
            flags |= Qt.WindowType.X11BypassWindowManagerHint
        elif sys.platform == 'win32':
            # Additional Windows-specific flags for proper always-on-top behavior
            flags |= Qt.WindowType.WindowDoesNotAcceptFocus

        self.setWindowFlags(flags)

        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "windows", "osw.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Set window attributes for transparency and staying on top
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # Fixed size for expanded indicator with clear text
        self.setFixedSize(160, 50)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Recording dot indicator
        self.dot_label = QLabel("●")
        self.dot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 16pt;
                font-weight: bold;
            }
        """)

        # Status text
        self.status_label = QLabel("Recording")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                font-weight: 600;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        """)

        layout.addWidget(self.dot_label)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Apply dark theme styling
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(26, 26, 26, 200);
                border: 1px solid rgba(64, 64, 64, 180);
                border-radius: 12px;
            }
        """)

        # Mouse events for interaction
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def setup_position(self) -> None:
        """Position indicator at bottom-right of screen"""
        screen = None

        # Priority: parent window → cursor position → primary screen
        if getattr(self, "parent_window", None):
            screen = self.parent_window.screen()
        if not screen:
            screen = QApplication.screenAt(QCursor.pos())
        if not screen:
            screen = QApplication.primaryScreen()

        # Get available geometry and position at bottom-right
        geo = screen.availableGeometry()
        x = geo.right() - self.width() - 20
        y = geo.bottom() - self.height() - 20
        self.move(x, y)

    def setup_animations(self) -> None:
        """Setup blink animation for recording state"""
        self.blink_timer.timeout.connect(self.toggle_blink)

    def show_recording(self) -> None:
        """Display recording indicator with animation"""
        if self.is_recording:
            return

        logger.logger.debug("RecordingIndicator.show_recording() called")
        self.is_recording = True
        self.status_label.setText("Recording")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 16pt;
                font-weight: bold;
            }
        """)

        # Show with fade-in animation
        self.setWindowOpacity(0.0)
        self.show()
        self.animate_fade_in()
        logger.logger.debug(f"Indicator shown, visible: {self.isVisible()}, size: {self.size()}, pos: {self.pos()}")

        # Start blinking animation
        self.blink_timer.start(1000)  # Blink every 1 second

    def show_processing(self) -> None:
        """Show processing state"""
        logger.logger.debug("RecordingIndicator.show_processing() called")
        self.blink_timer.stop()
        self.status_label.setText("Processing")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #ffc107;
                font-size: 16pt;
                font-weight: bold;
            }
        """)

        # Show with fade-in if not already visible
        if not self.isVisible():
            logger.logger.debug("Processing indicator not visible, showing now")
            self.setWindowOpacity(0.0)
            self.show()
            self.animate_fade_in()
        else:
            logger.logger.debug("Processing indicator already visible, updating state")
        logger.logger.debug(f"Processing indicator shown, visible: {self.isVisible()}, size: {self.size()}, pos: {self.pos()}")

    def hide_recording(self) -> None:
        """Hide recording indicator with animation"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.blink_timer.stop()

        # Show completion state briefly
        self.status_label.setText("Completed")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #28a745;
                font-size: 16pt;
                font-weight: bold;
            }
        """)

        # Hide after 2 seconds
        QTimer.singleShot(2000, self.animate_fade_out)
    
    def show_live_transcribing(self) -> None:
        """Show live transcribing state"""
        self.status_label.setText("Live Transcribing")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #17a2b8;
                font-size: 16pt;
                font-weight: bold;
            }
        """)
    
    def show_processing_chunk(self, current: int, total: int) -> None:
        """Show processing chunk X/Y"""
        self.status_label.setText(f"Processing Chunk {current}/{total}")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #ffc107;
                font-size: 16pt;
                font-weight: bold;
            }
        """)
    
    def show_finalizing(self) -> None:
        """Show finalizing state"""
        self.status_label.setText("Finalizing")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 16pt;
                font-weight: bold;
            }
        """)
    
    def show_cancelled(self) -> None:
        """Show cancelled state"""
        self.status_label.setText("Cancelled")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 16pt;
                font-weight: bold;
            }
        """)
        
        # Hide after 2 seconds
        QTimer.singleShot(2000, self.animate_fade_out)
    
    def show_cancelling(self) -> None:
        """Show cancelling state"""
        self.status_label.setText("Cancelling...")
        self.dot_label.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 16pt;
                font-weight: bold;
            }
        """)

    def toggle_blink(self) -> None:
        """Toggle dot visibility for blinking effect"""
        if not self.is_recording:
            return

        current_opacity = self.dot_label.styleSheet()
        if "color: #dc3545" in current_opacity:
            # Fade to dimmed red
            self.dot_label.setStyleSheet("""
                QLabel {
                    color: rgba(220, 53, 69, 100);
                    font-size: 16pt;
                    font-weight: bold;
                }
            """)
        else:
            # Back to bright red
            self.dot_label.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 16pt;
                    font-weight: bold;
                }
            """)

    def animate_fade_in(self) -> None:
        """Fade-in animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        if self.fade_animation is not None:
            self.fade_animation.setDuration(300)
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(0.9)
            self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.fade_animation.start()

    def animate_fade_out(self) -> None:
        """Fade-out animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        if self.fade_animation is not None:
            self.fade_animation.setDuration(500)
            self.fade_animation.setStartValue(0.9)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
            self.fade_animation.finished.connect(self.hide)
            self.fade_animation.start()

    def mousePressEvent(self, event: Any) -> None:
        """Handle click events on indicator"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Emit signal to stop recording and restore main window
            if self.parent_window is not None and hasattr(self.parent_window, 'restore_from_indicator'):
                self.parent_window.restore_from_indicator()
        super().mousePressEvent(event)

    def enterEvent(self, event: Any) -> None:
        """Mouse hover effect"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(26, 26, 26, 240);
                border: 1px solid rgba(0, 120, 212, 180);
                border-radius: 12px;
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event: Any) -> None:
        """Mouse leave effect"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(26, 26, 26, 200);
                border: 1px solid rgba(64, 64, 64, 180);
                border-radius: 12px;
            }
        """)
        super().leaveEvent(event)


class GlobalRecordingIndicator:
    """
    Singleton manager for the recording indicator
    """
    _instance = None
    _indicator = None

    @classmethod
    def get_instance(cls) -> 'GlobalRecordingIndicator':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """Initialize indicator"""
        if self._indicator is None:
            logger.logger.debug("Creating RecordingIndicator instance")
            app = QApplication.instance()
            if app is None:
                logger.logger.warning("No QApplication instance found!")
                return  # Don't create indicator without QApplication
            else:
                logger.logger.debug(f"QApplication instance found: {app}")
            self._indicator = RecordingIndicator()

    def _ensure_indicator(self) -> None:
        """Ensure indicator is created when QApplication is available"""
        if self._indicator is None:
            app = QApplication.instance()
            if app is not None:
                logger.logger.debug("Creating RecordingIndicator (delayed initialization)")
                self._indicator = RecordingIndicator()
            else:
                logger.logger.debug("QApplication still not available for delayed initialization")

    def show_recording(self) -> None:
        """Show recording indicator"""
        logger.logger.debug("GlobalRecordingIndicator.show_recording() called")
        self._ensure_indicator()
        if self._indicator:
            logger.logger.debug("Calling RecordingIndicator.show_recording()")
            self._indicator.show_recording()
        else:
            logger.logger.warning("No _indicator instance available!")

    def show_processing(self) -> None:
        """Show processing indicator"""
        logger.logger.debug("GlobalRecordingIndicator.show_processing() called")
        self._ensure_indicator()
        if self._indicator:
            logger.logger.debug("Calling RecordingIndicator.show_processing()")
            self._indicator.show_processing()
        else:
            logger.logger.warning("No _indicator instance available for processing!")

    def hide_recording(self) -> None:
        """Hide recording indicator"""
        if self._indicator:
            self._indicator.hide_recording()

    def set_parent_window(self, parent: Any) -> None:
        """Set parent window for communication"""
        if self._indicator:
            # Don't set parent to avoid being minimized with main window
            # Just store reference for communication
            self._indicator.parent_window = parent

    def is_visible(self) -> bool:
        """Check if indicator is currently visible"""
        return bool(self._indicator and self._indicator.is_recording)
    
    def show_live_transcribing(self) -> None:
        """Show live transcribing state"""
        self._ensure_indicator()
        if self._indicator:
            self._indicator.show_live_transcribing()
    
    def show_processing_chunk(self, current: int, total: int) -> None:
        """Show processing chunk state"""
        self._ensure_indicator()
        if self._indicator:
            self._indicator.show_processing_chunk(current, total)
    
    def show_finalizing(self) -> None:
        """Show finalizing state"""
        self._ensure_indicator()
        if self._indicator:
            self._indicator.show_finalizing()
    
    def show_cancelled(self) -> None:
        """Show cancelled state"""
        self._ensure_indicator()
        if self._indicator:
            self._indicator.show_cancelled()
    
    def show_cancelling(self) -> None:
        """Show cancelling state"""
        self._ensure_indicator()
        if self._indicator:
            self._indicator.show_cancelling()

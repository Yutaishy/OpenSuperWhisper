"""
Recording Status Overlay Indicator
Always-on-top floating indicator for recording status display
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QCursor, QPixmap
import sys


class RecordingIndicator(QWidget):
    """
    Always-on-top recording status indicator that overlays on screen
    """
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.blink_timer = QTimer()
        self.fade_animation = None
        self.setup_ui()
        self.setup_position()
        self.setup_animations()
        
    def setup_ui(self):
        """Setup the indicator UI with modern design"""
        # Window flags for always-on-top overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        
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
        
    def setup_position(self):
        """Position indicator at bottom-right of screen"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Position: 20px from bottom-right corner
        x = screen_geometry.width() - self.width() - 20
        y = screen_geometry.height() - self.height() - 20
        
        self.move(x, y)
        
    def setup_animations(self):
        """Setup blink animation for recording state"""
        self.blink_timer.timeout.connect(self.toggle_blink)
        
    def show_recording(self):
        """Display recording indicator with animation"""
        if self.is_recording:
            return
            
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
        
        # Start blinking animation
        self.blink_timer.start(1000)  # Blink every 1 second
        
    def show_processing(self):
        """Show processing state"""
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
            self.setWindowOpacity(0.0)
            self.show()
            self.animate_fade_in()
        
    def hide_recording(self):
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
        
    def toggle_blink(self):
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
            
    def animate_fade_in(self):
        """Fade-in animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(0.9)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
        
    def animate_fade_out(self):
        """Fade-out animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.9)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def mousePressEvent(self, event):
        """Handle click events on indicator"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Emit signal to stop recording and restore main window
            if hasattr(self.parent(), 'restore_from_indicator'):
                self.parent().restore_from_indicator()
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Mouse hover effect"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(26, 26, 26, 240);
                border: 1px solid rgba(0, 120, 212, 180);
                border-radius: 12px;
            }
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
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
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize indicator"""
        if self._indicator is None:
            self._indicator = RecordingIndicator()
    
    def show_recording(self):
        """Show recording indicator"""
        if self._indicator:
            self._indicator.show_recording()
    
    def show_processing(self):
        """Show processing indicator"""
        if self._indicator:
            self._indicator.show_processing()
    
    def hide_recording(self):
        """Hide recording indicator"""
        if self._indicator:
            self._indicator.hide_recording()
    
    def set_parent_window(self, parent):
        """Set parent window for communication"""
        if self._indicator:
            self._indicator.parent = lambda: parent
            
    def is_visible(self):
        """Check if indicator is currently visible"""
        return self._indicator and self._indicator.is_recording
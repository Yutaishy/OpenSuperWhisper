"""
Direct Keyboard Monitoring
Simple and reliable hotkey detection using direct Windows API polling
"""

import sys
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal

# Windows API constants
VK_CONTROL = 0x11
VK_SPACE = 0x20
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3

class DirectHotkeyMonitor(QObject):
    """
    Direct keyboard monitoring using GetAsyncKeyState polling
    More reliable than RegisterHotKey for some systems
    """
    hotkey_pressed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.is_monitoring = False
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_keys)
        self.last_state = False  # To prevent repeated firing

        # Try to import Windows API
        self.api_available = False
        self.user32: Any | None = None
        if sys.platform == "win32":
            try:
                import ctypes
                self.user32 = ctypes.windll.user32
                self.api_available = True
                pass  # Windows API available
            except Exception:
                pass  # Windows API not available

    def start_monitoring(self) -> bool:
        """Start monitoring keyboard state"""
        if not self.api_available:
            pass  # Cannot start monitoring
            return False

        if self.is_monitoring:
            return True

        self.is_monitoring = True
        self.poll_timer.start(50)  # Check every 50ms
        pass  # Started monitoring
        return True

    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        self.poll_timer.stop()
        pass  # Stopped monitoring

    def check_keys(self) -> None:
        """Check for Ctrl+Space combination"""
        if not self.api_available or self.user32 is None:
            return

        try:
            # Check if Control is pressed (either left or right)
            ctrl_pressed = (
                (self.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) or
                (self.user32.GetAsyncKeyState(VK_LCONTROL) & 0x8000) or
                (self.user32.GetAsyncKeyState(VK_RCONTROL) & 0x8000)
            )

            # Check if Space is pressed
            space_pressed = self.user32.GetAsyncKeyState(VK_SPACE) & 0x8000

            current_state = ctrl_pressed and space_pressed

            # Only trigger on new press (not held)
            if current_state and not self.last_state:
                pass  # Hotkey detected
                self.hotkey_pressed.emit("ctrl_space")

            self.last_state = current_state

        except Exception:
            pass  # Error checking keys

# Global instance
_direct_monitor = None

def get_direct_monitor() -> DirectHotkeyMonitor:
    """Get global direct monitor instance"""
    global _direct_monitor
    if _direct_monitor is None:
        _direct_monitor = DirectHotkeyMonitor()
    return _direct_monitor

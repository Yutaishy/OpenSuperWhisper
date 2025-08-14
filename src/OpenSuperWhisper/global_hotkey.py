"""
Global Hotkey Manager
Cross-platform global hotkey registration for background recording
"""

import sys
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal

# Platform-specific imports
if sys.platform == "win32":
    try:
        # ctypes imported later when needed to avoid lint warnings
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False


class GlobalHotkeyManager(QObject):
    """
    Cross-platform global hotkey manager
    """
    # Signals
    hotkey_pressed = Signal(str)  # Emitted when registered hotkey is pressed

    def __init__(self) -> None:
        super().__init__()
        self.registered_hotkeys: dict[int | str, Any] = {}
        self.is_monitoring = False

        # Initialize Windows API attributes
        self.user32: Any | None = None
        self.kernel32: Any | None = None

        # Setup platform-specific monitoring
        if WINDOWS_AVAILABLE:
            self.setup_windows_monitoring()
        else:
            self.setup_fallback_monitoring()

    def setup_windows_monitoring(self) -> None:
        """Setup Windows-specific hotkey monitoring"""
        try:
            # Windows API constants
            self.MOD_ALT = 0x0001
            self.MOD_CTRL = 0x0002
            self.MOD_SHIFT = 0x0004
            self.MOD_WIN = 0x0008

            # Key codes
            self.VK_SPACE = 0x20
            self.VK_F1 = 0x70
            self.VK_F12 = 0x7B

            # Windows API functions
            if WINDOWS_AVAILABLE:
                import ctypes  # Re-import for type checker
                self.user32 = ctypes.windll.user32  # type: ignore[attr-defined]
                self.kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

            # Message monitoring timer
            self.message_timer = QTimer()
            self.message_timer.timeout.connect(self.check_windows_messages)

        except Exception as e:
            print(f"Windows hotkey setup failed: {e}")
            self.setup_fallback_monitoring()

    def setup_fallback_monitoring(self) -> None:
        """Setup fallback monitoring for non-Windows platforms"""
        # Use Qt's built-in shortcut system as fallback
        self.fallback_timer = QTimer()
        self.fallback_timer.timeout.connect(self.check_fallback_hotkeys)

    def register_hotkey(self, hotkey_id: str, modifiers: list[str], key_code: int) -> bool:
        """
        Register a global hotkey

        Args:
            hotkey_id: Unique identifier for the hotkey
            modifiers: List of modifiers ('ctrl', 'alt', 'shift', 'win')
            key_code: Key code (e.g., space=32, F1=112)
        """
        if WINDOWS_AVAILABLE:
            return self.register_windows_hotkey(hotkey_id, modifiers, key_code)
        else:
            return self.register_fallback_hotkey(hotkey_id, modifiers, key_code)

    def register_windows_hotkey(self, hotkey_id: str, modifiers: list[str], key_code: int) -> bool:
        """Register hotkey on Windows"""
        try:
            # Convert modifiers to Windows constants
            mod_flags = 0
            if 'ctrl' in modifiers:
                mod_flags |= self.MOD_CTRL
            if 'alt' in modifiers:
                mod_flags |= self.MOD_ALT
            if 'shift' in modifiers:
                mod_flags |= self.MOD_SHIFT
            if 'win' in modifiers:
                mod_flags |= self.MOD_WIN

            # Get unique hotkey ID (use simpler ID generation)
            hotkey_int_id = abs(hash(hotkey_id)) % 10000 + 1

            # Unregister if already exists
            if hotkey_int_id in self.registered_hotkeys:
                if self.user32 is not None:
                    self.user32.UnregisterHotKey(None, hotkey_int_id)

            # Register with Windows
            if self.user32 is not None:
                result = self.user32.RegisterHotKey(
                    None,  # Window handle (None for global)
                    hotkey_int_id,
                    mod_flags,
                    key_code
                )
            else:
                result = False

            if result:
                self.registered_hotkeys[hotkey_int_id] = hotkey_id
                print(f"Registered hotkey: {hotkey_id} (ID: {hotkey_int_id})")

                # Start monitoring if not already started
                if not self.is_monitoring:
                    self.start_monitoring()

                return True
            else:
                # Get last error for debugging
                error_code = self.kernel32.GetLastError() if self.kernel32 is not None else 0
                print(f"Failed to register hotkey: {hotkey_id} (Error: {error_code})")
                return False

        except Exception as e:
            print(f"Windows hotkey registration error: {e}")
            return False

    def register_fallback_hotkey(self, hotkey_id: str, modifiers: list[str], key_code: int) -> bool:
        """Register hotkey using fallback method"""
        # Store for fallback monitoring
        self.registered_hotkeys[hotkey_id] = {
            'modifiers': modifiers,
            'key_code': key_code
        }

        if not self.is_monitoring:
            self.start_monitoring()

        return True

    def start_monitoring(self) -> None:
        """Start hotkey monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True

        if WINDOWS_AVAILABLE:
            # Start Windows message loop monitoring
            self.message_timer.start(50)  # Check every 50ms
        else:
            # Start fallback monitoring
            self.fallback_timer.start(100)  # Check every 100ms

    def stop_monitoring(self) -> None:
        """Stop hotkey monitoring"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False

        if WINDOWS_AVAILABLE:
            self.message_timer.stop()
        else:
            self.fallback_timer.stop()

    def check_windows_messages(self) -> None:
        """Check for Windows hotkey messages"""
        if not WINDOWS_AVAILABLE:
            return

        try:
            # Check for hotkey messages
            if not WINDOWS_AVAILABLE or self.user32 is None:
                return
            import ctypes  # Re-import for type checker
            from ctypes import wintypes  # Re-import for type checker
            msg = wintypes.MSG()
            while self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                if msg.message == 0x0312:  # WM_HOTKEY
                    hotkey_id = msg.wParam
                    if hotkey_id in self.registered_hotkeys:
                        hotkey_name = self.registered_hotkeys[hotkey_id]
                        self.hotkey_pressed.emit(hotkey_name)

        except Exception as e:
            print(f"Windows message check error: {e}")

    def check_fallback_hotkeys(self) -> None:
        """Check for hotkeys using fallback method"""
        # This is a simplified fallback - in production you might want
        # to use platform-specific libraries like pynput
        pass

    def unregister_hotkey(self, hotkey_id: str) -> bool:
        """Unregister a hotkey"""
        if WINDOWS_AVAILABLE:
            return self.unregister_windows_hotkey(hotkey_id)
        else:
            return self.unregister_fallback_hotkey(hotkey_id)

    def unregister_windows_hotkey(self, hotkey_id: str) -> bool:
        """Unregister Windows hotkey"""
        try:
            hotkey_int_id = hash(hotkey_id) & 0xFFFF
            if hotkey_int_id in self.registered_hotkeys:
                if self.user32 is not None:
                    result = self.user32.UnregisterHotKey(None, hotkey_int_id)
                else:
                    result = False
                if result:
                    del self.registered_hotkeys[hotkey_int_id]
                    print(f"Unregistered hotkey: {hotkey_id}")
                    return True
            return False
        except Exception as e:
            print(f"Windows hotkey unregistration error: {e}")
            return False

    def unregister_fallback_hotkey(self, hotkey_id: str) -> bool:
        """Unregister fallback hotkey"""
        if hotkey_id in self.registered_hotkeys:
            del self.registered_hotkeys[hotkey_id]
            return True
        return False

    def unregister_all(self) -> None:
        """Unregister all hotkeys"""
        for hotkey_id in list(self.registered_hotkeys.keys()):
            if isinstance(hotkey_id, int):
                # Windows hotkey
                self.unregister_windows_hotkey(
                    self.registered_hotkeys[hotkey_id]
                )
            else:
                # Fallback hotkey
                self.unregister_fallback_hotkey(hotkey_id)

        self.stop_monitoring()


# Convenience function to register common hotkeys
def register_ctrl_space_hotkey(callback: Callable[[], None]) -> GlobalHotkeyManager | None:
    """
    Register Ctrl+Space as global recording hotkey

    Args:
        callback: Function to call when hotkey is pressed
    """
    manager = GlobalHotkeyManager()

    # Connect signal to callback
    manager.hotkey_pressed.connect(
        lambda hotkey_id: callback() if hotkey_id == "record_toggle" else None
    )

    # Register Ctrl+Space (key code 32 for space)
    success = manager.register_hotkey(
        "record_toggle",
        ["ctrl"],
        32
    )

    return manager if success else None

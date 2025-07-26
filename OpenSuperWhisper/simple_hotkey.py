"""
Simple Hotkey Monitor
Alternative hotkey implementation using keyboard monitoring
"""

from PySide6.QtCore import QObject, QTimer, Signal
import sys

# Try to import pynput for cross-platform key monitoring
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("pynput not available - hotkeys will be limited to app focus")


class SimpleHotkeyMonitor(QObject):
    """
    Simple hotkey monitor using pynput or fallback methods
    """
    hotkey_pressed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.registered_hotkeys = {}
        self.current_keys = set()
        self.listener = None
        
    def register_hotkey(self, hotkey_id: str, key_combination: str):
        """
        Register a hotkey combination
        
        Args:
            hotkey_id: Unique identifier
            key_combination: String like "ctrl+space", "ctrl+shift+space"
        """
        self.registered_hotkeys[key_combination.lower()] = hotkey_id
        
        if not self.is_monitoring:
            self.start_monitoring()
        
        return True
    
    def start_monitoring(self):
        """Start monitoring keyboard input"""
        if self.is_monitoring:
            return
            
        if PYNPUT_AVAILABLE:
            self.start_pynput_monitoring()
        else:
            self.start_fallback_monitoring()
        
        self.is_monitoring = True
    
    def start_pynput_monitoring(self):
        """Start pynput-based monitoring"""
        try:
            self.listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.listener.start()
            print("Started pynput keyboard monitoring")
        except Exception as e:
            print(f"Failed to start pynput monitoring: {e}")
            self.start_fallback_monitoring()
    
    def start_fallback_monitoring(self):
        """Start fallback monitoring (polling-based)"""
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_fallback_keys)
        self.poll_timer.start(50)  # Check every 50ms
        print("Started fallback keyboard monitoring")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            # Add key to current pressed keys
            key_name = self.get_key_name(key)
            if key_name:
                self.current_keys.add(key_name)
                self.check_hotkey_combinations()
        except Exception as e:
            print(f"Key press error: {e}")
    
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            # Remove key from current pressed keys
            key_name = self.get_key_name(key)
            if key_name and key_name in self.current_keys:
                self.current_keys.remove(key_name)
        except Exception as e:
            print(f"Key release error: {e}")
    
    def get_key_name(self, key):
        """Convert pynput key to string name"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            elif hasattr(key, 'name'):
                return key.name.lower()
            else:
                return str(key).lower().replace('key.', '')
        except:
            return None
    
    def check_hotkey_combinations(self):
        """Check if current key combination matches any registered hotkeys"""
        # Convert current keys to sorted combination string
        if not self.current_keys:
            return
            
        # Create combination string
        sorted_keys = sorted(list(self.current_keys))
        combination = '+'.join(sorted_keys)
        
        print(f"DEBUG: Current keys pressed: {self.current_keys}")
        print(f"DEBUG: Checking combination: {combination}")
        
        # Check all possible combinations (order may vary)
        for registered_combo, hotkey_id in self.registered_hotkeys.items():
            registered_keys = set(registered_combo.split('+'))
            print(f"DEBUG: Checking against registered: {registered_combo} -> {registered_keys}")
            if registered_keys.issubset(self.current_keys):
                print(f"DEBUG: MATCH! Emitting hotkey signal for: {hotkey_id}")
                # Emit signal and clear keys to prevent repeated firing
                self.hotkey_pressed.emit(hotkey_id)
                self.current_keys.clear()
                break
    
    def check_fallback_keys(self):
        """Fallback key checking (Windows-specific)"""
        if not PYNPUT_AVAILABLE and sys.platform == "win32":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                
                # Check common key combinations manually
                ctrl_pressed = user32.GetAsyncKeyState(0x11) & 0x8000  # VK_CONTROL
                space_pressed = user32.GetAsyncKeyState(0x20) & 0x8000  # VK_SPACE
                
                if ctrl_pressed and space_pressed:
                    # Check if this combination is registered
                    if "ctrl+space" in self.registered_hotkeys:
                        hotkey_id = self.registered_hotkeys["ctrl+space"]
                        self.hotkey_pressed.emit(hotkey_id)
                        
                        # Wait a bit to prevent repeated firing
                        self.poll_timer.stop()
                        QTimer.singleShot(200, lambda: self.poll_timer.start())
                        
            except Exception as e:
                print(f"Fallback key check error: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
            self.listener = None
        
        if hasattr(self, 'poll_timer'):
            self.poll_timer.stop()
    
    def unregister_all(self):
        """Unregister all hotkeys"""
        self.registered_hotkeys.clear()
        self.stop_monitoring()


# Global instance
_hotkey_monitor = None

def get_hotkey_monitor():
    """Get global hotkey monitor instance"""
    global _hotkey_monitor
    if _hotkey_monitor is None:
        _hotkey_monitor = SimpleHotkeyMonitor()
    return _hotkey_monitor
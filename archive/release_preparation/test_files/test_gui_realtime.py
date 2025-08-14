"""
GUI test for realtime transcription
This will launch the GUI and test realtime features
"""

import sys
import os
import time
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from OpenSuperWhisper.ui_mainwindow import MainWindow
from OpenSuperWhisper import logger

def test_gui_realtime():
    """Test GUI with realtime features"""
    print("=== GUI Realtime Test ===\n")
    
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    
    # Test 1: Check realtime mode
    print("Test 1: Checking realtime mode...")
    if hasattr(window, 'realtime_mode') and window.realtime_mode:
        print("[OK] Realtime mode is enabled")
    else:
        print("[FAIL] Realtime mode is not enabled")
    
    # Test 2: Check components
    print("\nTest 2: Checking realtime components...")
    if hasattr(window, 'realtime_recorder') and window.realtime_recorder:
        print("[OK] Realtime recorder initialized")
    else:
        print("[FAIL] Realtime recorder not found")
    
    if hasattr(window, 'chunk_processor') and window.chunk_processor:
        print("[OK] Chunk processor initialized")
    else:
        print("[FAIL] Chunk processor not found")
    
    # Test 3: Check UI elements
    print("\nTest 3: Checking UI elements...")
    if hasattr(window, 'record_btn') and window.record_btn:
        print(f"[OK] Record button exists, enabled: {window.record_btn.isEnabled()}")
    else:
        print("[FAIL] Record button not found")
    
    if hasattr(window, 'stop_btn') and window.stop_btn:
        print(f"[OK] Stop button exists, enabled: {window.stop_btn.isEnabled()}")
    else:
        print("[FAIL] Stop button not found")
    
    # Test 4: Check tab names
    print("\nTest 4: Checking tab names...")
    if hasattr(window, 'tab_widget') and window.tab_widget:
        tab_count = window.tab_widget.count()
        print(f"  Tab count: {tab_count}")
        for i in range(tab_count):
            tab_name = window.tab_widget.tabText(i)
            print(f"  Tab {i}: {tab_name}")
            # Should be "Transcription" not "Raw Transcription"
            if tab_name == "Transcription":
                print("[OK] Tab name updated for realtime mode")
    
    # Show window
    window.show()
    
    # Schedule close after 3 seconds
    QTimer.singleShot(3000, window.close)
    QTimer.singleShot(3100, app.quit)
    
    print("\nGUI launched successfully. Window will close in 3 seconds...")
    print("If you see the window, realtime UI is working!")
    
    # Run app
    app.exec()
    
    print("\n=== GUI test completed ===")

if __name__ == "__main__":
    test_gui_realtime()
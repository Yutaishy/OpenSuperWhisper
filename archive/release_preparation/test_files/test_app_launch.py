import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication
    from OpenSuperWhisper.ui_mainwindow import MainWindow
    
    print("Starting OpenSuperWhisper...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Get window info
    print(f"Window title: {window.windowTitle()}")
    print(f"Window size: {window.size()}")
    print(f"Realtime mode: {window.realtime_mode}")
    
    # Show window
    window.show()
    print("Window shown")
    
    # Check if visible
    print(f"Is visible: {window.isVisible()}")
    
    # Take a screenshot after a delay
    from PySide6.QtCore import QTimer
    def take_screenshot():
        print("Taking screenshot...")
        # Just exit for now
        app.quit()
    
    QTimer.singleShot(2000, take_screenshot)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
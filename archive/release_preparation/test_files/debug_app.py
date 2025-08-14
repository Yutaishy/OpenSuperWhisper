#!/usr/bin/env python3
"""
Debug version of OpenSuperWhisper with detailed error logging
"""
import sys
import os
import traceback

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OpenSuperWhisper'))

print("Starting debug mode...")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    print("Importing PySide6...")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    print("[OK] PySide6 imported successfully")
    
    print("Importing OpenSuperWhisper modules...")
    from OpenSuperWhisper.ui_mainwindow import MainWindow
    print("[OK] MainWindow imported successfully")
    
    print("Creating QApplication...")
    # Set Qt platform plugin explicitly
    os.environ['QT_QPA_PLATFORM'] = 'windows'
    
    app = QApplication(sys.argv)
    print("[OK] QApplication created")
    
    print("Creating MainWindow...")
    window = MainWindow()
    print("[OK] MainWindow created")
    
    print("Showing window...")
    window.show()
    print("[OK] Window shown")
    
    print("Starting event loop...")
    sys.exit(app.exec())
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    traceback.print_exc()
    
except Exception as e:
    print(f"[ERROR] Runtime error: {e}")
    traceback.print_exc()
    
except SystemExit:
    print("Application closed normally")
    
finally:
    print("Debug session ended")
#!/usr/bin/env python3
"""
Test MainWindow initialization step by step
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Step 1: Importing Qt...")
    from PySide6.QtWidgets import QApplication
    print("Step 1 OK")
    
    print("Step 2: Creating QApplication...")
    app = QApplication(sys.argv)
    print("Step 2 OK")
    
    print("Step 3: Importing MainWindow...")
    from OpenSuperWhisper.ui_mainwindow import MainWindow
    print("Step 3 OK")
    
    print("Step 4: Creating MainWindow (this might crash)...")
    window = MainWindow()
    print("Step 4 OK - MainWindow created successfully")
    
    print("Step 5: Quick property check...")
    print(f"  Window title: {window.windowTitle()}")
    print(f"  Realtime mode: {window.realtime_mode}")
    print("Step 5 OK")
    
    print("Step 6: Show window...")
    window.show()
    print("Step 6 OK")
    
    print("Step 7: Close immediately...")
    window.close()
    app.quit()
    print("Step 7 OK")
    
    print("All steps completed! MainWindow works.")
    
except Exception as e:
    print(f"Failed at step: {e}")
    import traceback
    traceback.print_exc()
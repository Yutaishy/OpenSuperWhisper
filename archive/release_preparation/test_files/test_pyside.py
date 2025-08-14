#!/usr/bin/env python3
"""
Minimal PySide6 test to isolate the crash
"""
import sys
import os

print("Testing PySide6...")

try:
    # Step 1: Import test
    print("Step 1: Importing PySide6...")
    from PySide6.QtWidgets import QApplication, QWidget, QLabel
    from PySide6.QtCore import Qt
    print("Step 1 OK")
    
    # Step 2: Create app
    print("Step 2: Creating QApplication...")
    app = QApplication(sys.argv)
    print("Step 2 OK")
    
    # Step 3: Create simple widget
    print("Step 3: Creating simple widget...")
    widget = QWidget()
    widget.setWindowTitle("Test Window")
    widget.resize(300, 200)
    print("Step 3 OK")
    
    # Step 4: Show widget
    print("Step 4: Showing widget...")
    widget.show()
    print("Step 4 OK")
    
    # Step 5: Quick exit (don't run full event loop)
    print("Step 5: Quick exit test...")
    widget.close()
    app.quit()
    print("Step 5 OK")
    
    print("All steps completed successfully!")
    
except Exception as e:
    print(f"Error at step: {e}")
    import traceback
    traceback.print_exc()
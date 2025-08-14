import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication
    print("[OK] PySide6 is installed")
    
    from OpenSuperWhisper.ui_mainwindow import MainWindow
    print("[OK] MainWindow can be imported")
    
    from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
    print("[OK] RealtimeRecorder can be imported")
    
    from OpenSuperWhisper.chunk_processor import ChunkProcessor  
    print("[OK] ChunkProcessor can be imported")
    
    print("\nAll components are available. App should work.")
    
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("\nPlease install missing dependencies:")
    print("pip install -r requirements.txt")
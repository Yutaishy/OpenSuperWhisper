"""
Test recording simulation with realtime transcription
Simulates a complete recording session
"""

import sys
import os
import time
import numpy as np
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from OpenSuperWhisper.ui_mainwindow import MainWindow
from OpenSuperWhisper import logger

def simulate_audio_input(window, duration_seconds=5):
    """Simulate audio input in a separate thread"""
    print(f"Simulating {duration_seconds} seconds of audio input...")
    
    sample_rate = 16000
    chunk_duration = 0.1  # 100ms chunks
    samples_per_chunk = int(sample_rate * chunk_duration)
    
    for i in range(int(duration_seconds / chunk_duration)):
        if not window.is_recording:
            break
            
        # Generate audio data
        if i % 20 < 15:  # 75% speech, 25% silence
            # Simulate speech
            audio = 0.2 * np.sin(2 * np.pi * 440 * np.linspace(0, chunk_duration, samples_per_chunk))
            audio += 0.1 * np.random.randn(samples_per_chunk)
        else:
            # Simulate silence
            audio = 0.01 * np.random.randn(samples_per_chunk)
        
        audio = audio.astype(np.float32)
        
        # Add to recorder if in realtime mode
        if window.realtime_mode and window.realtime_recorder:
            result = window.realtime_recorder.add_audio_data(audio)
            if result:
                chunk_id, chunk_audio = result
                print(f"  [CHUNK] Created chunk {chunk_id} with {len(chunk_audio)/sample_rate:.1f}s audio")
        
        time.sleep(chunk_duration)
    
    print("Audio simulation completed")

def test_recording_simulation():
    """Test recording with simulated audio"""
    print("=== Recording Simulation Test ===\n")
    
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    def start_recording():
        print("\nTest 1: Starting recording...")
        if window.record_btn.isEnabled():
            window.record_btn.click()
            print("[OK] Recording started")
            print(f"  Is recording: {window.is_recording}")
            print(f"  Realtime mode: {window.realtime_mode}")
            
            # Start audio simulation in thread
            audio_thread = threading.Thread(
                target=simulate_audio_input,
                args=(window, 3)  # 3 seconds of audio
            )
            audio_thread.start()
        else:
            print("[FAIL] Record button not enabled")
    
    def stop_recording():
        print("\nTest 2: Stopping recording...")
        if window.stop_btn.isEnabled():
            window.stop_btn.click()
            print("[OK] Recording stopped")
            
            # Check results
            if hasattr(window, 'raw_text_edit'):
                text = window.raw_text_edit.toPlainText()
                print(f"  Raw text length: {len(text)} chars")
        else:
            print("[FAIL] Stop button not enabled")
    
    def check_chunks():
        print("\nTest 3: Checking chunks...")
        if window.chunk_processor:
            print(f"  Chunk results: {len(window.chunk_processor.chunk_results)}")
            print(f"  Processing chunks: {len(window.chunk_processor.processing_chunks)}")
            print(f"  API futures: {len(window.chunk_processor.api_futures)}")
        
        if window.realtime_recorder:
            print(f"  Current chunk size: {len(window.realtime_recorder.current_chunk)}")
            print(f"  Current chunk ID: {window.realtime_recorder.chunk_id}")
    
    def close_app():
        print("\n=== Test completed ===")
        window.close()
        app.quit()
    
    # Schedule test sequence
    QTimer.singleShot(1000, start_recording)
    QTimer.singleShot(4500, stop_recording)
    QTimer.singleShot(5000, check_chunks)
    QTimer.singleShot(6000, close_app)
    
    # Run app
    app.exec()

if __name__ == "__main__":
    test_recording_simulation()
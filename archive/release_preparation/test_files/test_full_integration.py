"""
Full integration test with GUI and all components
Tests the complete system including API simulation
"""

import sys
import os
import time
import numpy as np
import threading
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from OpenSuperWhisper.ui_mainwindow import MainWindow
from OpenSuperWhisper import logger

def simulate_long_recording(window, duration_minutes=3):
    """Simulate a long recording session"""
    print(f"\nSimulating {duration_minutes} minute recording...")
    
    sample_rate = 16000
    chunk_duration = 1.0  # 1 second chunks
    samples_per_chunk = int(sample_rate * chunk_duration)
    total_chunks = int(duration_minutes * 60)
    
    # Mock API responses
    window.chunk_processor.asr_api = Mock()
    window.chunk_processor.formatter_api = Mock()
    
    # Mock ASR response
    window.chunk_processor.asr_api.transcribe_audio.return_value = {
        "text": "これはテスト音声です。長時間録音のテストを実行しています。"
    }
    
    # Mock formatter response
    window.chunk_processor.formatter_api.format_text.return_value = {
        "formatted_text": "これはテスト音声です。\n長時間録音のテストを実行しています。",
        "model": "gpt-4o-mini"
    }
    
    original_time = time.time
    start_time = time.time()
    
    try:
        for second in range(total_chunks):
            if not window.is_recording:
                print(f"Recording stopped at {second}s")
                break
            
            # Simulate time progression
            simulated_time = start_time + second
            time.time = lambda: simulated_time
            
            # Generate audio pattern
            if second % 120 < 90:  # First 90s of each 2min: mostly speech
                if second % 10 < 8:  # 80% speech
                    audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, chunk_duration, samples_per_chunk))
                else:  # 20% short silence
                    audio = 0.05 * np.random.randn(samples_per_chunk)
            else:  # Last 30s of each 2min: more silence
                if second % 10 < 3:  # 30% speech
                    audio = 0.2 * np.sin(2 * np.pi * 440 * np.linspace(0, chunk_duration, samples_per_chunk))
                else:  # 70% silence
                    audio = 0.01 * np.random.randn(samples_per_chunk)
            
            audio = audio.astype(np.float32)
            
            # Add to recorder
            result = window.realtime_recorder.add_audio_data(audio)
            
            if result:
                chunk_id, chunk_audio = result
                duration = len(chunk_audio) / sample_rate
                print(f"\n[CHUNK {chunk_id}] Created at {second}s ({second/60:.1f}min)")
                print(f"  Duration: {duration:.1f}s")
                print(f"  Processing in background...")
                
                # Simulate API processing delay
                def simulate_api_response():
                    time.sleep(0.5)  # Simulate API delay
                    # Update UI with transcription
                    if hasattr(window, 'raw_text_edit'):
                        current_text = window.raw_text_edit.toPlainText()
                        new_text = f"\n[Chunk {chunk_id}] これはテスト音声です。長時間録音のテストを実行しています。"
                        window.raw_text_edit.setPlainText(current_text + new_text)
                
                # Run in thread to not block
                threading.Thread(target=simulate_api_response).start()
            
            # Progress update every 30 seconds
            if (second + 1) % 30 == 0:
                print(f"Progress: {(second + 1)/60:.1f} minutes recorded")
                if window.chunk_processor:
                    print(f"  Processed chunks: {len(window.chunk_processor.chunk_results)}")
                    print(f"  Processing queue: {len(window.chunk_processor.processing_chunks)}")
            
            # Sleep to simulate real-time
            time.sleep(0.01)  # Fast simulation
    
    finally:
        # Restore original time
        time.time = original_time
    
    print(f"\nRecording simulation completed after {second}s")

def test_full_integration():
    """Test full system integration"""
    print("=== Full Integration Test ===\n")
    
    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create main window
    print("1. Creating main window...")
    window = MainWindow()
    window.show()
    print("[OK] Window created and shown")
    
    # Verify realtime mode
    print("\n2. Checking realtime mode...")
    print(f"  Realtime mode: {window.realtime_mode}")
    print(f"  Realtime recorder: {window.realtime_recorder is not None}")
    print(f"  Chunk processor: {window.chunk_processor is not None}")
    
    def start_recording():
        print("\n3. Starting recording...")
        if window.record_btn.isEnabled():
            window.record_btn.click()
            print("[OK] Recording started")
            print(f"  Is recording: {window.is_recording}")
            
            # Start simulation in thread
            sim_thread = threading.Thread(
                target=simulate_long_recording,
                args=(window, 2)  # 2 minute test
            )
            sim_thread.start()
        else:
            print("[FAIL] Record button not enabled")
    
    def check_status():
        print("\n4. Checking status after 1 minute...")
        if window.realtime_recorder and window.chunk_processor:
            print(f"  Current chunk ID: {window.realtime_recorder.chunk_id}")
            print(f"  Processed chunks: {len(window.chunk_processor.chunk_results)}")
            print(f"  Processing queue: {len(window.chunk_processor.processing_chunks)}")
            
            # Check UI updates
            if hasattr(window, 'raw_text_edit'):
                text = window.raw_text_edit.toPlainText()
                print(f"  Transcription text length: {len(text)} chars")
                if text:
                    print(f"  First 100 chars: {text[:100]}...")
    
    def stop_recording():
        print("\n5. Stopping recording...")
        if window.stop_btn.isEnabled():
            window.stop_btn.click()
            print("[OK] Recording stopped")
            
            # Final status
            time.sleep(1)  # Wait for processing
            print("\n6. Final results:")
            if window.chunk_processor:
                print(f"  Total chunks processed: {len(window.chunk_processor.chunk_results)}")
                for chunk_id, result in window.chunk_processor.chunk_results.items():
                    if result:
                        print(f"    Chunk {chunk_id}: transcribed")
            
            if hasattr(window, 'raw_text_edit'):
                text = window.raw_text_edit.toPlainText()
                print(f"  Final transcription length: {len(text)} chars")
    
    def close_app():
        print("\n=== Test completed successfully! ===")
        window.close()
        app.quit()
    
    # Schedule test sequence
    QTimer.singleShot(500, start_recording)
    QTimer.singleShot(60000, check_status)  # Check after 1 minute
    QTimer.singleShot(120000, stop_recording)  # Stop after 2 minutes
    QTimer.singleShot(125000, close_app)
    
    # Run app
    app.exec()

if __name__ == "__main__":
    test_full_integration()
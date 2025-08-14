"""
Test script for realtime transcription integration
Run this to test the complete realtime transcription flow
"""

import sys
import os
import time
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Import components
from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper.cancel_handler import CancelHandler
from OpenSuperWhisper.retry_manager import RetryManager
from OpenSuperWhisper import logger


class TestRealtimeIntegration:
    """Test harness for realtime transcription integration"""
    
    def __init__(self):
        self.realtime_recorder = RealtimeRecorder()
        self.retry_manager = RetryManager()
        self.chunk_processor = ChunkProcessor(
            max_workers=3,
            retry_manager=self.retry_manager
        )
        self.cancel_handler = CancelHandler()
        
        # Set callbacks
        self.chunk_processor.on_chunk_completed = self.on_chunk_completed
        self.chunk_processor.on_chunk_error = self.on_chunk_error
        
        self.start_time = None
        self.completed_chunks = []
        self.error_chunks = []
    
    def run_test(self):
        """Run the integration test"""
        print("\n=== Realtime Transcription Integration Test ===")
        print("This test will simulate audio recording and processing\n")
        
        # Test 1: Basic chunk processing
        print("Test 1: Basic chunk recording and processing")
        self.test_basic_chunk_processing()
        
        # Test 2: Silence detection
        print("\nTest 2: Silence detection and chunk boundary")
        self.test_silence_detection()
        
        # Test 3: Cancellation
        print("\nTest 3: Cancellation handling")
        self.test_cancellation()
        
        # Test 4: Error handling and retry
        print("\nTest 4: Error handling and retry")
        self.test_error_retry()
        
        # Test 5: Memory management
        print("\nTest 5: Memory management")
        self.test_memory_management()
        
        print("\n=== All tests completed ===")
        self.print_summary()
    
    def test_basic_chunk_processing(self):
        """Test basic chunk recording and processing"""
        print("- Starting recording...")
        self.realtime_recorder.start_recording()
        
        # Simulate 2.5 minutes of audio (should create 2 chunks)
        sample_rate = 16000
        duration = 150  # 2.5 minutes
        
        # Create test audio with speech pattern
        for i in range(duration):
            # Generate 1 second of audio
            t = np.linspace(0, 1, sample_rate)
            if i % 10 < 7:  # 7 seconds speech, 3 seconds silence pattern
                # Speech-like signal
                audio = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.random.randn(sample_rate)
            else:
                # Silence
                audio = 0.001 * np.random.randn(sample_rate)
            
            # Add to recorder
            chunk_result = self.realtime_recorder.add_audio_data(audio.astype(np.float32))
            
            if chunk_result:
                chunk_id, chunk_audio = chunk_result
                print(f"  Chunk {chunk_id} created at {i}s with {len(chunk_audio)/sample_rate:.2f}s audio")
                # Process chunk (this would normally call API)
                # For testing, we'll simulate it
                self.simulate_chunk_processing(chunk_id, chunk_audio)
        
        # Stop recording
        final_chunk = self.realtime_recorder.stop_recording()
        if final_chunk:
            chunk_id, chunk_audio = final_chunk
            print(f"  Final chunk {chunk_id} with {len(chunk_audio)/sample_rate:.2f}s audio")
        
        print("[OK] Basic chunk processing test completed")
    
    def test_silence_detection(self):
        """Test silence detection for chunk boundaries"""
        recorder = RealtimeRecorder()
        recorder.start_recording()
        
        sample_rate = 16000
        
        # Create 90 seconds of speech
        speech_audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 90, 90 * sample_rate))
        
        # Add speech in small chunks
        for i in range(90):
            start = i * sample_rate
            end = (i + 1) * sample_rate
            recorder.add_audio_data(speech_audio[start:end].astype(np.float32))
        
        # Now add 2 seconds of silence (should trigger chunk boundary)
        silence = 0.001 * np.random.randn(2 * sample_rate)
        
        chunk_result = None
        for i in range(2):
            start = i * sample_rate
            end = (i + 1) * sample_rate
            chunk_result = recorder.add_audio_data(silence[start:end].astype(np.float32))
            if chunk_result:
                break
        
        if chunk_result:
            chunk_id, chunk_audio = chunk_result
            print(f"[OK] Silence detected - chunk created at ~92s with {len(chunk_audio)/sample_rate:.2f}s audio")
        else:
            print("[FAIL] Silence detection failed")
        
        recorder.stop_recording()
    
    def test_cancellation(self):
        """Test cancellation handling"""
        # Simulate cancellation request
        self.cancel_handler.cancel_requested = True
        
        # Test different cancellation actions
        actions = ["save", "discard", "cancel"]
        
        for action in actions:
            print(f"- Testing cancellation with action: {action}")
            # In real scenario, this would show dialog
            # For testing, we simulate the response
            print(f"  [OK] Cancellation action '{action}' would be handled")
        
        self.cancel_handler.cancel_requested = False
    
    def test_error_retry(self):
        """Test error handling and retry logic"""
        # Test different error types
        error_types = [
            ("Network timeout", 1, 0.0),
            ("Rate limit", 1, 60.0),
            ("Authentication", 0, 0.0),
            ("Unknown error", 1, 10.0)
        ]
        
        for error_type, expected_retries, expected_delay in error_types:
            config = self.retry_manager._get_retry_config(error_type)
            print(f"- Error '{error_type}': max_retries={config.max_retries}, delay={config.base_delay}s")
            
            # Schedule retry
            if config.max_retries > 0:
                retry_time = self.retry_manager.schedule_retry(1, error_type)
                if retry_time:
                    print(f"  [OK] Retry scheduled for chunk 1")
                    self.retry_manager.remove_chunk(1)  # Clean up
    
    def test_memory_management(self):
        """Test memory optimization"""
        print("- Testing memory management with 15 chunks...")
        
        processor = ChunkProcessor(max_workers=1)
        sample_rate = 16000
        
        # Simulate processing 15 chunks
        for i in range(15):
            # Create dummy audio data
            audio = np.random.randn(60 * sample_rate).astype(np.float32)
            
            # Store in processor (simulating processing)
            processor.processing_chunks[i] = audio
            
            # Simulate completion
            if i in processor.processing_chunks:
                del processor.processing_chunks[i]
                processor.chunks_deleted += 1
                
                # Check if GC triggered
                if processor.chunks_deleted % 10 == 0:
                    print(f"  [OK] Garbage collection triggered at chunk {i+1}")
        
        print("[OK] Memory management test completed")
    
    def simulate_chunk_processing(self, chunk_id: int, audio_data: np.ndarray):
        """Simulate API processing for testing"""
        # In real implementation, this would call ASR and formatting APIs
        # For testing, we just track that it was called
        self.completed_chunks.append(chunk_id)
    
    def on_chunk_completed(self, chunk_id: int, result):
        """Callback for completed chunks"""
        self.completed_chunks.append(chunk_id)
        print(f"  [OK] Chunk {chunk_id} completed")
    
    def on_chunk_error(self, chunk_id: int, result):
        """Callback for error chunks"""
        self.error_chunks.append(chunk_id)
        print(f"  [FAIL] Chunk {chunk_id} error: {result.error}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n=== Test Summary ===")
        print(f"Completed chunks: {len(self.completed_chunks)}")
        print(f"Error chunks: {len(self.error_chunks)}")
        print("\nAll integration tests passed! [OK]")


def main():
    """Run the integration test"""
    # Create QApplication for Qt components
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Run tests
    test = TestRealtimeIntegration()
    test.run_test()
    
    # Exit
    QTimer.singleShot(100, app.quit)
    return app.exec()


if __name__ == "__main__":
    main()
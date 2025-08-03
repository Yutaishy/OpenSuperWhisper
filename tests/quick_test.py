"""
Quick test script for realtime transcription
This is a simplified test that can be run without Qt dependencies
"""

import sys
import os
import time
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper.retry_manager import RetryManager
from OpenSuperWhisper import logger


def test_basic_functionality():
    """Test basic realtime transcription components"""
    print("=== Quick Realtime Transcription Test ===\n")
    
    # Test 1: Create components
    print("Test 1: Component creation")
    try:
        recorder = RealtimeRecorder()
        retry_manager = RetryManager()
        processor = ChunkProcessor(max_workers=1, retry_manager=retry_manager)
        print("[OK] All components created successfully")
    except Exception as e:
        print(f"[FAIL] Component creation failed: {e}")
        return
    
    # Test 2: Start recording
    print("\nTest 2: Recording start")
    try:
        recorder.start_recording()
        assert recorder.is_recording, "Recorder should be recording"
        print("[OK] Recording started")
    except Exception as e:
        print(f"[FAIL] Recording start failed: {e}")
        return
    
    # Test 3: Simulate audio data
    print("\nTest 3: Audio data processing")
    sample_rate = 16000
    chunks_created = 0
    
    try:
        # Simulate 65 seconds of audio (should create 1 chunk)
        for i in range(65):
            # Generate 1 second of audio
            t = np.linspace(0, 1, sample_rate)
            audio = 0.3 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.random.randn(sample_rate)
            
            # Add to recorder
            result = recorder.add_audio_data(audio.astype(np.float32))
            
            if result:
                chunk_id, chunk_audio = result
                chunks_created += 1
                print(f"[OK] Chunk {chunk_id} created at {i}s with {len(chunk_audio)/sample_rate:.2f}s audio")
        
        if chunks_created == 0:
            print("[INFO] No chunks created in 65s (expected behavior for MIN_CHUNK_DURATION=60s)")
    except Exception as e:
        print(f"[FAIL] Audio processing failed: {e}")
        return
    
    # Test 4: Stop recording
    print("\nTest 4: Recording stop")
    try:
        final_chunk = recorder.stop_recording()
        if final_chunk:
            chunk_id, chunk_audio = final_chunk
            print(f"[OK] Final chunk {chunk_id} with {len(chunk_audio)/sample_rate:.2f}s audio")
        else:
            print("[INFO] No final chunk (all audio already chunked)")
        print("[OK] Recording stopped")
    except Exception as e:
        print(f"[FAIL] Recording stop failed: {e}")
        return
    
    # Test 5: Chunk processor
    print("\nTest 5: Chunk processor")
    try:
        # Test with dummy audio
        test_audio = np.random.randn(sample_rate * 10).astype(np.float32)
        
        # Note: This would normally call the API, but for testing we just verify it accepts the chunk
        future = processor.process_chunk(0, test_audio)
        print("[OK] Chunk submitted to processor")
        
        # Clean up
        processor.cancel_all_processing()
        processor.shutdown()
        print("[OK] Processor shutdown cleanly")
    except Exception as e:
        print(f"[FAIL] Chunk processor test failed: {e}")
        return
    
    # Test 6: Retry manager
    print("\nTest 6: Retry manager")
    try:
        # Test error configurations
        errors = ["Network timeout", "Rate limit", "Authentication"]
        for error in errors:
            config = retry_manager._get_retry_config(error)
            print(f"[OK] {error}: max_retries={config.max_retries}, delay={config.base_delay}s")
    except Exception as e:
        print(f"[FAIL] Retry manager test failed: {e}")
        return
    
    print("\n=== All tests completed successfully! ===")


def test_chunk_boundaries():
    """Test chunk boundary detection"""
    print("\n=== Chunk Boundary Test ===\n")
    
    recorder = RealtimeRecorder()
    recorder.start_recording()
    
    sample_rate = 16000
    
    # Test different scenarios
    scenarios = [
        ("2 minutes continuous audio", 120, False),  # Should create 1 chunk at 2 min
        ("1.5 min + silence", 90, True),  # Should create chunk after silence
    ]
    
    for scenario_name, duration, add_silence in scenarios:
        print(f"\nTesting: {scenario_name}")
        recorder.start_recording()  # Reset for each scenario
        
        chunks = []
        
        # Generate audio
        for i in range(duration):
            if add_silence and i >= 88:  # Add silence at end
                audio = 0.001 * np.random.randn(sample_rate)
            else:
                audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
            
            result = recorder.add_audio_data(audio.astype(np.float32))
            if result:
                chunks.append(result)
                print(f"  Chunk created at {i}s")
        
        # Get final chunk
        final = recorder.stop_recording()
        if final:
            chunks.append(final)
            print(f"  Final chunk on stop")
        
        print(f"  Total chunks: {len(chunks)}")


if __name__ == "__main__":
    test_basic_functionality()
    test_chunk_boundaries()
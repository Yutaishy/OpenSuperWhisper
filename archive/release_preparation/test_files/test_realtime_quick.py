"""
Quick test for realtime transcription functionality
Tests the core components without full UI
"""

import sys
import os
import numpy as np
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper import logger

def test_realtime_components():
    """Test realtime components without GUI"""
    print("=== Quick Realtime Functionality Test ===\n")
    
    # Test 1: Create components
    print("Test 1: Creating realtime components...")
    try:
        recorder = RealtimeRecorder()
        processor = ChunkProcessor()
        print("[OK] Components created successfully")
    except Exception as e:
        print(f"[FAIL] Component creation failed: {e}")
        return False
    
    # Test 2: Start recording
    print("\nTest 2: Starting recording...")
    try:
        recorder.start_recording()
        assert recorder.is_recording, "Recorder should be recording"
        print("[OK] Recording started")
    except Exception as e:
        print(f"[FAIL] Recording start failed: {e}")
        return False
    
    # Test 3: Simulate audio data
    print("\nTest 3: Simulating 70 seconds of audio...")
    sample_rate = 16000
    chunk_created = False
    
    try:
        # Simulate 70 seconds to trigger chunk creation
        for i in range(70):
            # Generate 1 second of audio
            audio_data = 0.1 * np.random.randn(sample_rate).astype(np.float32)
            result = recorder.add_audio_data(audio_data)
            
            if result:
                chunk_id, chunk_audio = result
                chunk_created = True
                print(f"[OK] Chunk {chunk_id} created with {len(chunk_audio)/sample_rate:.1f}s audio")
                break
        
        if not chunk_created:
            print(f"[INFO] No chunk created yet (expected after 60s minimum)")
    except Exception as e:
        print(f"[FAIL] Audio simulation failed: {e}")
        return False
    
    # Test 4: Check chunk processor
    print("\nTest 4: Checking chunk processor...")
    try:
        # Check actual attributes from chunk_processor.py
        assert hasattr(processor, 'chunk_results'), "chunk_results attribute missing"
        assert hasattr(processor, 'executor'), "executor missing"
        assert hasattr(processor, 'api_futures'), "api_futures missing"
        assert hasattr(processor, 'processing_chunks'), "processing_chunks missing"
        print(f"  Chunk results dict: {type(processor.chunk_results)}")
        print(f"  Worker pool: {type(processor.executor)}")
        print(f"  API futures list: {type(processor.api_futures)}")
        print("[OK] Chunk processor is ready")
    except Exception as e:
        print(f"[FAIL] Chunk processor check failed: {e}")
        return False
    
    # Test 5: Stop recording
    print("\nTest 5: Stopping recording...")
    try:
        final_chunk = recorder.stop_recording()
        if final_chunk:
            chunk_id, chunk_audio = final_chunk
            print(f"[OK] Final chunk {chunk_id} with {len(chunk_audio)/sample_rate:.1f}s audio")
        else:
            print("[OK] Recording stopped (no final chunk)")
    except Exception as e:
        print(f"[FAIL] Recording stop failed: {e}")
        return False
    
    # Test 6: Verify realtime mode attributes
    print("\nTest 6: Verifying realtime mode attributes...")
    try:
        # Check key attributes
        assert hasattr(recorder, 'MIN_CHUNK_DURATION'), "MIN_CHUNK_DURATION missing"
        assert hasattr(recorder, 'MAX_CHUNK_DURATION'), "MAX_CHUNK_DURATION missing"
        assert hasattr(recorder, 'SILENCE_CHECK_START'), "SILENCE_CHECK_START missing"
        assert recorder.MIN_CHUNK_DURATION == 60.0, f"MIN_CHUNK_DURATION should be 60.0, got {recorder.MIN_CHUNK_DURATION}"
        assert recorder.MAX_CHUNK_DURATION == 120.0, f"MAX_CHUNK_DURATION should be 120.0, got {recorder.MAX_CHUNK_DURATION}"
        print("[OK] All realtime attributes verified")
    except Exception as e:
        print(f"[FAIL] Attribute verification failed: {e}")
        return False
    
    print("\n=== All tests passed! ===")
    print("\nRealtime transcription components are working correctly.")
    print("Note: This test doesn't require API keys or actual transcription.")
    return True

if __name__ == "__main__":
    success = test_realtime_components()
    sys.exit(0 if success else 1)
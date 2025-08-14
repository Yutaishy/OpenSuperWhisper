"""
Test chunk creation with proper time simulation
"""

import sys
import os
import numpy as np
import time
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper import logger

def test_chunk_creation():
    """Test chunk creation with simulated time"""
    print("=== Chunk Creation Test ===\n")
    
    # Create recorder
    recorder = RealtimeRecorder(sample_rate=16000)
    processor = ChunkProcessor(max_workers=1)
    
    # Start recording
    recorder.start_recording()
    print(f"Recording started at simulated time 0")
    
    sample_rate = 16000
    chunks_created = []
    
    # Simulate time progression
    simulated_time = recorder.recording_start_time
    
    print("\nSimulating audio input with proper time progression...")
    
    # We need to override time.time() for the recorder
    original_time = time.time
    
    try:
        # Generate 150 seconds of audio to ensure chunk creation
        for second in range(150):
            # Update simulated time
            simulated_time = recorder.recording_start_time + second
            
            # Monkey patch time.time to return our simulated time
            time.time = lambda: simulated_time
            
            # Generate 1 second of audio
            if second % 10 < 7:  # 70% speech
                audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
            else:  # 30% silence
                audio = 0.01 * np.random.randn(sample_rate)
            
            audio = audio.astype(np.float32)
            
            # Add to recorder
            result = recorder.add_audio_data(audio)
            
            if result:
                chunk_id, chunk_audio = result
                chunks_created.append((chunk_id, len(chunk_audio)/sample_rate))
                print(f"\n[CHUNK {chunk_id}] Created at {second}s with {len(chunk_audio)/sample_rate:.1f}s audio")
                
                # Process the chunk
                future = processor.process_chunk(chunk_id, chunk_audio)
                print(f"  Submitted for processing")
                
                # Update chunk start time for next chunk
                print(f"  Next chunk starts at {second}s")
            
            # Progress update every 30 seconds
            if (second + 1) % 30 == 0:
                chunk_duration = simulated_time - recorder.chunk_start_time
                print(f"Progress: {second + 1}s elapsed, current chunk duration: {chunk_duration:.1f}s")
        
        # Restore original time function
        time.time = original_time
        
        # Stop recording
        print(f"\nStopping recording at simulated time {150}s...")
        final_result = recorder.stop_recording()
        if final_result:
            chunk_id, chunk_audio = final_result
            chunks_created.append((chunk_id, len(chunk_audio)/sample_rate))
            print(f"[FINAL CHUNK {chunk_id}] {len(chunk_audio)/sample_rate:.1f}s audio")
    
    finally:
        # Always restore time.time
        time.time = original_time
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total chunks created: {len(chunks_created)}")
    for chunk_id, duration in chunks_created:
        print(f"  Chunk {chunk_id}: {duration:.1f}s")
    
    if len(chunks_created) >= 2:
        print("\n[SUCCESS] Chunk boundary detection is working correctly!")
    else:
        print("\n[FAIL] Expected at least 2 chunks for 150s audio")
    
    return len(chunks_created) >= 2

if __name__ == "__main__":
    success = test_chunk_creation()
    sys.exit(0 if success else 1)
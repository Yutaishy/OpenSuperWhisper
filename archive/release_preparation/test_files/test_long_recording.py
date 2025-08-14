"""
Test long recording with multiple chunks
Simulates 10+ minute recording to test chunk management
"""

import sys
import os
import numpy as np
import time
import gc

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper import logger

def test_long_recording():
    """Test long recording with multiple chunks"""
    print("=== Long Recording Test (10+ minutes) ===\n")
    
    # Create recorder and processor
    recorder = RealtimeRecorder(sample_rate=16000)
    processor = ChunkProcessor(max_workers=3)
    
    # Start recording
    recorder.start_recording()
    print(f"Recording started")
    
    sample_rate = 16000
    chunks_created = []
    
    # Simulate time progression
    simulated_time = recorder.recording_start_time
    original_time = time.time
    
    # Total duration: 12 minutes (720 seconds)
    total_duration = 720
    print(f"\nSimulating {total_duration/60:.1f} minutes of audio...")
    
    try:
        for second in range(total_duration):
            # Update simulated time
            simulated_time = recorder.recording_start_time + second
            time.time = lambda: simulated_time
            
            # Generate 1 second of audio with varying patterns
            if second % 300 < 200:  # First 200s of each 5min: mostly speech
                if second % 10 < 8:  # 80% speech
                    audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
                else:  # 20% short silence
                    audio = 0.01 * np.random.randn(sample_rate)
            else:  # Last 100s of each 5min: more silence
                if second % 10 < 3:  # 30% speech
                    audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
                else:  # 70% silence
                    audio = 0.01 * np.random.randn(sample_rate)
            
            audio = audio.astype(np.float32)
            
            # Add to recorder
            result = recorder.add_audio_data(audio)
            
            if result:
                chunk_id, chunk_audio = result
                duration = len(chunk_audio)/sample_rate
                chunks_created.append((chunk_id, duration, second))
                print(f"\n[CHUNK {chunk_id}] Created at {second}s ({second/60:.1f}min)")
                print(f"  Duration: {duration:.1f}s")
                print(f"  Memory usage before GC: {get_memory_usage():.1f}MB")
                
                # Process the chunk
                future = processor.process_chunk(chunk_id, chunk_audio)
                
                # Simulate chunk deletion after processing
                del chunk_audio
                
                # Check if GC should run (every 10 chunks as per docs)
                if (chunk_id + 1) % 10 == 0:
                    gc.collect()
                    print(f"  Garbage collection performed")
                
                print(f"  Memory usage after cleanup: {get_memory_usage():.1f}MB")
            
            # Progress update every minute
            if (second + 1) % 60 == 0:
                minutes = (second + 1) / 60
                chunk_duration = simulated_time - recorder.chunk_start_time
                print(f"\nProgress: {minutes:.0f} minutes elapsed")
                print(f"  Current chunk duration: {chunk_duration:.1f}s")
                print(f"  Total chunks created: {len(chunks_created)}")
                print(f"  Memory usage: {get_memory_usage():.1f}MB")
        
        # Restore original time function
        time.time = original_time
        
        # Stop recording
        print(f"\nStopping recording at {total_duration/60:.1f} minutes...")
        final_result = recorder.stop_recording()
        if final_result:
            chunk_id, chunk_audio = final_result
            duration = len(chunk_audio)/sample_rate
            chunks_created.append((chunk_id, duration, total_duration))
            print(f"[FINAL CHUNK {chunk_id}] Duration: {duration:.1f}s")
    
    finally:
        # Always restore time.time
        time.time = original_time
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total recording time: {total_duration/60:.1f} minutes")
    print(f"Total chunks created: {len(chunks_created)}")
    print("\nChunk details:")
    
    total_audio_duration = 0
    for chunk_id, duration, created_at in chunks_created:
        print(f"  Chunk {chunk_id}: {duration:.1f}s (created at {created_at/60:.1f}min)")
        total_audio_duration += duration
    
    print(f"\nTotal audio duration: {total_audio_duration:.1f}s ({total_audio_duration/60:.1f}min)")
    print(f"Average chunk duration: {total_audio_duration/len(chunks_created):.1f}s")
    
    # Validate results
    expected_chunks = total_duration // 120 + (1 if total_duration % 120 > 0 else 0)
    print(f"\nExpected chunks: ~{expected_chunks}")
    print(f"Actual chunks: {len(chunks_created)}")
    
    if len(chunks_created) >= expected_chunks - 1:
        print("\n[SUCCESS] Long recording handled correctly!")
        return True
    else:
        print("\n[FAIL] Fewer chunks than expected")
        return False

def get_memory_usage():
    """Get current memory usage in MB"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("Installing psutil for memory monitoring...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    success = test_long_recording()
    sys.exit(0 if success else 1)
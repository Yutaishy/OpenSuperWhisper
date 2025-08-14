"""
Debug silence detection and chunk splitting
"""

import sys
import os
import numpy as np
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder

def test_debug_silence():
    """Debug why small chunks are created during silence"""
    print("=== Debug Silence Detection ===\n")
    
    # Create recorder
    recorder = RealtimeRecorder(sample_rate=16000)
    recorder.start_recording()
    
    sample_rate = 16000
    simulated_time = recorder.recording_start_time
    original_time = time.time
    
    try:
        # Generate 210 seconds to trigger silence detection
        # Pattern: 90s speech, 120s silence to trigger priority split
        for second in range(210):
            simulated_time = recorder.recording_start_time + second
            time.time = lambda: simulated_time
            
            # First 90 seconds: mostly speech
            if second < 90:
                if second % 10 < 8:  # 80% speech
                    audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
                else:  # 20% short silence
                    audio = 0.01 * np.random.randn(sample_rate)
            else:
                # After 90 seconds: continuous silence
                audio = 0.005 * np.random.randn(sample_rate)  # Very quiet
            
            audio = audio.astype(np.float32)
            
            # Check status every 10 seconds
            if second % 10 == 0:
                chunk_duration = simulated_time - recorder.chunk_start_time
                print(f"Time: {second}s, Chunk duration: {chunk_duration:.1f}s")
                
                # Check if we're in silence detection range
                if chunk_duration >= recorder.SILENCE_CHECK_START:
                    # Check current audio buffer size
                    if recorder.current_chunk:
                        total_samples = sum(len(chunk) for chunk in recorder.current_chunk)
                        total_duration = total_samples / sample_rate
                        print(f"  Audio buffer: {total_duration:.1f}s ({total_samples} samples)")
                    
                    # Check if silence would be detected
                    if recorder.detect_silence(recorder.MIN_SILENCE_DURATION + 0.8):
                        print(f"  [SILENCE DETECTED] Would trigger split")
            
            # Add audio
            result = recorder.add_audio_data(audio)
            
            if result:
                chunk_id, chunk_audio = result
                duration = len(chunk_audio) / sample_rate
                print(f"\n[CHUNK {chunk_id}] Created at {second}s")
                print(f"  Chunk duration: {duration:.1f}s")
                print(f"  Expected duration: ~{second - (chunk_id * 120):.1f}s")
                
                # Debug: Check what happened in _find_optimal_split_point
                # Let's manually check the audio buffer that was combined
                if recorder.current_chunk:
                    print(f"  Note: Some audio might remain in buffer for next chunk")
                
                if duration < 60:  # Unexpected small chunk
                    print(f"  [WARNING] Small chunk detected!")
                    print(f"  This suggests _find_optimal_split_point found silence early in buffer")
                print()
    
    finally:
        time.time = original_time
    
    # Final chunk
    final = recorder.stop_recording()
    if final:
        chunk_id, chunk_audio = final
        print(f"[FINAL CHUNK {chunk_id}] Duration: {len(chunk_audio)/sample_rate:.1f}s")

if __name__ == "__main__":
    test_debug_silence()
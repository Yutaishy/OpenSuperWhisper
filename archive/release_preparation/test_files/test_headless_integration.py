"""
Headless integration test - tests all components without GUI
"""

import sys
import os
import time
import numpy as np
import threading
from unittest.mock import Mock, MagicMock, patch
import concurrent.futures

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper.retry_manager import RetryManager
from OpenSuperWhisper.cancel_handler import CancelHandler
from OpenSuperWhisper import logger

def test_headless_integration():
    """Test complete system without GUI"""
    print("=== Headless Integration Test ===\n")
    
    # 1. Initialize components
    print("1. Initializing components...")
    recorder = RealtimeRecorder(sample_rate=16000)
    processor = ChunkProcessor(
        max_workers=3,
        asr_model="whisper-1",
        chat_model="gpt-4o-mini",
        format_enabled=True
    )
    retry_manager = RetryManager()
    cancel_handler = CancelHandler()
    
    print("[OK] All components initialized")
    print(f"  Recorder: {recorder}")
    print(f"  Processor: {processor}")
    print(f"  Retry Manager: {retry_manager}")
    print(f"  Cancel Handler: {cancel_handler}")
    
    # 2. Mock API services
    print("\n2. Mocking API services...")
    processor.asr_api = Mock()
    processor.formatter_api = Mock()
    
    # Create more realistic mock responses
    def mock_transcribe(audio_data):
        # Simulate processing time
        time.sleep(0.1)
        chunk_duration = len(audio_data) / 16000
        return {
            "text": f"これはチャンク音声の内容です。約{chunk_duration:.0f}秒間の録音データを処理しました。"
        }
    
    def mock_format(text, model="gpt-4o-mini"):
        # Simulate processing time
        time.sleep(0.05)
        return {
            "formatted_text": text.replace("。", "。\n"),
            "model": model
        }
    
    processor.asr_api.transcribe_audio.side_effect = mock_transcribe
    processor.formatter_api.format_text.side_effect = mock_format
    
    print("[OK] API mocks configured")
    
    # 3. Start recording
    print("\n3. Starting recording session...")
    recorder.start_recording()
    
    sample_rate = 16000
    chunks_created = []
    processing_results = []
    
    # Time simulation
    original_time = time.time
    start_time = time.time()
    
    # 4. Simulate 3 minute recording
    print("\n4. Simulating 3 minute recording...")
    duration_seconds = 180
    
    try:
        for second in range(duration_seconds):
            # Update simulated time
            simulated_time = start_time + second
            time.time = lambda: simulated_time
            
            # Generate audio pattern
            if second % 120 < 90:  # First 90s: mostly speech
                if second % 10 < 8:
                    audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
                else:
                    audio = 0.02 * np.random.randn(sample_rate)
            else:  # Last 30s: more silence
                if second % 10 < 3:
                    audio = 0.2 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
                else:
                    audio = 0.01 * np.random.randn(sample_rate)
            
            audio = audio.astype(np.float32)
            
            # Add to recorder
            result = recorder.add_audio_data(audio)
            
            if result:
                chunk_id, chunk_audio = result
                duration = len(chunk_audio) / sample_rate
                chunks_created.append((chunk_id, duration))
                
                print(f"\n[CHUNK {chunk_id}] Created at {second}s")
                print(f"  Duration: {duration:.1f}s")
                
                # Process chunk
                future = processor.process_chunk(chunk_id, chunk_audio)
                print(f"  Submitted for processing")
                
                # Start background thread to check result
                def check_result(cid, fut):
                    try:
                        result = fut.result(timeout=5)
                        processing_results.append((cid, result))
                        print(f"  [PROCESSED] Chunk {cid} completed")
                    except Exception as e:
                        print(f"  [ERROR] Chunk {cid} failed: {e}")
                
                threading.Thread(target=check_result, args=(chunk_id, future)).start()
            
            # Progress update
            if (second + 1) % 30 == 0:
                print(f"\nProgress: {(second + 1)/60:.1f} minutes")
                print(f"  Chunks created: {len(chunks_created)}")
                print(f"  Chunks processed: {len(processing_results)}")
                print(f"  Active futures: {len(processor.api_futures)}")
        
        # Restore time
        time.time = original_time
        
        # 5. Stop recording
        print(f"\n5. Stopping recording...")
        final_chunk = recorder.stop_recording()
        if final_chunk:
            chunk_id, chunk_audio = final_chunk
            duration = len(chunk_audio) / sample_rate
            chunks_created.append((chunk_id, duration))
            print(f"[FINAL CHUNK {chunk_id}] Duration: {duration:.1f}s")
            
            # Process final chunk
            future = processor.process_chunk(chunk_id, chunk_audio)
            try:
                result = future.result(timeout=5)
                processing_results.append((chunk_id, result))
                print(f"  [PROCESSED] Final chunk completed")
            except Exception as e:
                print(f"  [ERROR] Final chunk failed: {e}")
        
        # 6. Wait for all processing to complete
        print("\n6. Waiting for all processing to complete...")
        time.sleep(2)
        
        # 7. Check retry manager
        print("\n7. Checking retry manager...")
        # RetryManager doesn't have check_retries method
        print(f"  Retry queue size: {len(retry_manager.retry_queue)}")
        print(f"  Retry counts: {len(retry_manager.retry_counts)}")
        
        # 8. Final results
        print("\n8. Final Results:")
        print(f"  Total recording time: {duration_seconds/60:.1f} minutes")
        print(f"  Total chunks created: {len(chunks_created)}")
        print(f"  Total chunks processed: {len(processing_results)}")
        
        print("\n  Chunk details:")
        total_audio = 0
        for chunk_id, duration in chunks_created:
            print(f"    Chunk {chunk_id}: {duration:.1f}s")
            total_audio += duration
        
        print(f"\n  Total audio duration: {total_audio:.1f}s ({total_audio/60:.1f}min)")
        print(f"  Average chunk duration: {total_audio/len(chunks_created):.1f}s")
        
        # 9. Verify processing results
        print("\n9. Verifying processing results:")
        for chunk_id, result in processing_results[:3]:  # Show first 3
            if result and hasattr(result, 'raw_text') and result.raw_text:
                trans_text = result.raw_text[:50]
                print(f"  Chunk {chunk_id}: {trans_text}...")
            elif result and hasattr(result, 'status'):
                print(f"  Chunk {chunk_id}: Status={result.status}")
        
        # 10. Memory check
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"\n10. Final memory usage: {memory_mb:.1f}MB")
        except:
            pass
        
        # Success criteria
        success = (
            len(chunks_created) >= 2 and
            len(processing_results) >= len(chunks_created) - 1 and
            all(duration > 60 for _, duration in chunks_created[:-1])
        )
        
        if success:
            print("\n[SUCCESS] All components working correctly!")
        else:
            print("\n[FAIL] Some issues detected")
        
        return success
    
    finally:
        # Always restore time
        time.time = original_time
        # Cleanup - processor and cancel_handler don't have cleanup methods
        print("\n[Cleanup completed]")

if __name__ == "__main__":
    # Install psutil if needed
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "-q"])
    
    success = test_headless_integration()
    sys.exit(0 if success else 1)
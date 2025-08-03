"""
Performance profiler for realtime transcription
Analyzes performance metrics and suggests optimizations
"""

import cProfile
import os
import pstats
import sys
import time
from datetime import datetime
from io import StringIO

import numpy as np
import psutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper.realtime_recorder import RealtimeRecorder


class PerformanceProfiler:
    """Profile performance of realtime transcription components"""

    def __init__(self):
        self.metrics = {
            'chunk_processing_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'audio_buffer_sizes': [],
            'api_response_times': []
        }
        self.process = psutil.Process()

    def profile_chunk_recording(self, duration_minutes: float = 5.0):
        """Profile chunk recording performance"""
        print(f"\n=== Profiling Chunk Recording ({duration_minutes} minutes) ===")

        recorder = RealtimeRecorder()
        sample_rate = 16000
        chunks_created = 0

        # Start profiling
        profiler = cProfile.Profile()
        profiler.enable()

        # Record start metrics
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        # Start recording
        recorder.start_recording()

        # Simulate audio recording
        total_samples = int(duration_minutes * 60 * sample_rate)
        chunk_size = sample_rate  # 1 second chunks

        for i in range(0, total_samples, chunk_size):
            # Generate audio data
            if (i // sample_rate) % 10 < 7:  # Speech pattern
                audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, chunk_size))
            else:  # Silence
                audio = 0.001 * np.random.randn(chunk_size)

            # Add to recorder
            result = recorder.add_audio_data(audio.astype(np.float32))

            if result:
                chunks_created += 1
                chunk_id, chunk_audio = result

                # Measure metrics
                self.metrics['audio_buffer_sizes'].append(len(chunk_audio))
                self.metrics['memory_usage'].append(
                    self.process.memory_info().rss / 1024 / 1024
                )
                self.metrics['cpu_usage'].append(
                    self.process.cpu_percent(interval=0.1)
                )

        # Stop recording
        recorder.stop_recording()

        # Stop profiling
        profiler.disable()

        # Calculate results
        elapsed_time = time.time() - start_time
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_increase = end_memory - start_memory

        # Print results
        print("\nRecording Performance:")
        print(f"- Duration: {elapsed_time:.2f}s (simulated {duration_minutes} minutes)")
        print(f"- Chunks created: {chunks_created}")
        print(f"- Memory increase: {memory_increase:.2f} MB")
        print(f"- Avg CPU usage: {np.mean(self.metrics['cpu_usage']):.1f}%")
        print(f"- Avg buffer size: {np.mean(self.metrics['audio_buffer_sizes'])/sample_rate:.2f}s")

        # Show profiling stats
        self._print_profile_stats(profiler, "Recording")

    def profile_chunk_processing(self, num_chunks: int = 10):
        """Profile chunk processing performance"""
        print(f"\n=== Profiling Chunk Processing ({num_chunks} chunks) ===")

        processor = ChunkProcessor(max_workers=3)
        sample_rate = 16000

        # Create test chunks
        test_chunks = []
        for i in range(num_chunks):
            # Create 60-second audio chunk
            audio = np.random.randn(60 * sample_rate).astype(np.float32)
            test_chunks.append((i, audio))

        # Start profiling
        profiler = cProfile.Profile()
        profiler.enable()

        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024

        # Process chunks
        futures = []
        for chunk_id, audio in test_chunks:
            # Measure submission time
            submit_start = time.time()
            future = processor.process_chunk(chunk_id, audio)
            submit_time = time.time() - submit_start

            if future:
                futures.append(future)

            # Record metrics
            self.metrics['memory_usage'].append(
                self.process.memory_info().rss / 1024 / 1024
            )

        # Wait for completion (with timeout)
        print("Waiting for chunk processing...")
        max_wait = 30  # 30 seconds timeout
        wait_start = time.time()

        while time.time() - wait_start < max_wait:
            completed = sum(1 for f in futures if f.done())
            if completed == len(futures):
                break
            time.sleep(0.5)

        # Stop profiling
        profiler.disable()

        # Calculate results
        elapsed_time = time.time() - start_time
        end_memory = self.process.memory_info().rss / 1024 / 1024
        memory_increase = end_memory - start_memory
        completed_count = sum(1 for f in futures if f.done())

        print("\nProcessing Performance:")
        print(f"- Total time: {elapsed_time:.2f}s")
        print(f"- Chunks completed: {completed_count}/{num_chunks}")
        print(f"- Memory increase: {memory_increase:.2f} MB")
        print(f"- Avg memory per chunk: {memory_increase/num_chunks:.2f} MB")

        # Show profiling stats
        self._print_profile_stats(profiler, "Processing")

        # Cleanup
        processor.shutdown()

    def profile_memory_optimization(self):
        """Profile memory optimization with garbage collection"""
        print("\n=== Profiling Memory Optimization ===")

        processor = ChunkProcessor(max_workers=1)
        sample_rate = 16000

        memory_before_gc = []
        memory_after_gc = []

        # Process 20 chunks to trigger GC
        for i in range(20):
            # Create chunk
            audio = np.random.randn(120 * sample_rate).astype(np.float32)  # 2-minute chunk
            processor.processing_chunks[i] = audio

            # Measure memory before deletion
            memory_before = self.process.memory_info().rss / 1024 / 1024

            # Simulate chunk completion
            del processor.processing_chunks[i]
            processor.chunks_deleted += 1

            # Check if GC triggered
            if processor.chunks_deleted % 10 == 0:
                memory_before_gc.append(memory_before)
                # GC happens here in real code
                import gc
                gc.collect()
                memory_after = self.process.memory_info().rss / 1024 / 1024
                memory_after_gc.append(memory_after)
                print(f"  GC at chunk {i+1}: {memory_before:.1f} MB → {memory_after:.1f} MB "
                      f"(freed {memory_before - memory_after:.1f} MB)")

        # Results
        if memory_before_gc and memory_after_gc:
            avg_freed = np.mean([b - a for b, a in zip(memory_before_gc, memory_after_gc, strict=False)])
            print("\nMemory Optimization Results:")
            print(f"- Average memory freed per GC: {avg_freed:.2f} MB")
            print("- GC triggered every 10 chunks as expected")

        processor.shutdown()

    def analyze_bottlenecks(self):
        """Analyze performance bottlenecks and suggest optimizations"""
        print("\n=== Performance Analysis & Recommendations ===")

        # Analyze metrics
        if self.metrics['cpu_usage']:
            avg_cpu = np.mean(self.metrics['cpu_usage'])
            max_cpu = np.max(self.metrics['cpu_usage'])

            print("\nCPU Usage:")
            print(f"- Average: {avg_cpu:.1f}%")
            print(f"- Peak: {max_cpu:.1f}%")

            if avg_cpu > 50:
                print("[WARNING]  High CPU usage detected")
                print("   Recommendations:")
                print("   - Consider reducing audio processing frequency")
                print("   - Optimize numpy operations with vectorization")

        if self.metrics['memory_usage']:
            memory_growth = self.metrics['memory_usage'][-1] - self.metrics['memory_usage'][0]

            print("\nMemory Usage:")
            print(f"- Growth: {memory_growth:.2f} MB")
            print(f"- Peak: {np.max(self.metrics['memory_usage']):.2f} MB")

            if memory_growth > 100:
                print("[WARNING]  High memory growth detected")
                print("   Recommendations:")
                print("   - Ensure audio buffers are properly released")
                print("   - Consider more frequent garbage collection")

        if self.metrics['audio_buffer_sizes']:
            avg_buffer = np.mean(self.metrics['audio_buffer_sizes']) / 16000

            print("\nAudio Buffers:")
            print(f"- Average size: {avg_buffer:.2f}s")

            if avg_buffer > 90:
                print("[WARNING]  Large audio buffers detected")
                print("   Recommendations:")
                print("   - Consider more aggressive silence detection")
                print("   - Reduce MAX_CHUNK_DURATION if appropriate")

        print("\n[OK] Optimization Suggestions:")
        print("1. Use numpy's in-place operations to reduce memory allocation")
        print("2. Implement audio compression for network transmission")
        print("3. Consider using audio streaming instead of chunk accumulation")
        print("4. Profile API calls to identify network bottlenecks")
        print("5. Implement adaptive chunk sizing based on speech patterns")

    def _print_profile_stats(self, profiler, title: str):
        """Print profiling statistics"""
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions

        print(f"\n{title} Profile (Top 10 Functions):")
        print(s.getvalue())

    def run_full_profile(self):
        """Run complete performance profile"""
        print("=== OpenSuperWhisper Realtime Performance Profiler ===")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Profile each component
        self.profile_chunk_recording(duration_minutes=2.0)
        self.profile_chunk_processing(num_chunks=5)
        self.profile_memory_optimization()

        # Analyze and recommend
        self.analyze_bottlenecks()

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Run performance profiling"""
    profiler = PerformanceProfiler()
    profiler.run_full_profile()


if __name__ == "__main__":
    main()


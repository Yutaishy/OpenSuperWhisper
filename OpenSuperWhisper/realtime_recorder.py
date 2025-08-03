"""
Realtime Recorder Module
Handles chunk-based recording with overlap for real-time transcription
"""

import time
from collections import deque

import numpy as np

from . import logger


class RealtimeRecorder:
    """Manages real-time chunk-based audio recording with overlap"""

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the realtime recorder

        Args:
            sample_rate: Audio sample rate (default: 16000 Hz for Whisper)
        """
        self.sample_rate = sample_rate
        self.current_chunk: list[np.ndarray] = []
        self.chunk_start_time: float = 0.0
        self.chunk_id: int = 0
        self.recording_start_time: float = 0.0
        self.is_recording: bool = False
        self.overlap_buffer: np.ndarray | None = None

        # Chunk timing parameters (in seconds)
        self.MIN_CHUNK_DURATION = 60.0    # 1 minute minimum
        self.SILENCE_CHECK_START = 90.0  # Start checking silence at 1.5 minutes
        self.PRIORITY_SPLIT_TIME = 110.0  # Priority split at 1m50s
        self.MAX_CHUNK_DURATION = 120.0   # Force split at 2 minutes

        # Silence detection parameters
        self.SILENCE_THRESHOLD = 0.01     # Amplitude threshold for silence
        self.MIN_SILENCE_DURATION = 1.5   # Minimum silence duration for split
        self.SHORT_SILENCE_DURATION = 0.5 # Short silence for priority split

        # Buffer for silence detection
        self.silence_buffer_size = int(2.5 * sample_rate)  # 2.5 seconds buffer
        self.recent_audio = deque(maxlen=self.silence_buffer_size)

        logger.logger.info("RealtimeRecorder initialized")

    def start_recording(self) -> None:
        """Start a new recording session"""
        self.is_recording = True
        self.recording_start_time = time.time()
        self.chunk_start_time = self.recording_start_time
        self.chunk_id = 0
        self.current_chunk = []
        self.overlap_buffer = None
        logger.logger.info("Started realtime recording session")

    def stop_recording(self) -> tuple[int, np.ndarray] | None:
        """
        Stop recording and return final chunk if any

        Returns:
            Tuple of (chunk_id, audio_data) if there's remaining audio, None otherwise
        """
        self.is_recording = False

        # Return remaining audio as final chunk
        if self.current_chunk:
            audio_data = self._combine_chunk_data()
            chunk_id = self.chunk_id
            logger.logger.info(f"Final chunk {chunk_id} with {len(audio_data)/self.sample_rate:.2f}s")
            return (chunk_id, audio_data)

        return None

    def add_audio_data(self, audio_data: np.ndarray) -> tuple[int, np.ndarray] | None:
        """
        Add audio data to current chunk and check if chunk boundary reached

        Args:
            audio_data: New audio samples to add

        Returns:
            Tuple of (chunk_id, audio_data) if chunk is ready, None otherwise
        """
        if not self.is_recording:
            return None

        # Add to current chunk
        self.current_chunk.append(audio_data.copy())

        # Update recent audio buffer for silence detection
        self.recent_audio.extend(audio_data)

        # Check chunk boundary
        current_time = time.time()
        if self.check_chunk_boundary(current_time):
            return self._finalize_current_chunk(current_time)

        return None

    def check_chunk_boundary(self, current_time: float) -> bool:
        """
        Check if current chunk should be finalized based on timing and silence

        Args:
            current_time: Current timestamp

        Returns:
            True if chunk should be finalized
        """
        chunk_duration = current_time - self.chunk_start_time

        # Under minimum duration: continue recording
        if chunk_duration < self.MIN_CHUNK_DURATION:
            return False

        # Over maximum duration: force split
        if chunk_duration >= self.MAX_CHUNK_DURATION:
            logger.logger.info(f"Force split at {chunk_duration:.1f}s")
            return True

        # Between 1m30s and 2m: check for silence
        if chunk_duration >= self.SILENCE_CHECK_START:
            # Calculate effective silence duration considering overlap
            overlap_duration = self.calculate_overlap_duration("ja")
            effective_silence_duration = self.MIN_SILENCE_DURATION + overlap_duration

            if self.detect_silence(effective_silence_duration):
                logger.logger.info(f"Silence detected at {chunk_duration:.1f}s")
                return True

        # After 1m50s: check for short silence
        if chunk_duration >= self.PRIORITY_SPLIT_TIME:
            if self.detect_silence(self.SHORT_SILENCE_DURATION):
                logger.logger.info(f"Short silence detected at {chunk_duration:.1f}s")
                return True

        return False

    def detect_silence(self, duration: float) -> bool:
        """
        Detect if recent audio contains silence of specified duration

        Args:
            duration: Required silence duration in seconds

        Returns:
            True if silence detected
        """
        if not self.recent_audio:
            return False

        # Convert deque to numpy array for analysis
        audio_array = np.array(self.recent_audio)
        required_samples = int(duration * self.sample_rate)

        if len(audio_array) < required_samples:
            return False

        # Check the most recent samples
        recent_samples = audio_array[-required_samples:]

        # Calculate RMS (Root Mean Square) for better silence detection
        rms = np.sqrt(np.mean(recent_samples ** 2))

        return rms < self.SILENCE_THRESHOLD

    def calculate_overlap_duration(self, language: str = "ja") -> float:
        """
        Calculate overlap duration based on language

        Args:
            language: Language code ("ja", "en", etc.)

        Returns:
            Overlap duration in seconds
        """
        overlap_durations = {
            "ja": 0.8,  # Japanese: consider phrases
            "en": 0.5,  # English: consider words
            "default": 0.6
        }
        return overlap_durations.get(language, overlap_durations["default"])

    def _finalize_current_chunk(self, current_time: float) -> tuple[int, np.ndarray]:
        """
        Finalize current chunk and prepare for next one

        Args:
            current_time: Current timestamp

        Returns:
            Tuple of (chunk_id, audio_data)
        """
        # Combine all audio data in current chunk
        audio_data = self._combine_chunk_data()

        # Calculate chunk duration to determine split strategy
        chunk_duration = current_time - self.chunk_start_time

        # Find optimal split point
        # Pass chunk duration to help determine split strategy
        split_point = self._find_optimal_split_point(audio_data, chunk_duration)

        # Create chunk with overlap
        chunk_data, next_start_data = self.create_chunk_with_overlap(
            audio_data, 0, split_point
        )

        # Save current chunk info
        current_chunk_id = self.chunk_id

        # Prepare for next chunk
        self.chunk_id += 1
        self.chunk_start_time = current_time
        self.current_chunk = []

        # Add overlap data to next chunk
        if next_start_data is not None:
            self.current_chunk.append(next_start_data)

        logger.logger.info(
            f"Finalized chunk {current_chunk_id}: "
            f"{len(chunk_data)/self.sample_rate:.2f}s of audio"
        )

        return (current_chunk_id, chunk_data)

    def create_chunk_with_overlap(
        self,
        audio_data: np.ndarray,
        start_idx: int,
        end_idx: int
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """
        Create chunk with overlap for context continuity

        Args:
            audio_data: Full audio data
            start_idx: Start index
            end_idx: End index (split point)

        Returns:
            Tuple of (chunk_data, overlap_data_for_next_chunk)
        """
        overlap_duration = self.calculate_overlap_duration("ja")
        overlap_samples = int(overlap_duration * self.sample_rate)

        # Main chunk data
        chunk_data = audio_data[start_idx:end_idx]

        # Add overlap at the end if not the last chunk
        if end_idx + overlap_samples <= len(audio_data):
            # Include overlap in current chunk
            chunk_with_overlap = audio_data[start_idx:end_idx + overlap_samples]
            # Overlap data for next chunk
            next_overlap = audio_data[max(start_idx, end_idx - overlap_samples):end_idx + overlap_samples]
            return chunk_with_overlap, next_overlap
        else:
            # Last chunk, no overlap needed
            return chunk_data, None

    def _combine_chunk_data(self) -> np.ndarray:
        """Combine all audio arrays in current chunk into single array"""
        if not self.current_chunk:
            return np.array([], dtype=np.float32)

        return np.concatenate(self.current_chunk)

    def _find_optimal_split_point(self, audio_data: np.ndarray, chunk_duration: float = None) -> int:
        """
        Find optimal split point considering phoneme boundaries

        Args:
            audio_data: Audio data to analyze
            chunk_duration: Current chunk duration in seconds

        Returns:
            Index of optimal split point
        """
        audio_duration = len(audio_data) / self.sample_rate

        # If chunk was triggered by silence detection (90s+),
        # we want to use the full audio length as the split point
        if chunk_duration and chunk_duration >= self.SILENCE_CHECK_START:
            # For silence-triggered splits, use the end of the audio
            # This prevents creating tiny chunks when silence is detected
            return len(audio_data)

        # For force-split at MAX_CHUNK_DURATION
        if audio_duration >= self.MAX_CHUNK_DURATION - 1:
            # Use the end of the audio as target
            target_samples = len(audio_data)
        else:
            # Otherwise use 2 minutes as target
            target_samples = int(2.0 * self.sample_rate)

        search_window = int(0.5 * self.sample_rate)   # ±0.5 seconds

        # If audio is shorter than target, use full length
        if len(audio_data) <= target_samples:
            return len(audio_data)

        # Define search range
        start_search = max(0, target_samples - search_window)
        end_search = min(len(audio_data), target_samples + search_window)

        # Priority 1: Look for 1.5+ second silence
        silence_threshold = self.SILENCE_THRESHOLD
        long_silence_samples = int(1.5 * self.sample_rate)

        best_silence_pos = self._find_silence_window(
            audio_data[start_search:end_search],
            long_silence_samples,
            silence_threshold
        )

        if best_silence_pos >= 0:
            return start_search + best_silence_pos + (long_silence_samples // 2)

        # Priority 2: Look for 0.5+ second silence
        short_silence_samples = int(0.5 * self.sample_rate)
        best_silence_pos = self._find_silence_window(
            audio_data[start_search:end_search],
            short_silence_samples,
            silence_threshold
        )

        if best_silence_pos >= 0:
            return start_search + best_silence_pos + (short_silence_samples // 2)

        # Priority 3: Find minimum amplitude point
        min_amp_pos = self._find_minimum_amplitude(audio_data[start_search:end_search])
        if min_amp_pos >= 0:
            return start_search + min_amp_pos

        # Priority 4: Find zero crossing point
        zero_cross_pos = self._find_zero_crossing(audio_data[start_search:end_search])
        if zero_cross_pos >= 0:
            return start_search + zero_cross_pos

        # Fallback: Use target time
        return target_samples

    def _find_silence_window(self, audio_data: np.ndarray, window_size: int,
                           threshold: float) -> int:
        """Find position of silence window of given size"""
        if len(audio_data) < window_size:
            return -1

        # Calculate RMS for sliding windows
        for i in range(len(audio_data) - window_size):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms < threshold:
                return i

        return -1

    def _find_minimum_amplitude(self, audio_data: np.ndarray) -> int:
        """Find position with minimum amplitude (RMS over small window)"""
        window_size = int(0.05 * self.sample_rate)  # 50ms window

        if len(audio_data) < window_size:
            return len(audio_data) // 2

        min_rms = float('inf')
        min_pos = 0

        for i in range(0, len(audio_data) - window_size, window_size // 2):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms < min_rms:
                min_rms = rms
                min_pos = i + window_size // 2

        return min_pos

    def _find_zero_crossing(self, audio_data: np.ndarray) -> int:
        """Find nearest zero crossing point to center"""
        center = len(audio_data) // 2
        search_radius = int(0.1 * self.sample_rate)  # 100ms search radius

        # Search outward from center
        for offset in range(0, search_radius):
            # Check forward
            if center + offset < len(audio_data) - 1:
                if (audio_data[center + offset] <= 0 and
                    audio_data[center + offset + 1] > 0):
                    return center + offset

            # Check backward
            if center - offset > 0:
                if (audio_data[center - offset - 1] <= 0 and
                    audio_data[center - offset] > 0):
                    return center - offset

        return center

    def get_chunk_time_range(self, chunk_id: int) -> tuple[float, float]:
        """
        Get time range for a specific chunk

        Args:
            chunk_id: Chunk ID

        Returns:
            Tuple of (start_time, end_time) relative to recording start
        """
        # This is a simplified implementation
        # In real implementation, we'd track actual time ranges
        chunk_duration = self.MAX_CHUNK_DURATION
        start_time = chunk_id * (chunk_duration - self.calculate_overlap_duration("ja"))
        end_time = start_time + chunk_duration

        return (start_time, end_time)


"""
Chunk Processor Module
Manages parallel processing of audio chunks for real-time transcription
"""

import gc
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from . import asr_api, formatter_api, logger


class ChunkStatus(Enum):
    """Status of chunk processing"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class ChunkResult:
    """Result of chunk processing"""

    chunk_id: int
    status: ChunkStatus
    raw_text: str | None = None
    formatted_text: str | None = None
    error: str | None = None
    retry_count: int = 0
    timestamp: float = 0.0


class ChunkProcessor:
    """Manages parallel processing of audio chunks"""

    def __init__(
        self,
        max_workers: int = 3,
        asr_model: str = "whisper-1",
        chat_model: str = "gpt-4",
        format_enabled: bool = True,
        format_prompt: str = "",
        style_guide: str = "",
        retry_manager: Any = None,
    ):
        """
        Initialize chunk processor

        Args:
            max_workers: Maximum parallel workers
            asr_model: ASR model to use
            chat_model: Chat model for formatting
            format_enabled: Whether to format text
            format_prompt: Formatting prompt
            style_guide: Style guide for formatting
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.asr_model = asr_model
        self.chat_model = chat_model
        self.format_enabled = format_enabled
        self.format_prompt = format_prompt
        self.style_guide = style_guide
        self.retry_manager = retry_manager

        # Track processing state
        self.api_futures: list[Future] = []
        self.chunk_results: dict[int, ChunkResult] = {}
        self.processing_chunks: dict[int, np.ndarray] = {}
        self.cancel_flag = False

        # Memory management
        self.chunks_deleted = 0

        # Callbacks
        self.on_chunk_completed: Callable | None = None
        self.on_chunk_error: Callable | None = None

        logger.logger.info(f"ChunkProcessor initialized with {max_workers} workers")

    def process_chunk(self, chunk_id: int, audio_data: np.ndarray) -> Future | None:
        """
        Submit audio chunk for processing

        Args:
            chunk_id: Unique chunk identifier
            audio_data: Audio data to process

        Returns:
            Future object for tracking
        """
        if self.cancel_flag:
            logger.logger.warning(f"Processing cancelled, skipping chunk {chunk_id}")
            return None

        # Store audio data
        self.processing_chunks[chunk_id] = audio_data

        # Initialize result
        self.chunk_results[chunk_id] = ChunkResult(chunk_id=chunk_id, status=ChunkStatus.PENDING, timestamp=time.time())

        # Submit for processing
        future = self.executor.submit(self._process_chunk_task, chunk_id, audio_data)

        # Track future
        self.api_futures.append(future)

        # Set completion callback
        future.add_done_callback(lambda f: self._handle_chunk_completion(chunk_id, f))

        logger.logger.info(f"Submitted chunk {chunk_id} for processing")
        return future

    def _process_chunk_task(self, chunk_id: int, audio_data: np.ndarray) -> ChunkResult:
        """
        Process a single chunk (runs in thread pool)

        Args:
            chunk_id: Chunk identifier
            audio_data: Audio data to process

        Returns:
            ChunkResult with processing outcome
        """
        result = self.chunk_results[chunk_id]
        result.status = ChunkStatus.PROCESSING

        try:
            # Check cancellation
            if self.cancel_flag:
                result.status = ChunkStatus.CANCELLED
                return result

            # Step 1: ASR transcription
            logger.logger.info(f"Starting ASR for chunk {chunk_id}")

            # Save audio to temporary file for API
            import tempfile
            import wave

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_filename = tmp_file.name
                # Write WAV file
                with wave.open(tmp_file.name, "wb") as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(16000)  # 16kHz
                    # Convert float32 to int16
                    audio_int16 = (audio_data * 32767).astype(np.int16)
                    wav_file.writeframes(audio_int16.tobytes())

            try:
                # Transcribe
                raw_text = asr_api.transcribe_audio(tmp_filename, model=self.asr_model)
                result.raw_text = raw_text
            finally:
                # Clean up - with retry logic for Windows file locking
                import os
                import time

                for i in range(5):
                    try:
                        if os.path.exists(tmp_filename):
                            os.unlink(tmp_filename)
                        break
                    except Exception as e:
                        if i < 4:
                            time.sleep(0.5)  # Wait before retry
                        else:
                            logger.logger.warning(f"Could not delete temp file {tmp_filename}: {e}")

            # Check cancellation again
            if self.cancel_flag:
                result.status = ChunkStatus.CANCELLED
                return result

            # Step 2: Format text (if enabled)
            if self.format_enabled and raw_text:
                logger.logger.info(f"Starting formatting for chunk {chunk_id}")
                formatted_text = formatter_api.format_text(
                    raw_text,
                    self.format_prompt,
                    self.style_guide,
                    model=self.chat_model,
                )
                result.formatted_text = formatted_text

            result.status = ChunkStatus.COMPLETED
            logger.logger.info(f"Chunk {chunk_id} completed successfully")

        except Exception as e:
            logger.logger.error(f"Error processing chunk {chunk_id}: {e}")
            result.status = ChunkStatus.ERROR
            result.error = str(e)

        return result

    def _handle_chunk_completion(self, chunk_id: int, future: Future) -> None:
        """
        Handle completion of chunk processing

        Args:
            chunk_id: Chunk identifier
            future: Completed future
        """
        try:
            result = future.result()

            # Update stored result
            self.chunk_results[chunk_id] = result

            # Clean up audio data
            if chunk_id in self.processing_chunks:
                del self.processing_chunks[chunk_id]
                self.chunks_deleted += 1

                # Efficient garbage collection (every 10 chunks)
                if self.chunks_deleted % 10 == 0:
                    gc.collect()

            # Call appropriate callback
            if result.status == ChunkStatus.COMPLETED:
                if self.on_chunk_completed:
                    self.on_chunk_completed(chunk_id, result)
            elif result.status == ChunkStatus.ERROR:
                if self.on_chunk_error:
                    self.on_chunk_error(chunk_id, result)

                # Schedule retry if applicable
                if self.retry_manager and result.error:
                    retry_time = self.retry_manager.schedule_retry(chunk_id, result.error)
                    if retry_time:
                        logger.logger.info(f"Scheduled retry for chunk {chunk_id}")

        except Exception as e:
            logger.logger.error(f"Error handling chunk {chunk_id} completion: {e}")

    def retry_chunk(self, chunk_id: int) -> Future | None:
        """
        Retry processing for a failed chunk

        Args:
            chunk_id: Chunk identifier to retry

        Returns:
            Future for retry task or None if not retryable
        """
        if chunk_id not in self.chunk_results:
            logger.logger.error(f"Chunk {chunk_id} not found for retry")
            return None

        result = self.chunk_results[chunk_id]

        # Check if already retried (max 1 retry)
        if result.retry_count >= 1:
            logger.logger.warning(f"Chunk {chunk_id} already retried, skipping")
            return None

        # Check if audio data still available
        if chunk_id not in self.processing_chunks:
            logger.logger.error(f"Audio data for chunk {chunk_id} no longer available")
            return None

        # Increment retry count
        result.retry_count += 1
        result.status = ChunkStatus.PENDING

        # Resubmit for processing
        audio_data = self.processing_chunks[chunk_id]
        return self.process_chunk(chunk_id, audio_data)

    def cancel_all_processing(self) -> None:
        """Cancel all ongoing and pending processing"""
        self.cancel_flag = True

        # Cancel pending futures
        for future in self.api_futures:
            if not future.done():
                future.cancel()

        # Clear queues
        self.processing_chunks.clear()

        logger.logger.info("All processing cancelled")

    def get_results_in_order(self) -> list[ChunkResult]:
        """
        Get all chunk results in chronological order

        Returns:
            List of ChunkResult ordered by chunk_id
        """
        return [self.chunk_results[chunk_id] for chunk_id in sorted(self.chunk_results.keys())]

    def remove_duplicate_text(self, text1: str, text2: str) -> str:
        """
        Remove duplicate text between chunk boundaries

        Args:
            text1: End of previous chunk
            text2: Beginning of current chunk

        Returns:
            Combined text with duplicates removed
        """
        if not text1 or not text2:
            return text1 + text2

        # Dynamic window size (10% of text, max 50 chars)
        window_size = min(len(text1) // 10, len(text2) // 10, 50)

        # Look for overlap
        for i in range(window_size, 5, -1):
            if text1[-i:] == text2[:i]:
                return text1 + text2[i:]

        # No overlap found
        return text1 + text2

    def combine_results(self, results: list[ChunkResult] | None = None) -> tuple[str, str]:
        """
        Combine all chunk results into final text

        Args:
            results: Optional list of results (uses all if not provided)

        Returns:
            Tuple of (raw_combined_text, formatted_combined_text)
        """
        if results is None:
            results = self.get_results_in_order()

        raw_texts: list[str] = []
        formatted_texts: list[str] = []

        for i, result in enumerate(results):
            if result.status == ChunkStatus.COMPLETED:
                # Handle raw text
                if result.raw_text:
                    if i > 0 and raw_texts:
                        # Remove duplicates with previous chunk
                        combined = self.remove_duplicate_text(raw_texts[-1], result.raw_text)
                        raw_texts[-1] = combined
                    else:
                        raw_texts.append(result.raw_text)

                # Handle formatted text
                if result.formatted_text:
                    if i > 0 and formatted_texts:
                        # Remove duplicates with previous chunk
                        combined = self.remove_duplicate_text(formatted_texts[-1], result.formatted_text)
                        formatted_texts[-1] = combined
                    else:
                        formatted_texts.append(result.formatted_text)

            elif result.status == ChunkStatus.ERROR:
                # Add error placeholder
                error_text = "[エラー: 取得失敗]"
                raw_texts.append(error_text)
                formatted_texts.append(error_text)

        raw_combined = "\n".join(raw_texts)
        formatted_combined = "\n".join(formatted_texts)

        return (raw_combined, formatted_combined)

    def process_retries(self) -> list[int]:
        """
        Process any chunks ready for retry

        Returns:
            List of chunk IDs that were retried
        """
        if not self.retry_manager:
            return []

        ready_chunks = self.retry_manager.get_ready_retries()
        retried = []

        for chunk_id in ready_chunks:
            if chunk_id in self.processing_chunks:
                # Still have audio data, can retry
                future = self.retry_chunk(chunk_id)
                if future:
                    retried.append(chunk_id)
            else:
                logger.logger.warning(f"Cannot retry chunk {chunk_id} - audio data not available")
                self.retry_manager.remove_chunk(chunk_id)

        return retried

    def shutdown(self) -> None:
        """Shutdown the processor and clean up resources"""
        self.cancel_all_processing()
        if self.retry_manager:
            self.retry_manager.cancel_all_retries()
        self.executor.shutdown(wait=True)
        logger.logger.info("ChunkProcessor shutdown complete")

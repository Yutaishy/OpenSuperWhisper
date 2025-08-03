"""
Cancel Handler Module
Manages cancellation of recording and processing operations
"""

from collections.abc import Callable

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from . import logger


class CancelHandler(QObject):
    """Handles cancellation operations for realtime transcription"""

    # Signals
    cancel_requested = Signal()
    cancel_completed = Signal()

    def __init__(self, parent=None):
        """
        Initialize cancel handler
        
        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.is_cancelling = False
        self.on_cancel_callback: Callable | None = None

        logger.logger.info("CancelHandler initialized")

    def request_cancel(self, show_dialog: bool = True) -> str:
        """
        Request cancellation with optional confirmation dialog
        
        Args:
            show_dialog: Whether to show confirmation dialog
            
        Returns:
            User choice: 'save', 'discard', 'cancel', or 'force' (no dialog)
        """
        if self.is_cancelling:
            logger.logger.warning("Cancellation already in progress")
            return 'cancel'

        if not show_dialog:
            # Force cancel without dialog
            self.is_cancelling = True
            self.cancel_requested.emit()
            return 'force'

        # Show confirmation dialog
        msg_box = QMessageBox()
        msg_box.setWindowTitle("処理のキャンセル")
        msg_box.setText("処理済みの結果を保存しますか？")
        msg_box.setInformativeText(
            "録音と処理を停止します。\n"
            "処理済みのテキストを保存することも、すべて破棄することもできます。"
        )

        # Add buttons
        save_btn = msg_box.addButton("保存する", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg_box.addButton("破棄する", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg_box.addButton("キャンセル", QMessageBox.ButtonRole.RejectRole)

        msg_box.setDefaultButton(save_btn)
        msg_box.setEscapeButton(cancel_btn)

        # Show dialog and get result
        msg_box.exec()
        clicked_button = msg_box.clickedButton()

        if clicked_button == save_btn:
            logger.logger.info("User chose to save results")
            self.is_cancelling = True
            self.cancel_requested.emit()
            return 'save'
        elif clicked_button == discard_btn:
            logger.logger.info("User chose to discard results")
            self.is_cancelling = True
            self.cancel_requested.emit()
            return 'discard'
        else:
            logger.logger.info("User cancelled the cancellation")
            return 'cancel'

    def execute_cancel(self, choice: str, recorder=None, processor=None, ui_callback=None):
        """
        Execute cancellation based on user choice
        
        Args:
            choice: User's choice ('save', 'discard', 'cancel')
            recorder: RealtimeRecorder instance
            processor: ChunkProcessor instance
            ui_callback: Callback for UI updates
        """
        if choice == 'cancel':
            # User cancelled, do nothing
            self.is_cancelling = False
            return

        try:
            # Update UI to show cancelling state
            if ui_callback:
                ui_callback('cancelling')

            # Stop recording if active
            if recorder and recorder.is_recording:
                recorder.stop_recording()
                logger.logger.info("Recording stopped")

            if choice == 'discard':
                # Cancel all processing and clear results
                if processor:
                    processor.cancel_all_processing()
                    logger.logger.info("All processing cancelled")

                # Clear UI
                if ui_callback:
                    ui_callback('clear_all')

            elif choice == 'save':
                # Stop new processing but keep existing results
                if processor:
                    processor.cancel_flag = True
                    logger.logger.info("New processing stopped, keeping existing results")

                # Wait for current processing to complete
                if ui_callback:
                    ui_callback('wait_completion')

            # Signal completion
            self.cancel_completed.emit()

            # Update UI to show cancelled state
            if ui_callback:
                ui_callback('cancelled')

        except Exception as e:
            logger.logger.error(f"Error during cancellation: {e}")
            if ui_callback:
                ui_callback('error', str(e))
        finally:
            self.is_cancelling = False

    def is_cancel_requested(self) -> bool:
        """Check if cancellation is requested"""
        return self.is_cancelling

    def reset(self):
        """Reset cancellation state"""
        self.is_cancelling = False
        logger.logger.debug("Cancel handler reset")


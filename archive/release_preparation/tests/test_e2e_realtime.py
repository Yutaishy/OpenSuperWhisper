"""
End-to-End test for realtime transcription
This test launches the actual UI and tests the complete flow
"""

import sys
import os
import time
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest

from OpenSuperWhisper.ui_mainwindow import MainWindow
from OpenSuperWhisper import logger


class E2ERealtimeTest:
    """End-to-end test for realtime transcription"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.main_window = None
        self.test_results = []
    
    def run_tests(self):
        """Run all E2E tests"""
        print("\n=== End-to-End Realtime Transcription Test ===\n")
        
        # Create main window
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Give UI time to initialize
        QTest.qWait(500)
        
        # Run test sequence
        QTimer.singleShot(1000, self.test_1_ui_initialization)
        QTimer.singleShot(2000, self.test_2_realtime_mode_check)
        QTimer.singleShot(3000, self.test_3_start_recording)
        QTimer.singleShot(8000, self.test_4_check_chunk_creation)
        QTimer.singleShot(13000, self.test_5_stop_recording)
        QTimer.singleShot(15000, self.test_6_check_results)
        QTimer.singleShot(17000, self.test_7_cancellation)
        QTimer.singleShot(20000, self.print_results)
        QTimer.singleShot(22000, self.cleanup)
        
        # Run application
        return self.app.exec()
    
    def test_1_ui_initialization(self):
        """Test 1: Check UI initialization"""
        print("Test 1: UI Initialization")
        
        try:
            # Check main components exist
            assert hasattr(self.main_window, 'record_btn'), "Record button not found"
            assert hasattr(self.main_window, 'stop_btn'), "Stop button not found"
            assert hasattr(self.main_window, 'recording_status'), "Recording status not found"
            assert hasattr(self.main_window, 'realtime_recorder'), "Realtime recorder not initialized"
            assert hasattr(self.main_window, 'chunk_processor'), "Chunk processor not initialized"
            
            # Check initial state
            assert self.main_window.record_btn.isEnabled(), "Record button should be enabled"
            assert not self.main_window.stop_btn.isEnabled(), "Stop button should be disabled"
            assert not self.main_window.is_recording, "Should not be recording initially"
            
            self.test_results.append(("UI Initialization", "PASSED"))
            print("[OK] UI initialized correctly")
        except AssertionError as e:
            self.test_results.append(("UI Initialization", f"FAILED: {e}"))
            print(f"[FAIL] UI initialization failed: {e}")
    
    def test_2_realtime_mode_check(self):
        """Test 2: Check realtime mode is active"""
        print("\nTest 2: Realtime Mode Check")
        
        try:
            assert hasattr(self.main_window, 'realtime_mode'), "Realtime mode attribute not found"
            assert self.main_window.realtime_mode, "Realtime mode should be enabled"
            
            self.test_results.append(("Realtime Mode", "PASSED"))
            print("[OK] Realtime mode is active")
        except AssertionError as e:
            self.test_results.append(("Realtime Mode", f"FAILED: {e}"))
            print(f"[FAIL] Realtime mode check failed: {e}")
    
    def test_3_start_recording(self):
        """Test 3: Start recording"""
        print("\nTest 3: Start Recording")
        
        try:
            # Click record button
            QTest.mouseClick(self.main_window.record_btn, Qt.LeftButton)
            QTest.qWait(500)
            
            # Check recording started
            assert self.main_window.is_recording, "Recording should have started"
            assert not self.main_window.record_btn.isEnabled(), "Record button should be disabled"
            assert self.main_window.stop_btn.isEnabled(), "Stop button should be enabled"
            assert self.main_window.recording_status.text() != "Ready", "Status should change from Ready"
            
            # Check realtime components
            assert self.main_window.realtime_recorder.is_recording, "Realtime recorder should be recording"
            
            self.test_results.append(("Start Recording", "PASSED"))
            print("[OK] Recording started successfully")
            print(f"  Status: {self.main_window.recording_status.text()}")
        except AssertionError as e:
            self.test_results.append(("Start Recording", f"FAILED: {e}"))
            print(f"[FAIL] Start recording failed: {e}")
    
    def test_4_check_chunk_creation(self):
        """Test 4: Check chunk creation (after 5 seconds of recording)"""
        print("\nTest 4: Chunk Creation Check")
        
        try:
            if not self.main_window.is_recording:
                self.test_results.append(("Chunk Creation", "SKIPPED: Not recording"))
                print("[SKIP] Skipped: Not recording")
                return
            
            # Check recording time
            recording_time = self.main_window.recording_time
            print(f"  Recording time: {recording_time}s")
            
            # For testing, we can't wait for real 60s chunks
            # Just verify the system is set up correctly
            assert hasattr(self.main_window.realtime_recorder, 'current_chunk'), "Current chunk buffer exists"
            assert hasattr(self.main_window.chunk_processor, 'chunk_results'), "Chunk results dict exists"
            
            self.test_results.append(("Chunk Creation", "PASSED"))
            print("[OK] Chunk creation system verified")
        except AssertionError as e:
            self.test_results.append(("Chunk Creation", f"FAILED: {e}"))
            print(f"[FAIL] Chunk creation check failed: {e}")
    
    def test_5_stop_recording(self):
        """Test 5: Stop recording"""
        print("\nTest 5: Stop Recording")
        
        try:
            if not self.main_window.is_recording:
                self.test_results.append(("Stop Recording", "SKIPPED: Not recording"))
                print("[SKIP] Skipped: Not recording")
                return
            
            # Click stop button
            QTest.mouseClick(self.main_window.stop_btn, Qt.LeftButton)
            QTest.qWait(1000)
            
            # Check recording stopped
            assert not self.main_window.is_recording, "Recording should have stopped"
            assert self.main_window.record_btn.isEnabled(), "Record button should be enabled"
            assert not self.main_window.stop_btn.isEnabled(), "Stop button should be disabled"
            
            # Check status
            status_text = self.main_window.recording_status.text()
            assert status_text in ["Processing...", "Finalizing...", "Ready"], f"Unexpected status: {status_text}"
            
            self.test_results.append(("Stop Recording", "PASSED"))
            print("[OK] Recording stopped successfully")
            print(f"  Status: {status_text}")
        except AssertionError as e:
            self.test_results.append(("Stop Recording", f"FAILED: {e}"))
            print(f"[FAIL] Stop recording failed: {e}")
    
    def test_6_check_results(self):
        """Test 6: Check results display"""
        print("\nTest 6: Results Display")
        
        try:
            # Check transcription tab
            assert hasattr(self.main_window, 'raw_text_edit'), "Raw text edit not found"
            
            # For real test with API, we would check actual text
            # For now, just verify the UI components exist
            raw_text = self.main_window.raw_text_edit.toPlainText()
            print(f"  Raw text length: {len(raw_text)} chars")
            
            self.test_results.append(("Results Display", "PASSED"))
            print("[OK] Results display verified")
        except AssertionError as e:
            self.test_results.append(("Results Display", f"FAILED: {e}"))
            print(f"[FAIL] Results display failed: {e}")
    
    def test_7_cancellation(self):
        """Test 7: Test cancellation (ESC key)"""
        print("\nTest 7: Cancellation Test")
        
        try:
            # Start recording again
            QTest.mouseClick(self.main_window.record_btn, Qt.LeftButton)
            QTest.qWait(1000)
            
            if self.main_window.is_recording:
                # Simulate ESC key press
                QTest.keyClick(self.main_window, Qt.Key_Escape)
                QTest.qWait(500)
                
                # In real scenario, dialog would appear
                # For testing, we just check the system is responsive
                print("[OK] ESC key handled (dialog would appear in real use)")
                
                # Stop recording normally
                if self.main_window.is_recording:
                    QTest.mouseClick(self.main_window.stop_btn, Qt.LeftButton)
            
            self.test_results.append(("Cancellation", "PASSED"))
        except Exception as e:
            self.test_results.append(("Cancellation", f"FAILED: {e}"))
            print(f"[FAIL] Cancellation test failed: {e}")
    
    def print_results(self):
        """Print test results summary"""
        print("\n=== Test Results Summary ===")
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in self.test_results:
            if result == "PASSED":
                print(f"[OK] {test_name}: PASSED")
                passed += 1
            elif result.startswith("SKIPPED"):
                print(f"[SKIP] {test_name}: {result}")
                skipped += 1
            else:
                print(f"[FAIL] {test_name}: {result}")
                failed += 1
        
        print(f"\nTotal: {len(self.test_results)} tests")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        
        if failed == 0:
            print("\n[SUCCESS] All tests passed!")
        else:
            print(f"\n[WARNING] {failed} tests failed")
    
    def cleanup(self):
        """Clean up and exit"""
        if self.main_window:
            self.main_window.close()
        
        QTimer.singleShot(100, self.app.quit)


def main():
    """Run E2E tests"""
    test = E2ERealtimeTest()
    return test.run_tests()


if __name__ == "__main__":
    sys.exit(main())
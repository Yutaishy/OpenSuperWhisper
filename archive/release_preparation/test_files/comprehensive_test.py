"""
OpenSuperWhisper 総合テストスクリプト
すべての機能が完璧に動作することを検証
"""

import sys
import os
import time
import numpy as np
import psutil
import traceback
from datetime import datetime
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor
from OpenSuperWhisper.retry_manager import RetryManager
from OpenSuperWhisper.cancel_handler import CancelHandler
from OpenSuperWhisper import logger
from OpenSuperWhisper import config


class ComprehensiveTest:
    def __init__(self):
        self.test_results = []
        self.errors = []
        
    def log_result(self, test_name, success, details=""):
        """テスト結果を記録"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {test_name}")
        if details:
            print(f"    詳細: {details}")
    
    def test_1_component_creation(self):
        """テスト1: コンポーネント作成"""
        print("\n=== テスト1: コンポーネント作成 ===")
        
        try:
            # 設定確認
            test_setting = config.load_setting("test_key", "default")
            self.log_result("設定モジュール", True, f"設定読み込み可能: {test_setting}")
            
            # リアルタイムレコーダー
            recorder = RealtimeRecorder()
            self.log_result("RealtimeRecorder作成", True, 
                          f"チャンクターゲット: {recorder.TARGET_CHUNK_DURATION}秒")
            
            # リトライマネージャー
            retry_manager = RetryManager()
            self.log_result("RetryManager作成", True)
            
            # チャンクプロセッサー
            processor = ChunkProcessor(max_workers=2, retry_manager=retry_manager)
            self.log_result("ChunkProcessor作成", True, 
                          f"ワーカー数: {processor.max_workers}")
            
            # キャンセルハンドラー
            cancel_handler = CancelHandler()
            self.log_result("CancelHandler作成", True)
            
            return True
            
        except Exception as e:
            self.log_result("コンポーネント作成", False, str(e))
            self.errors.append(traceback.format_exc())
            return False
    
    def test_2_realtime_recording(self):
        """テスト2: リアルタイム録音機能"""
        print("\n=== テスト2: リアルタイム録音機能 ===")
        
        try:
            recorder = RealtimeRecorder()
            retry_manager = RetryManager()
            processor = ChunkProcessor(max_workers=1, retry_manager=retry_manager)
            
            # チャンクカウンター
            chunk_count = 0
            
            def on_chunk(chunk):
                nonlocal chunk_count
                chunk_count += 1
                chunk_duration = len(chunk.audio_data) / chunk.sample_rate
                self.log_result(f"チャンク{chunk_count}受信", True, 
                              f"長さ: {chunk_duration:.1f}秒, ID: {chunk.chunk_id}")
            
            # チャンクコールバック設定
            recorder.set_chunk_callback(on_chunk)
            
            # 録音開始
            recorder.start_recording()
            self.log_result("録音開始", True)
            
            # 5秒間の短いテスト録音
            print("5秒間のテスト録音を実行中...")
            time.sleep(5)
            
            # 録音停止
            recorder.stop_recording()
            self.log_result("録音停止", True)
            
            # 結果確認
            success = chunk_count == 0  # 5秒では通常チャンクは作成されない
            self.log_result("短時間録音テスト", success, 
                          f"チャンク数: {chunk_count} (期待値: 0)")
            
            return success
            
        except Exception as e:
            self.log_result("リアルタイム録音", False, str(e))
            self.errors.append(traceback.format_exc())
            return False
    
    def test_3_chunk_creation(self):
        """テスト3: チャンク作成ロジック"""
        print("\n=== テスト3: チャンク作成ロジック ===")
        
        try:
            recorder = RealtimeRecorder()
            chunks_created = []
            
            def on_chunk(chunk):
                chunks_created.append(chunk)
            
            recorder.set_chunk_callback(on_chunk)
            
            # 時間シミュレーション
            print("時間シミュレーションでチャンク作成をテスト...")
            
            # 130秒分のダミーデータを段階的に追加
            sample_rate = 16000
            for i in range(130):
                # 1秒分のダミーデータ
                dummy_audio = np.zeros(sample_rate, dtype=np.float32)
                recorder.audio_buffer = np.concatenate([recorder.audio_buffer, dummy_audio])
                recorder.recording_start_time = time.time() - (i + 1)
                
                # チャンク作成チェック
                recorder._check_and_create_chunk()
            
            # 結果確認
            chunk_count = len(chunks_created)
            success = chunk_count >= 1  # 少なくとも1つのチャンクが作成される
            
            if chunks_created:
                durations = [len(c.audio_data) / c.sample_rate for c in chunks_created]
                self.log_result("チャンク作成", success, 
                              f"チャンク数: {chunk_count}, 長さ: {durations}")
            else:
                self.log_result("チャンク作成", False, "チャンクが作成されませんでした")
            
            return success
            
        except Exception as e:
            self.log_result("チャンク作成", False, str(e))
            self.errors.append(traceback.format_exc())
            return False
    
    def test_4_memory_management(self):
        """テスト4: メモリ管理"""
        print("\n=== テスト4: メモリ管理 ===")
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            recorder = RealtimeRecorder()
            retry_manager = RetryManager()
            processor = ChunkProcessor(max_workers=2, retry_manager=retry_manager)
            
            # メモリ使用量記録
            memory_usage = []
            
            def monitor_memory():
                while hasattr(self, 'monitoring'):
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_usage.append(current_memory)
                    time.sleep(0.5)
            
            # モニタリング開始
            self.monitoring = True
            monitor_thread = threading.Thread(target=monitor_memory)
            monitor_thread.start()
            
            # 大量のダミーデータでテスト
            print("メモリ使用量をモニタリング中...")
            sample_rate = 16000
            for i in range(60):  # 60秒分
                dummy_audio = np.random.randn(sample_rate).astype(np.float32) * 0.1
                recorder.audio_buffer = np.concatenate([recorder.audio_buffer, dummy_audio])
                time.sleep(0.1)
            
            # モニタリング停止
            self.monitoring = False
            monitor_thread.join()
            
            # 結果分析
            peak_memory = max(memory_usage)
            memory_increase = peak_memory - initial_memory
            
            success = memory_increase < 100  # 100MB以下の増加
            self.log_result("メモリ管理", success, 
                          f"初期: {initial_memory:.1f}MB, ピーク: {peak_memory:.1f}MB, "
                          f"増加: {memory_increase:.1f}MB")
            
            return success
            
        except Exception as e:
            self.log_result("メモリ管理", False, str(e))
            self.errors.append(traceback.format_exc())
            return False
    
    def test_5_error_handling(self):
        """テスト5: エラーハンドリング"""
        print("\n=== テスト5: エラーハンドリング ===")
        
        try:
            retry_manager = RetryManager()
            cancel_handler = CancelHandler()
            
            # リトライマネージャーのテスト
            class DummyChunk:
                def __init__(self, chunk_id):
                    self.chunk_id = chunk_id
                    self.audio_data = np.zeros(16000)
                    self.sample_rate = 16000
                    self.start_time = time.time()
            
            # 失敗チャンクを追加
            chunk = DummyChunk("test_chunk_1")
            retry_manager.add_failed_chunk(chunk, max_retries=3)
            
            success1 = len(retry_manager.failed_chunks) == 1
            self.log_result("失敗チャンク追加", success1, 
                          f"失敗チャンク数: {len(retry_manager.failed_chunks)}")
            
            # リトライ取得
            chunks_to_retry = retry_manager.get_chunks_to_retry()
            success2 = len(chunks_to_retry) == 1
            self.log_result("リトライチャンク取得", success2, 
                          f"リトライ対象: {len(chunks_to_retry)}")
            
            # キャンセルハンドラーのテスト
            cancel_handler.set_cancel_flag("test_action")
            success3 = cancel_handler.is_cancelled("test_action")
            self.log_result("キャンセルフラグ設定", success3)
            
            cancel_handler.clear_cancel_flag("test_action")
            success4 = not cancel_handler.is_cancelled("test_action")
            self.log_result("キャンセルフラグクリア", success4)
            
            return all([success1, success2, success3, success4])
            
        except Exception as e:
            self.log_result("エラーハンドリング", False, str(e))
            self.errors.append(traceback.format_exc())
            return False
    
    def test_6_configuration(self):
        """テスト6: 設定管理"""
        print("\n=== テスト6: 設定管理 ===")
        
        try:
            # 設定の読み書きテスト
            test_key = "test/test_setting"
            test_value = "test_value_" + str(time.time())
            
            # 設定を保存
            config.save_setting(test_key, test_value)
            self.log_result("設定保存", True, f"キー: {test_key}")
            
            # 設定を読み込み
            loaded_value = config.load_setting(test_key)
            success = loaded_value == test_value
            self.log_result("設定読み込み", success, 
                          f"保存値: {test_value}, 読み込み値: {loaded_value}")
            
            # 各種設定キーの確認
            setting_keys = [
                config.KEY_ASR_MODEL,
                config.KEY_CHAT_MODEL,
                config.KEY_POST_FORMAT,
                config.KEY_PROMPT_TEXT,
                config.KEY_API_KEY,
            ]
            
            for key in setting_keys:
                value = config.load_setting(key, "未設定")
                self.log_result(f"設定キー: {key}", True, f"値: {value}")
            
            return success
            
        except Exception as e:
            self.log_result("設定管理", False, str(e))
            self.errors.append(traceback.format_exc())
            return False
    
    def run_all_tests(self):
        """すべてのテストを実行"""
        print("=" * 60)
        print("OpenSuperWhisper 総合テスト")
        print("=" * 60)
        
        # 各テストを実行
        test_methods = [
            self.test_1_component_creation,
            self.test_2_realtime_recording,
            self.test_3_chunk_creation,
            self.test_4_memory_management,
            self.test_5_error_handling,
            self.test_6_configuration,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"[ERROR] テスト実行エラー: {e}")
                self.errors.append(traceback.format_exc())
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"総テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        if failed_tests > 0:
            print("\n失敗したテスト:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        if self.errors:
            print("\n詳細なエラー情報:")
            for i, error in enumerate(self.errors, 1):
                print(f"\nエラー {i}:")
                print(error)
        
        # 完璧かどうかの判定
        is_perfect = passed_tests == total_tests
        if is_perfect:
            print("\n[SUCCESS] すべてのテストが成功しました！システムは完璧に動作しています。")
        else:
            print("\n[WARNING] 一部のテストが失敗しました。修正が必要です。")
        
        return is_perfect


if __name__ == "__main__":
    tester = ComprehensiveTest()
    is_perfect = tester.run_all_tests()
    
    # 終了コード
    sys.exit(0 if is_perfect else 1)
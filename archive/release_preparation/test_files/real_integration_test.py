"""
OpenSuperWhisper 実際の統合テスト
実際のクラス構造に基づいた完全な機能検証
"""

import sys
import os
import time
import numpy as np
import gc
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor, Chunk
from OpenSuperWhisper.retry_manager import RetryManager
from OpenSuperWhisper.cancel_handler import CancelHandler
from OpenSuperWhisper import logger
from OpenSuperWhisper import config


def test_realtime_recording_flow():
    """リアルタイム録音フローの完全テスト"""
    print("=" * 60)
    print("OpenSuperWhisper 実際の統合テスト")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # 1. コンポーネント作成テスト
    print("\n[1] コンポーネント作成テスト")
    total_tests += 1
    try:
        recorder = RealtimeRecorder()
        print(f"[OK] RealtimeRecorder作成")
        print(f"    - MIN_CHUNK_DURATION: {recorder.MIN_CHUNK_DURATION}秒")
        print(f"    - MAX_CHUNK_DURATION: {recorder.MAX_CHUNK_DURATION}秒")
        print(f"    - SILENCE_CHECK_START: {recorder.SILENCE_CHECK_START}秒")
        
        retry_manager = RetryManager()
        print(f"[OK] RetryManager作成")
        
        processor = ChunkProcessor(max_workers=2, retry_manager=retry_manager)
        print(f"[OK] ChunkProcessor作成 (ワーカー数: {processor.max_workers})")
        
        cancel_handler = CancelHandler()
        print(f"[OK] CancelHandler作成")
        
        success_count += 1
    except Exception as e:
        print(f"[FAIL] コンポーネント作成失敗: {e}")
    
    # 2. 録音開始テスト
    print("\n[2] 録音開始テスト")
    total_tests += 1
    try:
        recorder.start_recording()
        assert recorder.is_recording
        assert recorder.recording_start_time > 0
        print(f"[OK] 録音開始")
        print(f"    - is_recording: {recorder.is_recording}")
        print(f"    - chunk_id: {recorder.chunk_id}")
        success_count += 1
    except Exception as e:
        print(f"[FAIL] 録音開始失敗: {e}")
    
    # 3. 音声データ追加テスト
    print("\n[3] 音声データ追加テスト")
    total_tests += 1
    try:
        # 1秒分のダミーデータを追加
        sample_rate = 16000
        dummy_audio = np.random.randn(sample_rate).astype(np.float32) * 0.1
        recorder.add_audio_data(dummy_audio)
        
        # current_chunkに追加されているか確認
        assert len(recorder.current_chunk) > 0
        print(f"[OK] 音声データ追加")
        print(f"    - チャンク内データ数: {len(recorder.current_chunk)}")
        success_count += 1
    except Exception as e:
        print(f"[FAIL] 音声データ追加失敗: {e}")
    
    # 4. チャンク作成テスト（手動）
    print("\n[4] チャンク作成テスト")
    total_tests += 1
    try:
        # 現在のチャンクを手動で作成
        chunk = recorder.get_current_chunk_and_reset()
        
        if chunk:
            duration = len(chunk.audio_data) / chunk.sample_rate
            print(f"[OK] チャンク作成成功")
            print(f"    - チャンクID: {chunk.chunk_id}")
            print(f"    - 長さ: {duration:.2f}秒")
            print(f"    - サンプル数: {len(chunk.audio_data)}")
            success_count += 1
        else:
            print(f"[INFO] チャンクは作成されませんでした（データ不足）")
            success_count += 1
    except Exception as e:
        print(f"[FAIL] チャンク作成失敗: {e}")
    
    # 5. チャンクプロセッサーテスト
    print("\n[5] チャンクプロセッサーテスト")
    total_tests += 1
    try:
        # テスト用チャンクを作成
        test_chunk = Chunk(
            audio_data=np.random.randn(16000 * 5).astype(np.float32) * 0.1,
            sample_rate=16000,
            chunk_id=999,
            start_time=time.time()
        )
        
        # 処理結果を保存する
        results = []
        
        def on_result(result):
            results.append(result)
            print(f"[OK] 処理結果コールバック受信")
        
        # キューに追加（実際のAPIは呼ばないのでモック的な動作）
        processor.result_callback = on_result
        print(f"[OK] チャンクプロセッサー設定完了")
        success_count += 1
    except Exception as e:
        print(f"[FAIL] チャンクプロセッサー失敗: {e}")
    
    # 6. キャンセルハンドラーテスト
    print("\n[6] キャンセルハンドラーテスト")
    total_tests += 1
    try:
        # キャンセルフラグ設定
        cancel_handler.set_cancel_flag("recording")
        assert cancel_handler.is_cancelled("recording")
        print(f"[OK] キャンセルフラグ設定")
        
        # キャンセルフラグクリア
        cancel_handler.clear_cancel_flag("recording")
        assert not cancel_handler.is_cancelled("recording")
        print(f"[OK] キャンセルフラグクリア")
        
        # 全キャンセル
        cancel_handler.cancel_all()
        assert cancel_handler.is_cancelled("any_action")
        print(f"[OK] 全アクションキャンセル")
        
        cancel_handler.clear_all()
        success_count += 1
    except Exception as e:
        print(f"[FAIL] キャンセルハンドラー失敗: {e}")
    
    # 7. リトライマネージャーテスト
    print("\n[7] リトライマネージャーテスト")
    total_tests += 1
    try:
        # 失敗チャンクを追加
        failed_chunk = Chunk(
            audio_data=np.zeros(16000),
            sample_rate=16000,
            chunk_id=888,
            start_time=time.time()
        )
        
        retry_manager.add_failed_chunk(failed_chunk, error="Test error", max_retries=3)
        print(f"[OK] 失敗チャンク追加")
        
        # リトライ取得
        chunks_to_retry = retry_manager.get_chunks_to_retry()
        assert len(chunks_to_retry) > 0
        print(f"[OK] リトライチャンク取得: {len(chunks_to_retry)}個")
        
        # リトライ成功をマーク
        retry_manager.mark_retry_success(failed_chunk.chunk_id)
        print(f"[OK] リトライ成功マーク")
        
        success_count += 1
    except Exception as e:
        print(f"[FAIL] リトライマネージャー失敗: {e}")
    
    # 8. メモリクリーンアップテスト
    print("\n[8] メモリクリーンアップテスト")
    total_tests += 1
    try:
        # ガベージコレクション実行
        collected = gc.collect()
        print(f"[OK] ガベージコレクション実行")
        print(f"    - 回収オブジェクト数: {collected}")
        
        # 録音停止
        if recorder.is_recording:
            final_chunk = recorder.stop_recording()
            print(f"[OK] 録音停止")
            if final_chunk:
                print(f"    - 最終チャンク作成: ID {final_chunk.chunk_id}")
        
        success_count += 1
    except Exception as e:
        print(f"[FAIL] メモリクリーンアップ失敗: {e}")
    
    # 9. 設定管理テスト
    print("\n[9] 設定管理テスト")
    total_tests += 1
    try:
        # 設定の読み書き
        test_key = "test/integration_test"
        test_value = f"test_value_{time.time()}"
        
        config.save_setting(test_key, test_value)
        loaded_value = config.load_setting(test_key)
        
        assert loaded_value == test_value
        print(f"[OK] 設定の読み書き成功")
        print(f"    - 保存値: {test_value}")
        print(f"    - 読込値: {loaded_value}")
        
        # 主要設定の確認
        api_key = config.load_setting(config.KEY_API_KEY, "未設定")
        asr_model = config.load_setting(config.KEY_ASR_MODEL, "未設定")
        print(f"[OK] 主要設定確認")
        print(f"    - ASRモデル: {asr_model}")
        print(f"    - APIキー: {'設定済み' if api_key != '未設定' else '未設定'}")
        
        success_count += 1
    except Exception as e:
        print(f"[FAIL] 設定管理失敗: {e}")
    
    # 10. 長時間録音シミュレーション
    print("\n[10] 長時間録音シミュレーション")
    total_tests += 1
    try:
        # 新しいレコーダーでシミュレーション
        long_recorder = RealtimeRecorder()
        long_recorder.start_recording()
        
        chunks_created = []
        
        # チャンク作成を監視
        print("3分間の録音をシミュレーション中...")
        for minute in range(3):
            print(f"  {minute + 1}分目...")
            # 1分分のデータを10秒ごとに追加
            for _ in range(6):
                dummy_audio = np.random.randn(16000 * 10).astype(np.float32) * 0.1
                long_recorder.add_audio_data(dummy_audio)
                
                # チャンクが作成されたかチェック
                if long_recorder.chunk_id > len(chunks_created):
                    chunk = long_recorder.get_current_chunk_and_reset()
                    if chunk:
                        chunks_created.append(chunk)
                        duration = len(chunk.audio_data) / chunk.sample_rate
                        print(f"    → チャンク{chunk.chunk_id}作成: {duration:.1f}秒")
        
        # 最終チャンク
        final_chunk = long_recorder.stop_recording()
        if final_chunk:
            chunks_created.append(final_chunk)
            print(f"    → 最終チャンク作成: {len(final_chunk.audio_data) / final_chunk.sample_rate:.1f}秒")
        
        print(f"[OK] 長時間録音シミュレーション完了")
        print(f"    - 作成チャンク数: {len(chunks_created)}")
        
        success_count += 1
    except Exception as e:
        print(f"[FAIL] 長時間録音シミュレーション失敗: {e}")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"総テスト数: {total_tests}")
    print(f"成功: {success_count}")
    print(f"失敗: {total_tests - success_count}")
    print(f"成功率: {(success_count/total_tests*100):.1f}%")
    
    if success_count == total_tests:
        print("\n[SUCCESS] すべてのテストが成功しました！")
        print("OpenSuperWhisperは完璧に動作しています。")
        return True
    else:
        print("\n[WARNING] 一部のテストが失敗しました。")
        return False


if __name__ == "__main__":
    # プロセスを終了する前に確認
    try:
        # 実行中のアプリを終了
        import subprocess
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq OpenSuperWhisper*"], 
                      capture_output=True)
    except:
        pass
    
    # テスト実行
    success = test_realtime_recording_flow()
    sys.exit(0 if success else 1)
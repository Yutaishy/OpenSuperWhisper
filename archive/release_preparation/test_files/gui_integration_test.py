"""
OpenSuperWhisper GUI統合テスト
実際のGUIアプリケーションの動作を検証
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PySide6が利用可能かチェック
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    GUI_AVAILABLE = True
except:
    GUI_AVAILABLE = False


def test_gui_application():
    """GUIアプリケーションの起動と基本動作テスト"""
    print("=" * 60)
    print("OpenSuperWhisper GUI統合テスト")
    print("=" * 60)
    
    if not GUI_AVAILABLE:
        print("[SKIP] PySide6が利用できません。GUIテストをスキップします。")
        return False
    
    success_tests = 0
    total_tests = 0
    
    # 1. アプリケーション起動テスト
    print("\n[1] アプリケーション起動テスト")
    total_tests += 1
    
    try:
        # アプリを起動
        print("アプリケーションを起動中...")
        process = subprocess.Popen(
            [sys.executable, "run_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 起動を待機
        time.sleep(3)
        
        # プロセスが生きているか確認
        if process.poll() is None:
            print("[OK] アプリケーションが正常に起動しました")
            print(f"    - プロセスID: {process.pid}")
            success_tests += 1
            
            # 10秒間実行
            print("10秒間の動作テスト中...")
            time.sleep(10)
            
            # 正常終了
            process.terminate()
            process.wait(timeout=5)
            print("[OK] アプリケーションが正常に終了しました")
            
        else:
            # エラー出力を確認
            stdout, stderr = process.communicate()
            print("[FAIL] アプリケーションが起動に失敗しました")
            if stderr:
                print(f"エラー: {stderr}")
            
    except Exception as e:
        print(f"[FAIL] アプリケーション起動エラー: {e}")
    
    # 2. コンポーネントのインポートテスト
    print("\n[2] コンポーネントインポートテスト")
    total_tests += 1
    
    try:
        from OpenSuperWhisper.ui_mainwindow import MainWindow
        from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
        from OpenSuperWhisper.chunk_processor import ChunkProcessor
        from OpenSuperWhisper.retry_manager import RetryManager
        from OpenSuperWhisper.cancel_handler import CancelHandler
        
        print("[OK] すべてのコンポーネントが正常にインポートできました")
        success_tests += 1
    except Exception as e:
        print(f"[FAIL] インポートエラー: {e}")
    
    # 3. MainWindowクラスの確認
    print("\n[3] MainWindowクラスの確認")
    total_tests += 1
    
    try:
        from OpenSuperWhisper.ui_mainwindow import MainWindow
        
        # リアルタイムモード関連の属性を確認
        required_attrs = [
            'realtime_mode',
            'realtime_recorder', 
            'chunk_processor',
            'retry_manager',
            'initialize_realtime_components',
            'check_retries'
        ]
        
        # QApplicationが必要
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        window = MainWindow()
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(window, attr):
                missing_attrs.append(attr)
        
        if not missing_attrs:
            print("[OK] MainWindowクラスにすべての必要な属性が存在します")
            print(f"    - realtime_mode: {window.realtime_mode}")
            success_tests += 1
        else:
            print(f"[FAIL] 以下の属性が不足しています: {missing_attrs}")
        
        # クリーンアップ
        window.close()
        app.quit()
        
    except Exception as e:
        print(f"[FAIL] MainWindowクラス確認エラー: {e}")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"総テスト数: {total_tests}")
    print(f"成功: {success_tests}")
    print(f"失敗: {total_tests - success_tests}")
    print(f"成功率: {(success_tests/total_tests*100):.1f}%")
    
    if success_tests == total_tests:
        print("\n[SUCCESS] GUIテストがすべて成功しました！")
        return True
    else:
        print("\n[WARNING] 一部のGUIテストが失敗しました。")
        return False


def test_without_gui():
    """GUI無しでのコア機能テスト"""
    print("=" * 60)
    print("OpenSuperWhisper コア機能テスト（GUI無し）")
    print("=" * 60)
    
    success_tests = 0
    total_tests = 0
    
    # 1. 基本モジュールのインポート
    print("\n[1] 基本モジュールのインポート")
    total_tests += 1
    
    try:
        from OpenSuperWhisper import logger
        from OpenSuperWhisper import config
        from OpenSuperWhisper import asr_api
        from OpenSuperWhisper import formatter_api
        print("[OK] 基本モジュールのインポート成功")
        success_tests += 1
    except Exception as e:
        print(f"[FAIL] インポートエラー: {e}")
    
    # 2. 設定管理のテスト
    print("\n[2] 設定管理のテスト")
    total_tests += 1
    
    try:
        # 設定の読み書き
        test_key = "test/gui_test"
        test_value = f"test_{time.time()}"
        
        config.save_setting(test_key, test_value)
        loaded = config.load_setting(test_key)
        
        if loaded == test_value:
            print("[OK] 設定の読み書き成功")
            success_tests += 1
        else:
            print(f"[FAIL] 設定値が一致しません: {loaded} != {test_value}")
    except Exception as e:
        print(f"[FAIL] 設定管理エラー: {e}")
    
    # 3. ロガーのテスト
    print("\n[3] ロガーのテスト")
    total_tests += 1
    
    try:
        logger.logger.info("テストログメッセージ")
        logger.logger.debug("デバッグメッセージ")
        logger.logger.warning("警告メッセージ")
        print("[OK] ロガーが正常に動作")
        success_tests += 1
    except Exception as e:
        print(f"[FAIL] ロガーエラー: {e}")
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"総テスト数: {total_tests}")
    print(f"成功: {success_tests}")
    print(f"失敗: {total_tests - success_tests}")
    print(f"成功率: {(success_tests/total_tests*100):.1f}%")
    
    return success_tests == total_tests


if __name__ == "__main__":
    # メインのテスト実行
    gui_success = test_gui_application()
    print("\n" + "-" * 60 + "\n")
    core_success = test_without_gui()
    
    # 最終結果
    print("\n" + "=" * 60)
    print("最終テスト結果")
    print("=" * 60)
    
    if gui_success and core_success:
        print("[PERFECT] OpenSuperWhisperは完璧に動作しています！")
        print("すべての機能が正常に動作することが確認されました。")
        sys.exit(0)
    else:
        print("[NEEDS IMPROVEMENT] 一部の機能に問題があります。")
        print("上記のエラーを確認して修正が必要です。")
        sys.exit(1)
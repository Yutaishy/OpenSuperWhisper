# OpenSuperWhisper テストのベストプラクティス

## 作成日
2025年8月3日

## 効果的なテスト方法

### 1. 段階的アプローチ

#### Step 1: 依存関係確認
```python
# check_app.py
import sys
try:
    from PySide6.QtWidgets import QApplication
    print("[OK] PySide6 is installed")
    from OpenSuperWhisper.ui_mainwindow import MainWindow
    print("[OK] MainWindow can be imported")
except ImportError as e:
    print(f"[ERROR] {e}")
```

#### Step 2: コンポーネント単体テスト
```python
# test_realtime_quick.py
from OpenSuperWhisper.realtime_recorder import RealtimeRecorder
from OpenSuperWhisper.chunk_processor import ChunkProcessor

recorder = RealtimeRecorder()
processor = ChunkProcessor()
print("Components initialized successfully")
```

#### Step 3: 統合テスト（ヘッドレス）
```python
# test_headless_integration.py
# GUIなしで全機能をテスト
# 時間シミュレーションを使用
```

#### Step 4: GUI動作確認
```python
# verify_app.py
app = QApplication(sys.argv)
window = MainWindow()
# 詳細な状態確認
```

### 2. 時間シミュレーションテクニック

```python
# 長時間録音のシミュレーション
original_time = time.time
start_time = time.time()

for second in range(duration):
    simulated_time = start_time + second
    time.time = lambda: simulated_time
    # 音声データを追加
    
# 必ず元に戻す
time.time = original_time
```

### 3. デバッグ手法

#### 問題の特定
```python
# チャンクサイズが予期しない値の場合
def debug_chunk_creation():
    print(f"Time: {second}s, Chunk duration: {duration}s")
    print(f"Audio buffer size: {len(audio_data)}")
    print(f"Expected vs Actual: {expected}s vs {actual}s")
```

#### 段階的な修正
1. 問題を再現する最小限のテストを作成
2. デバッグ出力を追加
3. 原因を特定
4. 修正を実装
5. 再テストで確認

### 4. メモリ使用量の監視

```python
import psutil

def get_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

# テスト中に定期的に確認
print(f"Memory usage: {get_memory_usage():.1f}MB")
```

### 5. エラーハンドリング

#### 属性エラーの対処
```python
# 属性が存在しない場合の対処
if hasattr(window, 'record_btn'):
    print("Record button found")
else:
    print("Record button not found")

# または getattr を使用
chunk_id = getattr(recorder, 'chunk_id', 0)
```

#### import エラーの対処
```python
try:
    from module import Class
except ImportError:
    # 代替処理またはモック
    Class = Mock()
```

### 6. APIモックの作成

```python
# 実際のAPIを使わずにテスト
def mock_transcribe(audio_data):
    time.sleep(0.1)  # API遅延のシミュレーション
    return {
        "text": f"Test transcription for {len(audio_data)/16000:.1f}s audio"
    }

processor.asr_api.transcribe_audio = Mock(side_effect=mock_transcribe)
```

### 7. テスト結果の記録

```markdown
# test_results_summary.md
## テスト結果

### 1. コンポーネントテスト
**結果**: ✅ 成功
- 詳細...

### 2. 修正した問題
1. **問題**: チャンクが2.3秒になる
   **原因**: _find_optimal_split_point の実装
   **修正**: chunk_duration パラメータを追加
```

### 8. 継続的なテスト

```bash
# すべてのテストを順番に実行
python check_app.py && \
python test_realtime_quick.py && \
python test_chunk_creation.py && \
python test_long_recording.py && \
python test_headless_integration.py
```

### 9. よくある問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| Segmentation fault | GUI環境なし | ヘッドレステストを使用 |
| UnicodeEncodeError | cp932エンコーディング | ASCII文字のみ使用 |
| AttributeError | 属性名の変更 | hasattr()で確認 |
| Import Error | 依存関係不足 | pip install -r requirements.txt |

### 10. 推奨テストフロー

1. **開発時**
   - 単体テスト → 統合テスト → GUI確認

2. **デバッグ時**
   - 最小限の再現コード作成
   - print文でのデバッグ
   - 段階的な修正

3. **リリース前**
   - 全テストスイート実行
   - 長時間録音テスト
   - メモリリークチェック

## まとめ

効果的なテストには：
- 段階的なアプローチ
- 適切なモックの使用
- 詳細なログ出力
- エラーの適切な処理
- 結果の記録と共有

これらの手法により、OpenSuperWhisperのような複雑なアプリケーションでも確実な動作確認が可能になります。
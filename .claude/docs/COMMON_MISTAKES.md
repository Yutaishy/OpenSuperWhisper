# 繰り返しミス防止ガイド

作成日: 2025年8月3日

## 概要
OpenSuperWhisperプロジェクトで発生した繰り返しミスとその対策をまとめたガイド。
同じミスを二度と犯さないための自己記録システム。

## 1. 文字エンコーディングエラー

### ミス内容
```python
# NG: Windows環境でUnicodeエラー
print("✓ Success")  # UnicodeEncodeError: 'cp932' codec can't encode character
print("✗ Failed")
```

### 正しい対応
```python
# OK: ASCII文字のみ使用
print("[OK] Success")
print("[ERROR] Failed")
print("[INFO] Information")
print("[WARN] Warning")
```

### 予防策
- 常にASCII文字のみを使用
- 特殊文字は避ける
- 環境変数でUTF-8を設定

## 2. 属性名・メソッド名の間違い

### 発生したミス
```python
# NG: 存在しない属性
chunk.chunk_count  # → AttributeError

# NG: 間違ったメソッド名
self.check_and_process_retries()  # → AttributeError
```

### 正しい対応
```python
# OK: 正しい属性名
chunk.chunk_id

# OK: 正しいメソッド名
self.check_retries()
```

### 予防策
- 実装前にクラス定義を確認
- IDEの自動補完を活用
- エラー発生時は即座に属性を確認

## 3. MCPツール使用時の無応答問題

### ミス内容
- MCPツールが応答しないまま永久待機
- ユーザーがエスケープキーで中断する必要
- 特に`mcp__win-desktop__`系ツールで頻発

### 正しい対応
```python
# 3秒ルールを適用
try:
    # MCPツールは最大3秒で判断
    result = mcp_tool_with_timeout(operation, timeout=3)
except TimeoutError:
    # 即座に代替手段を使用
    result = alternative_method()
```

### 予防策
- MCPツールには必ずタイムアウトを設定
- 代替手段を事前に用意
- 危険なMCP操作は避ける

## 4. チャンク分割ロジックの誤解

### ミス内容
```python
# NG: 小さなチャンクを作成してしまう
def _find_optimal_split_point(self, audio_data):
    # 音声の最初の無音部分で分割 → 2.3秒のチャンク
    return silence_start_position
```

### 正しい対応
```python
# OK: 適切なチャンク長を維持
def _find_optimal_split_point(self, audio_data, chunk_duration=None):
    if chunk_duration and chunk_duration >= self.SILENCE_CHECK_START:
        # 無音検出による長いチャンクは全体を使用
        return len(audio_data)
```

### 予防策
- チャンク長の要件を明確に理解
- テストでチャンク長を検証
- ユーザー要件（60-120秒）を常に意識

## 5. GUIアプリケーションの起動方法

### ミス内容
```bash
# NG: Bashでの直接実行（Segmentation fault）
python OpenSuperWhisper/ui_mainwindow.py
```

### 正しい対応
```python
# OK: MCPツールでの適切な起動
mcp__win-desktop__run(program="full_path_to_python.exe run_app.py")
```

### 予防策
- GUIアプリは専用ツールで起動
- フルパスを使用
- 環境依存の処理を理解

## 6. パス指定の間違い

### ミス内容
```python
# NG: 相対パスでの問題
path = "./OpenSuperWhisper/file.py"  # 実行ディレクトリ依存
```

### 正しい対応
```python
# OK: 絶対パスまたは__file__ベース
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base_dir, "OpenSuperWhisper", "file.py")
```

### 予防策
- 常に絶対パスを使用
- os.path.joinで安全に結合
- パス存在確認を実施

## 7. テストでの条件確認不足

### ミス内容
```python
# NG: 条件確認が不十分
assert len(chunks) > 0  # チャンク数のみ確認
```

### 正しい対応
```python
# OK: 包括的な条件確認
assert len(chunks) > 0, "チャンクが作成されていません"
assert all(len(chunk.audio_data) > min_size for chunk in chunks), "チャンクサイズが小さすぎます"
assert sum(len(chunk.audio_data) for chunk in chunks) == len(original_audio), "音声データが欠損しています"
```

### 予防策
- テストは多角的に検証
- 期待値を明確に設定
- エラーメッセージを具体的に

## 8. リアルタイムモード設定忘れ

### ミス内容
```python
# NG: リアルタイムモードが無効のまま
self.realtime_mode = False  # デフォルトが無効
```

### 正しい対応
```python
# OK: リアルタイムモードをデフォルトで有効
self.realtime_mode = True
self.initialize_realtime_components()
```

### 予防策
- プロジェクト要件を常に確認
- デフォルト設定を適切に
- 初期化処理を忘れずに

## 9. 作業中断のタイミング

### ミス内容
- テスト途中で停止してしまう
- エラー修正→テストのサイクルを完了しない
- ユーザーの「つづけて」指示を無視

### 正しい対応
- テスト→エラー→修正→テストのサイクルを完遂
- 完全に動作するまで継続
- 中断は明確な指示がある場合のみ

### 予防策
- タスクの完了条件を明確化
- 途中停止しない意識を持つ
- プロセス全体を見通す

## 10. ログ出力での情報不足

### ミス内容
```python
# NG: 不十分なログ情報
print("Error occurred")
```

### 正しい対応
```python
# OK: 詳細なログ情報
print(f"[ERROR] チャンク処理でエラー: {error_details}")
print(f"[INFO] チャンク数: {len(chunks)}, 合計時間: {total_duration}s")
```

### 予防策
- ログレベルを明確に
- 具体的な値を含める
- デバッグに必要な情報を出力

## 11. Windows一時ファイルのロック問題

### ミス内容
```python
# NG: ファイルハンドルを閉じる前に削除
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
    # WAVファイル書き込み
    raw_text = asr_api.transcribe_audio(tmp_file.name)
    os.unlink(tmp_file.name)  # WinError 32: プロセスはファイルにアクセスできません
```

### 正しい対応
```python
# OK: ファイルハンドルを確実に閉じてからリトライ付きで削除
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
    tmp_filename = tmp_file.name
    # WAVファイル書き込み

try:
    raw_text = asr_api.transcribe_audio(tmp_filename)
finally:
    # リトライ付き削除
    for i in range(5):
        try:
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)
            break
        except:
            if i < 4:
                time.sleep(0.5)
```

### 予防策
- Windowsでは`with`ブロックを出てからファイル削除
- リトライロジックを実装
- try-finallyで確実なクリーンアップ

## まとめ

### 重要な教訓
1. **文字エンコーディング**: ASCII文字のみ使用
2. **MCP無応答**: 3秒ルール + 代替手段
3. **属性・メソッド**: 実装前に定義確認
4. **チャンク処理**: ユーザー要件を正確に理解
5. **継続性**: 完了まで中断しない
6. **Windowsファイル処理**: リトライ付き削除

### 自己チェックリスト
- [ ] Unicode文字を使用していないか？
- [ ] MCPツールにタイムアウトを設定したか？
- [ ] 属性名・メソッド名を確認したか？
- [ ] チャンク長が要件を満たしているか？
- [ ] テストが完全に通るまで継続したか？

### 記録更新ルール
新しいミスが発生した場合：
1. 即座にこのファイルに追記
2. 原因と解決策を明記
3. 予防策を考案
4. チェックリストを更新

**重要**: このガイドを定期的に見直し、同じミスを二度と犯さないよう徹底する。

## 12. AttributeError対策不足

### ミス内容
```python
# NG: hasattrチェックなしでアクセス
self.chunk_processor.shutdown()
self.recording_status.setText("Complete")
```

### 正しい対応
```python
# OK: 常にhasattrでチェック
if hasattr(self, 'chunk_processor') and self.chunk_processor:
    self.chunk_processor.shutdown()
if hasattr(self, 'recording_status'):
    self.recording_status.setText("Complete")
```

### 予防策
- すべての属性アクセスにhasattrチェック
- try-exceptで包括的エラーハンドリング
- エラー発生時もUIの一貫性を保つ

## 13. コールバック処理のエラー伝播

### ミス内容
```python
# NG: コールバック内のエラーが親処理をクラッシュ
def check_realtime_completion(self):
    # エラーが発生するとアプリ全体がクラッシュ
    self.chunk_processor.combine_results()  # AttributeError
```

### 正しい対応
```python
# OK: コールバック内で完全なエラーハンドリング
def check_realtime_completion(self):
    try:
        if hasattr(self, 'chunk_processor') and self.chunk_processor:
            raw_combined, formatted_combined = self.chunk_processor.combine_results()
    except Exception as e:
        logger.logger.error(f"Error: {e}")
        import traceback
        logger.logger.error(traceback.format_exc())
        # エラーでも処理を継続
        self.complete_realtime_processing()
```

### 予防策
- すべてのコールバックでtry-except
- トレースバック情報も記録
- エラー時も次の処理へ進む

## 14. GUIスレッドセーフティ違反

### ミス内容
```python
# NG: ワーカースレッドから直接GUI操作
def on_chunk_completed(self, chunk_id, result):
    self.raw_text_edit.setPlainText(result.raw_text)  # クラッシュ
```

### 正しい対応
```python
# OK: シグナルを使ってメインスレッドで更新
class MainWindow(QMainWindow):
    chunk_update_signal = Signal(int, str, str, str, str)
    
    def __init__(self):
        self.chunk_update_signal.connect(self._handle_chunk_update_signal)
    
    def on_chunk_completed(self, chunk_id, result):
        # シグナル経由で更新
        self.chunk_update_signal.emit(chunk_id, "completed", result.raw_text, "", "")
    
    def _handle_chunk_update_signal(self, chunk_id, status, raw_text, formatted_text, error):
        # メインスレッドで安全にGUI更新
        self.raw_text_edit.setPlainText(raw_text)
```

### 予防策
- Qt/PySideではGUI操作は必ずメインスレッドで
- ワーカースレッドからはシグナル経由
- コールバックがどのスレッドで実行されるか確認
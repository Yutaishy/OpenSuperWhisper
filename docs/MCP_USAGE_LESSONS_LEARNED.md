# MCP使用時の教訓とエラー対処法

## 作成日
2025年8月3日

## 概要
OpenSuperWhisperのテスト中にMCPツール使用で遭遇した問題と解決策をまとめました。

## 1. MCP win-desktop ツールの応答問題

### 問題
```python
# これらのコマンドが応答を返さない、または永久に待機する
mcp__win-desktop__winGetPos(title="OpenSuperWhisper")
mcp__win-desktop__winExists(title="SuperWhisper") 
mcp__win-desktop__processExists(process="python.exe")
mcp__win-desktop__run(program="python", ...)
```

### 原因
- MCPツールが応答を返さない場合がある
- 特にGUIアプリケーションの操作時に発生
- エラーも成功も返さず、永久に待機状態になる

### 解決策
1. **通常のBashコマンドを優先使用**
```bash
# MCPの代わりにこれらを使用
tasklist | findstr python
cmd /c start program.exe
```

2. **タイムアウトを想定した代替手段を用意**
```python
# MCPが応答しない場合の代替確認方法
python check_app.py  # 自作の確認スクリプト
```

## 2. GUI アプリケーションの起動確認

### 問題
- Windowsデスクトップアプリの起動状態が確認できない
- ウィンドウタイトルの検索が機能しない

### 解決策
```python
# 検証用スクリプトを作成して確認
def verify_functionality():
    app = QApplication(sys.argv)
    window = MainWindow()
    print(f"Window title: {window.windowTitle()}")
    print(f"Is visible: {window.isVisible()}")
    # 詳細な状態確認
```

## 3. 文字エンコーディング問題

### 問題
```python
print("✓ OK")  # UnicodeEncodeError: 'cp932' codec can't encode character
```

### 解決策
```python
# Unicode文字を使わない
print("[OK] Success")
print("[ERROR] Failed")
print("[INFO] Information")
```

## 4. プロセス起動の問題

### 問題
```bash
# これらが期待通り動作しない
start python app.py  # bashでは動作しない
cmd /c start app.py  # パスの問題
```

### 解決策
```bash
# バッチファイルを作成
@echo off
cd C:\path\to\app
python app.py
pause

# 実行
cmd /c start batch.bat
```

## 5. MCP Playwright の使用

### 成功例
```python
# Webアプリケーションの場合は正常動作
mcp__playwright__browser_navigate(url="http://localhost:8000")
```

### 注意点
- デスクトップGUIアプリには使用できない
- Webサーバーが起動していることを確認

## 6. 推奨されるテスト手順

### 1. 依存関係の確認
```python
# check_dependencies.py
try:
    import required_module
    print("[OK] Module available")
except ImportError as e:
    print(f"[ERROR] {e}")
```

### 2. ヘッドレステスト
```python
# GUIを表示せずに機能テスト
def test_headless():
    # コンポーネントの初期化と動作確認
    recorder = RealtimeRecorder()
    processor = ChunkProcessor()
    # テスト実行
```

### 3. 段階的な確認
1. モジュールのインポート確認
2. コンポーネントの初期化確認
3. 基本機能の動作確認
4. 統合テストの実施

## 7. エラー時の対処フロー

1. **MCPツールが応答しない場合**
   - 待たずに中断（Ctrl+C）
   - 代替手段（Bashコマンド）を使用
   - 自作の確認スクリプトを実行

2. **プロセスの確認**
   ```bash
   # Windows
   tasklist | findstr process_name
   
   # PowerShell（使える場合）
   Get-Process | Where-Object {$_.Name -like "*python*"}
   ```

3. **ログの活用**
   - アプリケーション内でログ出力を実装
   - エラー時は即座にログを確認

## 8. ベストプラクティス

1. **MCPツールは補助的に使用**
   - メインの処理はPythonスクリプトで実装
   - MCPは確認用途に限定

2. **エラーハンドリングを徹底**
   ```python
   try:
       # MCP操作
   except Exception as e:
       print(f"MCP failed: {e}")
       # 代替処理
   ```

3. **タイムアウトを設定**
   - 長時間待機を避ける
   - 代替手段を常に用意

4. **検証スクリプトの作成**
   - アプリケーション固有の確認スクリプト
   - 再利用可能な形で保存

## まとめ

MCPツールは便利だが、特にWindows環境でのGUIアプリケーション操作では制限がある。
- 基本的な処理は通常のPython/Bashで実装
- MCPは補助的な確認用途に使用
- エラー時は代替手段で対処
- 永久に待機する場合は即座に中断して別の方法を試す

この経験を活かして、より効率的なテストとデバッグが可能になります。
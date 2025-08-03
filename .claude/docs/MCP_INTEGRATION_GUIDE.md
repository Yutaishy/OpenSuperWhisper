# MCPツール統合ガイド

## 概要

OpenSuperWhisperプロジェクトでMCPツールを安全に使用するためのガイド。
MCPの無応答問題を根本的に解決し、効率的な開発を実現します。

## MCP無応答問題の解決

### 実装した解決策

1. **3秒タイムアウトルール**
   - MCPツールが3秒以内に応答しない場合は自動中断
   - ユーザーの長時間待機を防止

2. **自動フォールバック**
   - MCP失敗時は即座に代替手段を実行
   - Bashコマンドやシステムツールを活用

3. **プロアクティブエラー回避**
   - 危険なMCP操作は事前チェック
   - 安全な操作のみを実行

### 適用例

#### プロセス確認
```python
# 危険: 無応答の可能性
mcp__win-desktop__processExists(process="python.exe")

# 安全: タイムアウト付き + フォールバック
def check_python_process():
    try:
        # 3秒タイムアウトでMCPを試行
        return safe_mcp_with_timeout(
            lambda: mcp__win-desktop__processExists(process="python.exe"),
            timeout=3
        )
    except TimeoutError:
        # フォールバック: Bashコマンド
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        return 'python.exe' in result.stdout
```

#### ウィンドウ操作
```python
# 危険: 長時間ハングの可能性
mcp__win-desktop__winGetPos(title="OpenSuperWhisper")

# 安全: 代替手段優先
def check_app_window():
    # 直接プロセス確認で代替
    import psutil
    for proc in psutil.process_iter(['name', 'cmdline']):
        if 'python.exe' in proc.info['name']:
            cmdline = proc.info['cmdline']
            if cmdline and 'run_app.py' in ' '.join(cmdline):
                return True
    return False
```

## 開発時のMCP使用方針

### 推奨されるMCP操作
1. **ファイル操作**: 通常のPythonツールで実行
2. **プロセス確認**: Bashコマンド優先
3. **Web操作**: Playwright MCPは安定

### 避けるべきMCP操作
1. **win-desktop__processExists**: しばしば無応答
2. **win-desktop__winGetPos**: ハングしやすい
3. **win-desktop__run**: 予期しない動作

### ベストプラクティス

#### 1. MCPは補助的に使用
```python
# メイン処理は通常のPython
import subprocess
result = subprocess.run(['python', 'script.py'], capture_output=True)

# MCPは確認・検証のみ
if need_verification:
    mcp_result = safe_mcp_operation()
```

#### 2. 必ず代替手段を用意
```python
def robust_operation():
    # 1次: MCP（タイムアウト付き）
    # 2次: システムコマンド
    # 3次: Python標準ライブラリ
    pass
```

#### 3. エラーログの記録
```python
def mcp_with_logging(operation_name, mcp_func, fallback_func):
    try:
        result = mcp_func()
        log_success(operation_name, "MCP")
        return result
    except TimeoutError:
        log_fallback(operation_name, "MCP timeout")
        return fallback_func()
```

## テスト環境での注意点

### GUI無効環境
- PySide6アプリはheadlessモードでテスト
- MCPのwin-desktopツールは使用不可
- システムコマンドでの代替必須

### CI/CD環境
- MCPツールは基本的に利用不可
- 全ての操作で代替手段を実装
- テスト時はモック使用を推奨

## 実装チェックリスト

- [ ] MCPツールにタイムアウト設定（3秒）
- [ ] 代替手段の実装
- [ ] エラーログの記録
- [ ] テスト環境での動作確認
- [ ] CI/CDでの動作確認

## 今後の改善

1. **自動化ツールの作成**
   - MCP操作を自動的に安全化
   - 代替手段の自動生成

2. **監視システム**
   - MCP操作の成功率監視
   - 問題のあるツールの特定

3. **ドキュメント更新**
   - 新しいエラーパターンの記録
   - 解決策の共有

この統合により、MCPツールの利点を活かしながら、安定した開発環境を実現できます。
# OpenSuperWhisper プロジェクトガイド

## プロジェクト概要
音声認識（Whisper）とテキスト整形（GPT）の2段階パイプラインを持つデスクトップアプリケーション。

## 重要ファイル
- `OpenSuperWhisper/formatter_api.py`: GPTモデル呼び出し
- `OpenSuperWhisper/ui_mainwindow.py`: UI制御
- `tests/`: テストスイート
- `build_executable.py`: ビルド設定

## OpenAI API 実装ガイド

### ChatGPT UI vs API の違い

| ChatGPT UI | API実装 | 備考 |
|------------|---------|------|
| o4-mini-high | model:"o4-mini" + reasoning_effort:"high" | v0.6.12で学習 |
| o4-mini | model:"o4-mini" | 標準推論モデル |
| gpt-4o | model:"gpt-4o" | 汎用モデル |

### パラメータ制限

**GPT系（gpt-4, gpt-4o等）**
- ✅ temperature, max_tokens, top_p 設定可能

**o系推論モデル（o1, o3, o4等）**
- ❌ temperature 設定不可（エラー400）
- ✅ max_tokens のみ設定可能
- ✅ o4系のみ reasoning_effort 対応

### 実装パターン

```python
# formatter_api.py の正しい実装
def format_text(raw_text: str, prompt: str, style_guide: str = "", model: str = "gpt-4o-mini") -> str:
    # o4-mini-high特別処理
    actual_model = model
    if model == "o4-mini-high":
        actual_model = "o4-mini"
    
    api_params = {
        "model": actual_model,
        "messages": [system_message, user_message]
    }
    
    # o4-mini-highにreasoning_effort追加
    if model == "o4-mini-high":
        api_params["reasoning_effort"] = "high"
    
    # GPT系のみtemperature設定
    if model in ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]:
        api_params["temperature"] = 0.0
```

## リリースプロセス

### 基本フロー（9フェーズ）
1. **問題分析** → エラー詳細記録・原因特定
2. **修正実装** → コード修正・テスト作成
3. **ドキュメント更新** → バージョン番号・CHANGELOG
4. **リポジトリ整備** → キャッシュ削除・クリーンアップ
5. **コミット・プッシュ** → 詳細メッセージでコミット
6. **CI/CD監視** → GitHub Actions確認
7. **リリース作成** → タグ作成・プッシュ
8. **リリース整備** → リリースノート作成
9. **最終検証** → ダウンロードリンク確認

### 重要コマンド
```bash
# テスト実行
python -m pytest tests/ -v

# linting
ruff check . --fix

# バージョン確認
python run_app.py --version

# CI/CD監視
gh run list --limit 3
gh run watch <RUN_ID>

# リリース作成
git tag v0.6.12
git push origin v0.6.12
```

## デバッグパターン

### APIエラー対処
1. **404エラー**: モデルID確認 → 公式ドキュメント参照
2. **400エラー**: パラメータ確認 → モデル別制限チェック
3. **解決手順**: エラー記録 → WebSearch → モックテスト → 実装

### CI/CDエラー対処
```bash
# lintingエラー確認
ruff check . --show-source

# 自動修正
ruff check --fix .

# 追加コミット
git add -u && git commit -m "Fix linting errors"
```

## Geminiとの協調開発

### 効果的な使い方
```bash
# API仕様確認
gemini -p "OpenAI o4-miniのtemperatureパラメータについて"

# エラー相談
gemini -p "Error code 400の解決方法"
```

### 注意点
- Geminiの提案は参考程度に
- 必ず公式ドキュメントで確認
- 最終判断はClaude Codeが行う

## 今後の改善提案

1. **設定の外部化**
   - モデル設定をJSONで管理
   - APIパラメータの動的制御

2. **エラーハンドリング強化**
   - より詳細なエラーメッセージ
   - 自動リトライ機能

3. **テスト拡充**
   - 全モデルの動作確認
   - エッジケースカバー

記録日: 2025-01-30
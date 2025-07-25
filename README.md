# Open Super Whisper

## 2段構成の概要（A案）

本プロジェクトは音声認識 (ASR) とテキスト整形 (o4-mini) の 2 段構成で音声入力を高速に文字起こしします。

1. ASR: OpenAI の `whisper-1`, `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` から選択
2. Post-formatter: Chat Completions API 経由で `o4-mini` モデルを用い、日本語文体を自動推定しながら整形

## ビルド方法（uv + PyInstaller）

```powershell
# 依存パッケージのインストール
uv pip install -r requirements.txt

# バイナリのビルド
uv run pyinstaller --onefile ^
    --add-data "assets/prompts;assets/prompts" ^
    --add-data "project_styles;project_styles" ^
    src/cli.py
```

> Windows では上記コマンドで `dist/open-super-whisper.exe` が生成されます。 

## 開発環境セットアップ

```powershell
# 依存パッケージ + 開発ツール
uv pip install -r requirements.txt
uv pip install -r dev-requirements.txt  # 任意: dev 依存を分けている場合

# pre-commit フックをインストール
uv run pre-commit install
``` 

## 操作フロー

1. アプリを起動し、`Open Audio` ボタンで音声ファイル (wav/mp3 等) を選択
2. ASR が実行され、Raw タブに素のテキストが表示
3. PostFormatter が動作し、Formatted タブに整形済みテキストが表示
4. 語彙候補が抽出された場合は自動でダイアログが開き、承認可能
5. ログは `logs/<session_id>/` ディレクトリに自動保存

> 詳細設定はメニューバーの `Settings` から変更できます。 
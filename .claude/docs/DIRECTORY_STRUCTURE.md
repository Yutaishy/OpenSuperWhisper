# ディレクトリ構造説明

## 整理完了後の構造（2025年8月3日更新）

```
voice_input_v2/
├── .claude/                          # プロジェクト管理（Claude Code専用）
│   ├── CLAUDE.md                     # プロジェクト指針とドキュメント一覧
│   └── docs/                         # プロジェクト専用ドキュメント
│       ├── INDEX.md                  # ドキュメント目次
│       ├── PROJECT_OVERVIEW.md       # プロジェクト概要
│       ├── DIRECTORY_STRUCTURE.md    # ディレクトリ構造（本ファイル）
│       ├── INSTALLATION_GUIDE.md     # インストールガイド
│       ├── USAGE_GUIDE.md            # 使用方法
│       ├── DEVELOPMENT_GUIDE.md      # 開発ガイド
│       ├── TESTING_GUIDE.md          # テスト実行方法
│       ├── TROUBLESHOOTING.md        # トラブルシューティング
│       ├── API_REFERENCE.md          # API仕様
│       ├── CHANGELOG.md              # 変更履歴
│       ├── MCP_INTEGRATION_GUIDE.md  # MCPツール統合ガイド
│       └── COMMON_MISTAKES.md        # 繰り返しミス防止ガイド
│
├── OpenSuperWhisper/                 # メインアプリケーション
│   ├── __init__.py                   # パッケージ初期化
│   ├── ui_mainwindow.py             # メインGUIウィンドウ
│   ├── asr_api.py                   # 音声認識API
│   ├── formatter_api.py             # テキスト整形API
│   ├── config.py                    # 設定管理
│   ├── realtime_recorder.py         # リアルタイム録音（新機能）
│   ├── chunk_processor.py           # チャンク処理（新機能）
│   ├── retry_manager.py             # リトライ管理（新機能）
│   ├── cancel_handler.py            # キャンセル処理（新機能）
│   ├── recording_indicator.py       # 録音インジケーター
│   ├── logger.py                    # ログ管理
│   ├── security.py                  # セキュリティ機能
│   ├── web_api.py                   # Web API
│   ├── global_hotkey.py             # グローバルホットキー
│   ├── simple_hotkey.py             # シンプルホットキー
│   ├── direct_hotkey.py             # ダイレクトホットキー
│   └── first_run.py                 # 初回実行設定
│
├── docs/                            # プロジェクトドキュメント（元からあるもの）
│   ├── MCP_USAGE_LESSONS_LEARNED.md
│   ├── REALTIME_TRANSCRIPTION_IMPLEMENTATION_LOG.md
│   ├── REALTIME_TRANSCRIPTION_PHASE3_SUMMARY.md
│   ├── REALTIME_TRANSCRIPTION_REQUIREMENTS.md
│   ├── REALTIME_TRANSCRIPTION_REQUIREMENTS_CHANGELOG.md
│   ├── REALTIME_TRANSCRIPTION_TEST_PLAN.md
│   ├── REALTIME_TRANSCRIPTION_VALIDATION.md
│   └── TESTING_BEST_PRACTICES.md
│
├── tests/                           # 公式テストスイート
│   ├── __init__.py
│   ├── test_asr_api.py             # ASR APIテスト
│   ├── test_config.py              # 設定テスト
│   ├── test_formatter_api.py       # フォーマッターAPIテスト
│   ├── test_integration.py         # 統合テスト
│   ├── test_realtime_integration.py # リアルタイム統合テスト
│   ├── test_e2e_realtime.py        # E2Eリアルタイムテスト
│   ├── quick_test.py               # クイックテスト
│   ├── performance_profiler.py     # パフォーマンス分析
│   └── test_summary.md             # テスト結果サマリー（統合版）
│
├── archive/                         # アーカイブ（整理で移動したファイル）
│   ├── test_files/                  # 開発中のテスト・デバッグファイル
│   │   ├── check_app.py
│   │   ├── debug_app.py
│   │   ├── test_app_launch.py
│   │   ├── test_chunk_creation.py
│   │   ├── test_debug_silence.py
│   │   ├── test_full_integration.py
│   │   ├── test_gui_realtime.py
│   │   ├── test_headless_integration.py
│   │   ├── test_long_recording.py
│   │   ├── test_mainwindow.py
│   │   ├── test_pyside.py
│   │   ├── test_realtime_quick.py
│   │   ├── test_recording_simulation.py
│   │   ├── test_simple_flow.py
│   │   ├── test_results_summary.md   # 旧テスト結果
│   │   └── verify_app.py
│   ├── old_logs/                    # 古いログファイル
│   │   └── logs/
│   │       ├── 2025-08-02.log
│   │       └── 2025-08-03.log
│   ├── current_logs/                # 現在のログファイル（一時的）
│   │   └── 2025-08-03.log
│   ├── npm_cache/                   # npmキャッシュ
│   │   └── %APPDATA%/               # 移動したnpmキャッシュ
│   ├── dev_reports/                 # 開発レポート
│   │   ├── DIRECTORY_CLEANUP_REPORT.md
│   │   ├── FINAL_VALIDATION_REPORT.md
│   │   └── MANUAL_TEST_GUIDE.md
│   └── temp_files/                  # 一時ファイル
│
├── assets/                          # アプリケーション素材
│   ├── android/                     # Androidアイコン
│   ├── ios/                         # iOSアイコン
│   ├── misc/                        # その他素材
│   ├── web/                         # Webアイコン
│   └── windows/                     # Windowsアイコン
│
├── brand/                           # ブランド素材
│   └── icon/                        # アイコンファイル
│       ├── LICENSE-ARTWORK.md
│       └── wave-quote/
│
├── style_guides/                    # スタイルガイド
│   ├── example_style.json
│   └── example_style.yaml
│
├── run_app.py                       # メイン起動スクリプト（統一版）
├── web_server.py                    # Webサーバー起動
├── build_executable.py             # 実行ファイルビルド
├── requirements.txt                 # 依存パッケージ
├── requirements-docker.txt         # Docker用依存
├── pyproject.toml                  # プロジェクト設定
├── Dockerfile                      # Docker設定
├── README.md                       # プロジェクト説明
├── CHANGELOG.md                    # 変更履歴
├── LICENSE                         # ライセンス
├── SECURITY.md                     # セキュリティ方針
├── CODE_OF_CONDUCT.md             # 行動規範
└── CONTRIBUTING.md                # 貢献ガイド
```

## 整理内容（2025年8月3日実施）

### アーカイブしたファイル
- **npmキャッシュ**: `%APPDATA%/` → `archive/npm_cache/`
- **テストログ**: `tests/logs/` → `archive/old_logs/logs/`
- **開発用テストファイル**: ルートの `test_*.py` → `archive/test_files/`
- **テスト結果サマリー**: `test_results_summary.md` → `archive/test_files/`

### マージ・統一したファイル
- **テストサマリー**: 2つのサマリーファイルを `tests/test_summary.md` に統合
  - 2025年8月2日と8月3日の結果を時系列で整理
  - エラー修正履歴とパフォーマンス測定を追加

### 構造の最適化
- **tests/logs/** ディレクトリを削除（ログはarchiveで一元管理）
- **開発用テストファイル**と**公式テストスイート**を明確に分離

## ディレクトリの役割

### コアディレクトリ
- **OpenSuperWhisper/**: メインアプリケーションコード
- **tests/**: 公式テストスイート（保守対象）
- **.claude/**: プロジェクト管理（Claude Code専用）

### サポートディレクトリ
- **docs/**: プロジェクトドキュメント（元からあるもの）
- **assets/**: アプリケーション素材
- **archive/**: 整理で移動したファイル（定期的に見直し）

### 設定ファイル
- **pyproject.toml**: プロジェクト設定とメタデータ
- **requirements*.txt**: 依存パッケージ管理
- **Dockerfile**: Docker環境設定

## メンテナンス指針

1. **新機能追加**: 
   - コード: `OpenSuperWhisper/` 内に追加
   - テスト: `tests/` に公式テストを作成
   - ドキュメント: `.claude/docs/` に記録

2. **開発中のファイル**:
   - 一時的なテスト: `archive/test_files/` に保存
   - デバッグ用スクリプト: 完了後は `archive/` へ

3. **ログファイル**:
   - すべて `archive/old_logs/` で管理
   - 本番環境のログは別管理

4. **定期クリーンアップ**:
   - `archive/` ディレクトリを3ヶ月ごとに見直し
   - 不要なファイルは完全削除

5. **ドキュメント更新**:
   - 構造変更時は本ファイルを更新
   - `.claude/docs/` 内のドキュメントも同期

この構造により、プロジェクトが整然と管理され、新機能開発と保守が効率的に行えます。
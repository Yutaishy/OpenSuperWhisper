# OpenSuperWhisper プロジェクト管理

本ファイルはOpenSuperWhisperプロジェクトの**行動指針**と**docs/**への**リンク集**のみを記載する。
**200字超**または**コードブロック**を含む追記は、**docs/**に新規ファイルを作成し、ここには**1行リンクのみ**を追加する。

## プロジェクト概要
リアルタイム音声文字起こしアプリケーション。10分以上の長時間録音対応、チャンクベース処理による効率化。v0.6.13

## ドキュメント一覧
@docs/INDEX.md                              # 目次（自動生成）
@docs/PROJECT_OVERVIEW.md                   # プロジェクト概要
@docs/DIRECTORY_STRUCTURE.md                # ディレクトリ構造説明
@docs/INSTALLATION_GUIDE.md                 # インストールガイド
@docs/USAGE_GUIDE.md                        # 使用方法
@docs/DEVELOPMENT_GUIDE.md                  # 開発ガイド
@docs/TESTING_GUIDE.md                      # テスト実行方法
@docs/TROUBLESHOOTING.md                    # トラブルシューティング
@docs/API_REFERENCE.md                      # API仕様
@docs/CHANGELOG.md                          # 変更履歴
@docs/MCP_INTEGRATION_GUIDE.md              # MCPツール統合ガイド
@docs/COMMON_MISTAKES.md                    # 繰り返しミス防止ガイド

## 重要原則
1. リアルタイムモードをデフォルトで有効
2. チャンクベース処理（60-120秒）を維持
3. メモリ効率を最優先
4. エラーハンドリングを徹底

## 自動記録ルール
### プロジェクト固有の知識管理
1. **新機能追加時は必ず記録**
   - 場所: `.claude/docs/CHANGELOG.md`
   - 形式: バージョン→機能→詳細
2. **バグ修正時は必ず記録**
   - 場所: `.claude/docs/TROUBLESHOOTING.md`
   - 形式: 問題→原因→解決策
3. **パフォーマンス改善時は記録**
   - 場所: `.claude/docs/DEVELOPMENT_GUIDE.md`
   - 形式: 改善前→改善後→効果
4. **テスト追加・修正時は記録**
   - 場所: `.claude/docs/TESTING_GUIDE.md`
   - 形式: テスト内容→結果→改善点
5. **自分のミス発生時は必ず記録**
   - 場所: `.claude/docs/COMMON_MISTAKES.md`
   - 形式: ミス内容→正しい対応→予防策
   - タイミング: エラー解決直後に記録

## 起動方法
```bash
python run_app.py
```

## リマインダー
- MCP無応答時は3秒で中断、代替手段を使用
- テスト実行時はheadlessモードを活用
- 新機能実装時は必ずテストも作成
- プロジェクト固有の知識は.claude/docsに記録

---
更新日: 2025年8月3日
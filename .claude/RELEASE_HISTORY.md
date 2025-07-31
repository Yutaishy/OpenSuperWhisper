# OpenSuperWhisper リリース履歴

## v0.6.12 (2025-01-30) - Critical Hotfix

### 問題と解決
**問題1**: o4-mini-highモデルで404エラー
- **原因**: ChatGPT UIの表示名をAPIで直接使用
- **解決**: `model:"o4-mini" + reasoning_effort:"high"`に変換

**問題2**: o系モデルで400エラー（temperature）
- **原因**: 推論モデルはtemperature非対応
- **解決**: GPT系のみtemperature設定

### 実装詳細
```python
# formatter_api.py の修正
if model == "o4-mini-high":
    actual_model = "o4-mini"
    api_params["reasoning_effort"] = "high"

# temperatureはGPT系のみ
if model in ["gpt-4o-mini", "gpt-4o", ...]:
    api_params["temperature"] = 0.0
```

### 学んだ教訓
1. **ChatGPT UI ≠ OpenAI API**: 表示名とAPIパラメータは別物
2. **モデル別制限**: o系は確定的、GPT系は確率的
3. **エラーから学ぶ**: 404=モデルID誤り、400=パラメータ誤り
4. **ユーザー対応**: 「勝手に消すな」→即座に方針転換

### タイムライン
- 10:00 録音時間延長要望（60→600秒）
- 10:30 o4-mini-high追加要望
- 11:00 APIエラー発生
- 12:00 正しい実装方法発見
- 13:00 リリースプロセス開始
- 14:00 v0.6.12リリース完了

### リリースプロセス特記事項
- lintingエラー（trailing whitespace）で追加コミット必要
- 9フェーズ全て完了（約1時間）
- .claude/ディレクトリ作成でナレッジ管理開始

---

## v0.6.11 (2025-01-30)

### 新機能
- 録音時間制限を60秒から600秒（10分）に拡張
- o4-mini-highモデルのサポート追加（UI上）

### 問題点
- o4-mini-highがAPIエラーを引き起こす
- → v0.6.12で緊急修正

---

## 今後の課題

1. **API互換性の事前検証**
   - 新モデル追加前にAPIドキュメント確認
   - モックテストでパラメータ検証

2. **設定の外部化**
   ```json
   {
     "models": {
       "o4-mini-high": {
         "api_model": "o4-mini",
         "params": {"reasoning_effort": "high"}
       }
     }
   }
   ```

3. **エラーハンドリング改善**
   - APIエラーの詳細表示
   - ユーザーへの分かりやすい通知

記録日: 2025-01-30
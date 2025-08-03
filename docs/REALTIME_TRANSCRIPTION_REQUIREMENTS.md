# リアルタイム文字起こし機能 要件定義書

## 1. 概要

### 1.1 何を作るのか
現在の「録音→完了後に一括処理」から「録音しながら逐次処理・表示」に変更する機能。

### 1.2 なぜ作るのか
- **問題1**: 10分を超える録音ができない → **解決**: チャンクに分けて処理
- **問題2**: 録音が終わるまで結果が見えない → **解決**: 処理済みから順次表示
- **問題3**: 長時間録音でメモリ不足になる → **解決**: 処理済みチャンクを解放

## 2. 動作仕様（これが全て）

### 2.1 録音の分割ルール（改善版）
```
録音開始
↓
1分経過するまで: 何もしない（録音継続）
↓
1分～1分30秒: まだ何もしない（録音継続）
↓
1分30秒経過後: 無音検出を開始
  → 1.5秒以上無音が続いたら: 音韻境界を考慮して分割
  → 無音がない場合: 録音継続
↓
1分50秒経過: 優先分割ポイント検索
  → 0.5秒以上の無音: そこで分割
  → 無音がない: 音量最小点で分割
↓
2分経過: ゼロクロッシング点で強制分割（音の途切れ最小化）
↓
最初に戻る（次のチャンクを録音開始）
```

#### 音韻境界の考慮（技術詳細）
```python
def find_optimal_split_point(audio_data, target_time):
    # target_time の前後0.5秒を探索範囲とする
    # 優先順位:
    # 1. 1.5秒以上の無音区間の中央
    # 2. 0.5秒以上の無音区間の中央
    # 3. 振幅が最小の地点
    # 4. ゼロクロッシング点（音波が0を横切る点）
    # 5. どれも見つからない場合のみtarget_timeで分割

def calculate_overlap_duration(self, language="ja"):
    # 言語によってオーバーラップ時間を調整
    overlap_durations = {
        "ja": 0.8,  # 日本語：文節を考慮
        "en": 0.5,  # 英語：単語境界を考慮
        "default": 0.6
    }
    return overlap_durations.get(language, 0.6)
```

### 2.2 具体的な動作例
```
例1: 2分30秒話し続けた場合
- 0:00-2:00.5 → チャンク1（2分で強制分割+0.5秒オーバーラップ）
- 1:59.5-2:30 → チャンク2（0.5秒重複開始、録音終了時に送信）

例2: 1分35秒で3秒黙った場合  
- 0:00-1:35.5 → チャンク1（1.5秒無音で分割+0.5秒オーバーラップ）
- 1:35-録音終了 → チャンク2（0.5秒重複開始）

例3: 50秒で終了した場合
- 0:00-0:50 → チャンク1（1分未満なので分割なし）
```

### 2.3 チャンク境界のオーバーラップ処理
```
目的: 文脈の継続性確保と単語途切れ防止

実装:
- 各チャンクの終端に0.8秒追加（日本語の場合）
- 次チャンクの開始を0.8秒前から
- 重複部分のテキストは高度なアルゴリズムで検出・除去

例: 「今日は晴れています。明日も晴れるでしょう。」
チャンク1: 「今日は晴れています。明日も」（←0.8秒延長）
チャンク2: 「います。明日も晴れるでしょう。」（←0.8秒前から）
結合結果: 「今日は晴れています。明日も晴れるでしょう。」（重複除去）
```

## 3. UI仕様（画面の変更内容）

### 3.1 タブ名の変更
```
【現在】
┌─────────────────┬───────────────┐
│ Raw Transcription │ Formatted Text  │
└─────────────────┴───────────────┘

【変更後】  
┌─────────────────┬───────────────┐
│  Transcription    │ Formatted Text  │
└─────────────────┴───────────────┘
```

### 3.2 操作方法

#### 基本操作（キーボードショートカット）
- **Ctrl+Space**: 録音開始/停止（現状維持）
- **Esc**: 全処理の即時キャンセル（新規・最優先）
- **Ctrl+Shift+Space**: 一時停止/再開（将来実装）

#### Escキー（緊急停止）の詳細仕様
```
Escキーが押されたら（どの状態でも有効）:

1. 確認ダイアログの表示:
   「処理済みの結果を保存しますか？」
   [保存する] [破棄する] [キャンセル]

2. 「保存する」選択時:
   - 録音を停止
   - 新規API呼び出しを中止
   - 処理済みのテキストは保持
   - 処理中のチャンクは完了を待つ

3. 「破棄する」選択時:
   - 録音を即座に停止
   - すべてのAPI呼び出しをキャンセル
   - 処理待ちキューをクリア
   - すべての結果を破棄
   - 完全に初期状態に戻る

4. 「キャンセル」選択時:
   - Esc操作を取り消し
   - 録音/処理を継続
```

#### ポップアップの操作
- **録音中にクリック**: 録音停止（Ctrl+Spaceと同じ）
- **処理中にクリック**: 進捗詳細を表示
- **エラー時にクリック**: エラー詳細を表示
- **完了時にクリック**: メインウィンドウを表示

#### メインウィンドウでのキャンセル操作
```
┌─────────────────────────────────────────────┐
│ [Transcription] [Formatted Text]             │
├─────────────────────────────────────────────┤
│ 録音中のテキスト表示エリア                    │
│                                             │
│ [Escキーで全キャンセル]                      │
├─────────────────────────────────────────────┤
│ ⚠️ エラー (1件) [詳細] [クリア] [全キャンセル] │
└─────────────────────────────────────────────┘
```

### 3.3 Transcriptionタブの表示内容

#### 録音中の表示（リアルタイムモード）
```
┌─────────────────────────────────────┐
│ [00:00-01:35] ✓                     │
│ こんにちは、今日は天気がいいですね。    │
│ 昨日は雨でしたが...                   │
│                                      │
│ [01:35-02:00] 🔄 処理中...           │
│ （この部分は処理完了まで空白）         │
│                                      │
│ [02:00-録音中] 🎤 録音中...          │
└─────────────────────────────────────┘

【重要】時系列順表示ルール:
- 処理完了したチャンクのみ表示
- 未完了チャンクは空白で場所を確保
- 順番が前後することは絶対にない
```

#### 録音完了後の表示（通常モード）
```
┌─────────────────────────────────────┐
│ こんにちは、今日は天気がいいですね。    │
│ 昨日は雨でしたが、今日は晴れています。  │
│ 明日も晴れるといいですね。             │
│                                      │
│ （タイムスタンプは消える）             │
│ （全文が編集可能になる）               │
└─────────────────────────────────────┘
```

### 3.4 Formatted Textタブの表示（新規追加）

#### 録音中の表示（リアルタイムモード）
```
┌─────────────────────────────────────┐
│ ■ 今日の天気                         │
│ 本日は晴天に恵まれ、気温も過ごしやすい │
│ 一日となりました。                    │
│                                      │
│ [処理中のチャンク...]                 │
│                                      │
│ ※ フォーマット: Meeting Minutes      │
└─────────────────────────────────────┘

【動作仕様】
- 各チャンクのASR完了後、即座にフォーマット処理
- フォーマット済みテキストもリアルタイムで逐次表示
- エラーチャンクは「[エラー: 取得失敗]」として含めてフォーマット
- 処理中は「処理中...」を一時表示
- 現在のプリセット名を下部に表示
```

### 3.5 プリセット選択の制約
```
録音開始前:
- すべてのプリセット選択可能
- フォーマットON/OFF切り替え可能

録音開始後:
- プリセット選択ボタンが無効化（グレーアウト）
- フォーマットON/OFF切り替えも無効化
- 「録音中は変更できません」ツールチップ表示
```

### 3.3 エラー表示エリア（新規追加）

#### 場所：メインウィンドウの一番下
```
┌─────────────────────────────────────┐
│          メインコンテンツエリア         │
├─────────────────────────────────────┤
│ ⚠️ エラー (2件) [クリア]              │
│ ├ 02:45 チャンク3: ネットワークエラー  │
│ └ 03:12 チャンク5: API制限            │
└─────────────────────────────────────┘
```

#### エラーをクリックすると詳細表示
```
┌─────────────────────────────────────┐
│ エラー詳細:                          │
│ 時刻: 02:45                          │
│ チャンク: 3 (02:00-02:45)            │
│ エラー: Network timeout              │
│ 詳細: Connection timed out after 30s  │
│ [再試行] [無視] [閉じる]              │
└─────────────────────────────────────┘
```

### 3.6 ポップアップの状態表示（右下）

#### 現在の3状態
1. Recording（録音中）
2. Processing（処理中）  
3. Complete（完了）

#### 新しい7状態
1. **Recording** - 通常録音中（最初の1分間）
2. **Live Transcribing** - リアルタイム処理中（1分以降）
3. **Processing Chunk X/Y** - チャンクX/Y処理中
4. **Finalizing** - 最終処理中（全チャンク結合）
5. **Complete** - 完了
6. **Cancelled** - キャンセル済み（2秒後に自動消去）
7. **Cancelling...** - キャンセル処理中（API停止待ち）

## 4. エラー処理の詳細仕様

### 4.1 エラー発生時の動作

#### 録音中にエラーが発生した場合
```
1. エラーが起きたチャンクをスキップ
2. エラー情報をエラーエリアに控えめに表示
   - 小さいエラーアイコン（🔸）を表示
   - 点滅や音は出さない
   - エラー件数をカウンターで表示
3. 録音は継続（次のチャンクへ）
4. 処理中表示は「⚠️ エラー」に変更
```

#### 録音終了後の自動リトライ
```
1. 失敗したチャンクのリスト作成
2. 古い順（チャンク番号順）に再試行
3. 最大3並列で処理
4. 成功したチャンクを時系列順に挿入
   - 空白だった部分にテキストを埋める
   - 後続のテキストは自動的に下にシフト
5. リトライは1回のみ
   - 2回失敗したら諦める
   - その部分は「[エラー: 取得失敗]」と表示
```

### 4.2 エラーの種類と対応

| エラー内容 | 録音中 | 録音後 | ユーザー操作 |
|-----------|--------|--------|-------------|
| ネットワーク切断 | スキップ | 5秒後に1回再試行 | 不要 |
| APIレート制限 | スキップ | 60秒後に1回再試行 | 不要 |
| API認証エラー | 録音停止 | 再試行しない | API key確認 |
| タイムアウト(30秒) | スキップ | 即座に1回再試行 | 不要 |
| 不明なエラー | スキップ | 10秒後に1回再試行 | 不要 |

## 5. 技術仕様

### 5.1 音声バッファ管理とメモリ最適化
```python
# 現在の実装（全体を1つのバッファに保存）
self.recording_buffer = []  # 最大10分

# 新実装（チャンクごとに管理）
self.current_chunk = []     # 現在録音中のチャンク
self.chunk_queue = []       # 送信待ちチャンク
self.processing_chunks = {} # 処理中のチャンク
self.completed_texts = {}   # 完了したテキスト結果
self.cancel_flag = False    # キャンセルフラグ（新規）
self.api_futures = []       # 実行中のAPI呼び出し（新規）

# メモリ最適化
def on_chunk_completed(self, chunk_id, text_result):
    # テキスト結果を保存
    self.completed_texts[chunk_id] = text_result
    
    # 音声データを即座に削除（メモリ解放）
    if chunk_id in self.processing_chunks:
        del self.processing_chunks[chunk_id]
    
    # 効率的なガベージコレクション（10チャンクごと）
    self.chunks_deleted += 1
    if self.chunks_deleted % 10 == 0:
        gc.collect()
```

### 5.2 チャンク分割とオーバーラップの実装
```python
def check_chunk_boundary(self, current_time, audio_data):
    chunk_duration = current_time - self.chunk_start_time
    
    # 1分未満: 分割しない
    if chunk_duration < 60.0:
        return False
    
    # 2分経過: 強制分割
    if chunk_duration >= 120.0:
        return True
    
    # 1分30秒経過後: 無音検出（オーバーラップを考慮）
    if chunk_duration >= 90.0:
        # オーバーラップ時間を考慮した実効的な無音時間
        overlap_duration = self.calculate_overlap_duration("ja")
        effective_silence_duration = 1.5 + overlap_duration  # 1.5 + 0.8 = 2.3秒
        if self.detect_silence(audio_data, effective_silence_duration):
            return True
    
    return False

def create_chunk_with_overlap(self, audio_data, start_idx, end_idx):
    """言語に応じたオーバーラップを含むチャンクを作成"""
    sample_rate = 16000
    overlap_duration = self.calculate_overlap_duration("ja")  # 0.8秒
    overlap_samples = int(overlap_duration * sample_rate)
    
    # 終端にオーバーラップ追加（最後のチャンクを除く）
    if end_idx + overlap_samples < len(audio_data):
        chunk = audio_data[start_idx:end_idx + overlap_samples]
    else:
        chunk = audio_data[start_idx:end_idx]
    
    # 次のチャンクの開始位置（オーバーラップ分前から）
    next_start = max(start_idx, end_idx - overlap_samples)
    
    return chunk, next_start
```

### 5.3 API呼び出しの並列化
```python
# ThreadPoolExecutorで最大3並列
executor = ThreadPoolExecutor(max_workers=3)

# チャンクごとに非同期送信
future = executor.submit(
    send_chunk_to_api,
    chunk_id=chunk_id,
    audio_data=chunk_data
)
self.api_futures.append(future)  # キャンセル用に保持

# キャンセル処理の実装
def cancel_all_processing(self):
    self.cancel_flag = True
    
    # 録音を停止
    if self.is_recording:
        self.stop_recording()
    
    # すべてのAPI呼び出しをキャンセル
    for future in self.api_futures:
        future.cancel()  # まだ開始していないものはキャンセル
    
    # 実行中のものは中断フラグで停止
    self.chunk_queue.clear()
    self.processing_chunks.clear()
    
    # UIをリセット
    self.reset_ui()
```

### 5.4 結果の表示制御（時系列順保証）
```python
# チャンクIDと結果を管理
results = {
    1: {"status": "completed", "text": "こんにちは...", "formatted": "■ 挨拶\nこんにちは..."},
    2: {"status": "processing", "text": None, "formatted": None},
    3: {"status": "error", "text": None, "formatted": None, "error": "Network timeout"},
    4: {"status": "completed", "text": "今日は...", "formatted": "■ 本日の内容\n今日は..."},
}

# 時系列順で表示（未完了部分は空白確保）
def display_chunks_in_order(self, results):
    for chunk_id in sorted(results.keys()):
        chunk = results[chunk_id]
        if chunk["status"] == "completed":
            # Transcriptionタブに生テキスト表示
            self.display_chunk_text(chunk_id, chunk["text"])
            # Formatted Textタブにフォーマット済み表示
            if self.format_enabled and chunk["formatted"]:
                self.display_formatted_text(chunk_id, chunk["formatted"])
        elif chunk["status"] == "processing":
            self.display_chunk_placeholder(chunk_id, "🔄 処理中...")
        elif chunk["status"] == "error":
            self.display_chunk_placeholder(chunk_id, "⚠️ エラー")

# 段階的な重複テキスト除去実装
def remove_duplicate_text(self, text1, text2):
    """Phase 1: シンプルな文字列マッチング実装"""
    # 動的なウィンドウサイズ（テキストの10%、最大50文字）
    window_size = min(len(text1) // 10, len(text2) // 10, 50)
    
    # 完全一致による重複検出（Phase 1ではこれのみ実装）
    for i in range(window_size, 5, -1):
        if text1[-i:] == text2[:i]:
            return text1 + text2[i:]
    
    # 重複が見つからない場合は単純に結合
    return text1 + text2

# 将来の拡張用（Phase 2以降）
def remove_duplicate_text_advanced(self, text1, text2):
    """Phase 2以降: 高度なアルゴリズム実装予定"""
    # - 編集距離による類似度検索
    # - 形態素解析による文節境界検出
    # - 機械学習ベースの重複検出
    pass

def handle_error_chunk_in_format(self, chunks):
    """エラーチャンクを含むフォーマット処理"""
    formatted_chunks = []
    for chunk in chunks:
        if chunk["status"] == "error":
            formatted_chunks.append("[エラー: 取得失敗]")
        else:
            formatted_chunks.append(chunk["text"])
    
    # エラーを含む全体をフォーマット
    combined_text = "\n".join(formatted_chunks)
    return self.format_api(combined_text, self.current_preset)
```

## 6. ファイル変更一覧

### 6.1 新規作成ファイル
1. `OpenSuperWhisper/realtime_recorder.py` - チャンク分割ロジック
2. `OpenSuperWhisper/chunk_processor.py` - 並列処理管理
3. `OpenSuperWhisper/retry_manager.py` - リトライ制御
4. `OpenSuperWhisper/cancel_handler.py` - キャンセル処理管理（新規）

### 6.2 修正ファイル
1. `OpenSuperWhisper/ui_mainwindow.py`
   - line 488: タブ名を "Raw Transcription" → "Transcription" に変更
   - line 500-600: リアルタイムモード表示機能を追加
   - line 1400-1450: エラー表示エリアを追加

2. `OpenSuperWhisper/recording_indicator.py`
   - line 85-95: 新しい状態（Live Transcribing等）を追加
   - line 100-110: Cancelledステータスの追加

3. `OpenSuperWhisper/global_hotkey.py`
   - line 150-160: Escキーのグローバルホットキー登録

## 7. 動作確認方法

### 7.1 基本動作テスト
```
1. アプリを起動
2. Ctrl+Spaceで録音開始
3. 2分30秒話し続ける
4. Ctrl+Spaceで録音停止
確認: 2つのチャンクに分かれて表示される
```

### 7.2 無音検出テスト
```
1. 録音開始
2. 1分35秒話す
3. 3秒黙る
4. また話す
確認: 黙った部分でチャンクが分割される
```

### 7.3 エラーテスト
```
1. ネットワークを切断
2. 録音開始
3. 1分以上録音
4. ネットワークを再接続
5. 録音停止
確認: エラーが表示され、自動リトライされる
```

### 7.4 キャンセルテスト
```
テスト1: 録音中のキャンセル
1. 録音開始
2. 30秒録音
3. Escキーを押す
確認: 即座に録音停止、結果なし

テスト2: 処理中のキャンセル
1. 録音開始
2. 2分以上録音（チャンク処理開始）
3. 処理中にEscキーを押す
確認: API呼び出し中断、部分結果も破棄

テスト3: リトライ中のキャンセル
1. ネットワーク切断で録音
2. エラー発生後、録音停止
3. リトライ開始後にEscキー
確認: リトライ中断、エラー表示クリア
```

## 8. 実装スケジュール

### Phase 1: 基本機能（10営業日）
- Day 1-3: チャンク分割機能
- Day 4-7: UI表示モード実装
- Day 8-10: API並列処理

### Phase 2: エラー処理（5営業日）
- Day 11-12: エラー表示UI
- Day 13-15: リトライ機能

### Phase 3: 最適化（5営業日）
- Day 16-17: メモリ最適化
- Day 18-20: パフォーマンス改善

## 9. 注意事項

### 9.1 やってはいけないこと
- ❌ 録音中にモーダルダイアログを出す
- ❌ エラーで録音を中断する（認証エラー以外）
- ❌ チャンクの順番を入れ替えて表示する
- ❌ 単語の途中で音声を切断する
- ❌ エラーを完全に隠す（透明性を保つ）

### 9.2 必ず守ること
- ✅ 音声の欠落を防ぐ（ギャップレス録音）
- ✅ UIをフリーズさせない（非同期処理）
- ✅ エラーは控えめに表示（録音優先だが透明性確保）
- ✅ 時系列順を厳守（ユーザーの混乱を防ぐ）
- ✅ 音韻境界を考慮した分割（自然な区切り）
- ✅ 日本語は0.8秒、英語は0.5秒のオーバーラップ
- ✅ フォーマット処理も即座に実行・表示
- ✅ エラーチャンクも含めてフォーマット

## 10. 完成イメージ

### 10.1 録音中の画面
```
OpenSuperWhisper - リアルタイム文字起こし中
┌─────────────────────────────────────────────┐
│ [Transcription] [Formatted Text]             │
├─────────────────────────────────────────────┤
│ [00:00-01:35] ✓                            │
│ おはようございます。今日は月曜日です。        │
│ 今週も頑張りましょう。                      │
│                                            │
│ [01:35-03:00] ✓                            │  
│ さて、今日の予定ですが、午前中は会議があり   │
│ ます。午後は資料作成を...                   │
│                                            │
│ [03:00-03:45] 🔄 処理中...                  │
│ （処理完了まで空白）                        │
│                                            │
│ [03:45-04:30] ⚠️ エラー                     │
│ （再試行待ち）                              │
│                                            │
│ [04:30-録音中] 🎤                           │
├─────────────────────────────────────────────┤
│ 🔸 エラー (1件) [詳細] [クリア]              │
└─────────────────────────────────────────────┘

右下ポップアップ: "Live Transcribing"
```

### 10.2 完了後の画面
```
OpenSuperWhisper - 完了
┌─────────────────────────────────────────────┐
│ [Transcription] [Formatted Text]             │
├─────────────────────────────────────────────┤
│ おはようございます。今日は月曜日です。        │
│ 今週も頑張りましょう。さて、今日の予定です   │
│ が、午前中は会議があります。午後は資料作成   │
│ を行い、夕方にはレビューを実施します。       │
│                                            │
│ （編集可能）                                │
└─────────────────────────────────────────────┘

右下ポップアップ: "Complete"
```
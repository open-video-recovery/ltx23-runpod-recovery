# Netlify匿名利用計測 — 実装・展開手順（第1段階）
更新: 2026-11-06

## 状態とソースの注意
このリポジトリの `index.html` はGitHub公開用JSON補助画面です。
ユーザー指定のNetlify `friendly-elf-6cfdcf.netlify.app` の現行配信物
`riruka_runpod_json_helper_v4.html` と一致するかは、**Netlify管理接続がないため未確認**。
既存NetlifyサイトへPRだけで配信できるとは限りません。
**Netlifyが手動ZIP/ドラッグデプロイの場合、Functions/Blobsも含めてCLIまたはGit連携デプロイが必要です。**
現行Netlifyの公開HTMLをバックアップし、差分確認するまで上書きしないこと。

## 実装済み（本番展開ではない）
- `telemetry.js`: 外部トラッカー無し、同一オリジンのみ、送信障害は無視。
- `track.mjs`: 許可リスト型、数百バイト制限、公開サイトOrigin固定（Deploy Previewは本番集計へ記録しない）、Netlify FunctionsのIPベースレート制限。
- `stats.mjs`: 管理者トークン認証、30/90日の日別・週別・月別。
- `prune-metrics.mjs`: 日次90日超削除（UTC 03:00、JST 12:00）。
- `admin-stats.html`: トークンをURLやlocalStorageへ保存しない管理者画面。
- `test/metrics.test.mjs`: 許可フィールド、冪等、集計の単体テスト。

## 保存するもの
**保存しない**: IP、氏名、メール、完全UA、APIキー、画像、動画、プロンプト、
生成JSON、RunPod Endpoint ID/Job ID、リファラ、URLパス。
**保存する**: JST日付、許可リストのイベント名、ランダムなタブセッションUUIDの
サーバー秘密鍵によるHMAC短縮値、イベントUUIDのHMAC短縮値。
任意同意の場合だけ、30日以内の再訪確認用UUIDのHMAC短縮値。
保存場所はNetlify Blobs `ovr-anon-metrics-v1`。中身は空文字列、情報はキーだけ。
保持期限は90日、削除はスケジュールジョブ（正常実行が必要）。

ブラウザのsessionStorageにセッションUUIDが残る。同一人物が別タブ・端末で開くと
別セッション扱い。任意の再訪分析にチェックするとlocalStorageに30日期限の
UUIDを保存し、チェックを外すと削除。本人の識別や厳密なUU計測ではなく**推定セッション数**。
再訪人数は、同意があり、同じ仮名UUIDを使った異なる日付の利用だけを数える。
ブラウザのストレージ利用を禁止した場合は、セッション数の重複が増える。

## 展開準備
1. Netlify側で現在のDeploy履歴/公開HTML/Build設定/Git連携の有無を確認。
   Netlify標準Analytics導入状況、履歴保持、Function/Blobs使用量も確認。
2. リポジトリの別ブランチをNetlifyのDeploy PreviewでUIとJSONの動作確認。Previewの計測は本番データ混入防止のため意図的に停止する。
3. 計測する公開Originは既定で `https://friendly-elf-6cfdcf.netlify.app` に固定。カスタムドメインに変更する場合は `telemetry.js` のHOST_OKとFunctionsの `ANALYTICS_ALLOWED_ORIGIN` を同じ値に設定して再ビルドする。
4. **Netlify Project configuration → Environment variables** へ、
   `ANALYTICS_ADMIN_TOKEN` に乱数で生成した**32文字以上**の十分に長い秘密値を登録。
   `netlify.toml` に秘密値を記載しない。SecretはFunctionsだけで使用し公開HTMLに混ぜない。
   未設定ならイベントを記録せず、管理画面は503で閉じる（安全側に失敗）。
4. NetlifyとこのGitHubリポジトリを同一サイトへ連携するか、
   正式なNetlify CLI/APIデプロイを準備する（Netlifyのトークンは公開GitHubに保存しない）。
   `npm run build` で配信物は`dist/`のみ、Functionsは`netlify/functions/`。
5. 現在のNetlify HTMLが本リポジトリと異なる場合は**既存HTMLに計測フックだけ移植**。
   JSON生成ボタンの成功時 `window.ovrMetrics?.send('json_created')` などを入れる。
   既存の入力UIや変換処理を置換しない。
6. 本番配信後に公開画面を開く → JSON生成/コピー/保存 →
   `/admin-stats.html` で管理者トークンを入力し、日別・週別・月別数値が増えるか検証。
   異なるタブで別セッション、同一タブ再読込で同一日重複しないことを確認。
   ブラウザ開発者ツールで計測に機密が含まれないことを確認する。
7. `/.netlify/functions/stats` にトークンなしで401、誤トークンで401を確認。
   JSON生成は計測APIが停止中でも完了することを確認。
8. 課金上限をNetlify Billingから確認し、Function/Blob使用量を定期点検。

## バックエンド仕様
- POST `/.netlify/functions/track` JSON: `{"event":"visit","sid":"UUIDv4","eid":"UUIDv4","rid":"任意UUIDv4"}`
- GET `/.netlify/functions/stats?days=30` + Authorization Bearer 管理者トークン
- `visit` は1日・セッションで重複除外（Blob onlyIfNew）。他イベントは送信UUIDで重複除外。
- 計測イベントは実行開始/成功を意図的に分ける。JSON保存はダウンロード操作回数でありOS保存成功を保証しない。
- アクセス測定とRunPod実行は完全分離。
- 動画・Endpoint系イベントはRunPod統合実装時に配線する。現時点ではゼロが正常。

## 費用・過去データ
Netlifyの旧計測履歴はこのコードで過去に遡って復元できない。
標準Web AnalyticsはPV分析用、独自計測はJSON操作人数の推定用。
Web Analyticsの利用可能期間は契約プランに依存する（2026年時点で
Freeは1日、Personalは7日、Proは30日が案内されている）。
Functions/BlobsはFreeでも使用可だが無制限無料ではなくクレジット制。
静的HTMLだけではサーバー側の蓄積・非公開集計を作れない。
イベント数に比例してBlobs件数/Functions呼び出しが増える。大量アクセス時は再設計する。

## 第2段階の境界
RunPod v2管理APIと実行APIは別ホスト。別途 `docs/runpod-api-investigation.md` を参照。
旧Worker/Workflowレイヤーを含むGHCRを正式公開版として自動適用しない。

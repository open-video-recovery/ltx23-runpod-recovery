# RunPod Serverless統合調査（第2段階の着手資料）
更新: 2026-11-06

## 現状
本リポジトリのGitHub公開版はJSON生成補助のみ。RunPod管理APIの実行は未実装。
既存Netlifyの配信HTMLは別物の可能性があるため、まず第1段階の本番展開と一致確認を優先する。
旧 `ghcr.io/open-video-recovery/ltx23-10eros-licensed` は古いWorker/Workflowレイヤーを含み、
独立後継としては**未承認**。固定Digest/環境変数/HF設定を事前に監査する。

## 最新API
- 2026年8月にRunPodが発表したREST v2: `https://api.runpod.io/v2`（public beta）。
- Endpoint管理: `GET/POST https://api.runpod.io/v2/serverless` 等。
- Queue実行: `POST https://api.runpod.ai/v2/{endpointId}/run`
- 状態: `GET https://api.runpod.ai/v2/{endpointId}/status/{jobId}`
- REST v2の例は `templateId`, `type:'QUEUE'`, `gpu:{pools:['ADA_24'],count:1}`,
  `workers:{min:0,max:1,idleTimeout:5}`, `scaling:{type:'QUEUE_DELAY',queueDelay:4}`。
- コンテナのimageやdisk/env設定は、最新のテンプレート作成API/Endpoint Request schemaに
  照らして実機確認する（旧GraphQLのgpuIds等とは混用しない）。
- レスポンスに含まれるRunPod job IDやEndpoint IDは**分析APIへ送らない**。

## セキュリティとUI
- RunPod APIキーはページ内メモリのみで、既定ではlocalStorageやCookieへ保存しない。
- キー権限はEndpoint作成・削除、GPU課金を伴う。送信・削除ボタンは最終確認を必須にする。
- CORSが許可される場合のみブラウザから直接RunPod APIへ接続する。
- 不許可ならNetlify Functionsの限定された中継（許可されたRunPod API host/path/methodのみ）を検討。
  **運営者側のFunctionsをAPIキーが通過する事実を明示**し、キーの保存/ログ/計測を禁止。
- 初回設定候補: ADA_24、min0/max1、idle5、150GBディスク。ただしモデル要件が確定するまで有効化しない。
- 先に既存Endpointを一覧して重複作成を避ける。予想料金、対象Digest、GPU設定を確認し
  ユーザーが押した場合のみEndpointを作成・削除する。
- `/run` は二重送信対策としてUIで排他し、受付済ジョブは同じIDで `/status` 再試行。
- 応答が曖昧なネットワーク障害時の再POSTは課金二重化するおそれあり、再POST前にユーザーへ警告。
- RunPod側のステータスと生成Workerの出力形式（mp4 URL / Base64 / blob）が別問題。
- Netlify Functionsのバッファ応答上限は6MBでBase64化オーバーヘッドがあるため、
  大きなMP4をFunctions経由でそのままリレーしない。
  ブラウザ直接/ユーザー所有ストレージ等を比較し、運営者側で動画を保存しない。
- メトリクスは許可リスト `endpoint_created`, `video_started`,
  `video_succeeded`, `video_failed`, `video_downloaded` で集計できるよう準備済み。

## 関連公式文書
- https://www.runpod.io/blog/runpods-rest-api-v2-is-here-one-api-for-your-entire-gpu-stack
- https://docs.runpod.io/serverless/endpoints/overview
- https://docs.netlify.com/build/functions/configuration/

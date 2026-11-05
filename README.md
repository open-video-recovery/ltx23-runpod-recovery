# LTX 2.3 / 10Eros v1.4 — RunPod Serverless

画像1枚から動画を生成する、自分専用のRunPod Endpointを作る手順です。**Docker・GitHub・モデルのダウンロード操作は不要です。**

> **GHCRイメージ登録済み。** 元のモデルとWorker、Workflowに対応した利用規約・NOTICEをOCIへ同梱しています。RunPodでのGPU動画生成はまだ未検証です。

## 1. GHCRイメージ

GitHub Actionsで実際に登録・Digest確認したイメージです。

~~~text
ghcr.io/open-video-recovery/ltx23-10eros-licensed@sha256:434141dc283fe49808b93139de7905a9fb190071fbbe811809b1f021d9f1ceb5
~~~

既存のLTX 2.3 / 10Eros v1.4モデル、Worker、Workflowを再利用し、GHCRの10GB/レイヤー制限のため巨大レイヤーを分割しました。実行時に元のレイヤー内容を復元してからWorkerを起動します。ライセンス文書も同梱しています。

## 2. RunPodでEndpointを作成

1. [RunPod](https://www.runpod.io/)に登録し、支払い設定を行います（GPU利用は有料）。
2. RunPod Console → **Serverless → New Endpoint**。
3. **Import from Docker Registry** を選び、上記の固定Digestを入力。
4. **Queue**タイプを選び、公開時に指定するGPU・Disk・Timeoutを設定。
5. 初回は **Active Workers = 0、Max Workers = 1** として **Deploy Endpoint**。

既存のEndpointを使う場合は、Endpointの編集画面からContainer Imageを固定Digestに変更します。

GPU利用は有料です。初回起動で分割モデルを復元するため、Container Diskは120GBを目安にし、起動時間に余裕を見てください。

## 3. Requestsから動画生成

Endpoint → **Requests** に次のJSONを入力します。JPEG_BASE64は、実際のJPEG画像をBase64にした文字列へ置き換えてください。

~~~json
{
  "input": {
    "mode": "i2v",
    "model_version": "ltx23",
    "quality_preset": "balanced",
    "width": 640,
    "height": 960,
    "fps": 24,
    "seconds": 5,
    "seed": 1234567,
    "distilled_strength": 0.5,
    "first_stage_strength": 0.85,
    "refine_stage_strength": 1.0,
    "prompt": "A gentle breeze moves the subject's hair.",
    "files": [{"name": "input.jpg", "data": "JPEG_BASE64"}]
  }
}
~~~

**Run** を押し、完了したら動画を確認します。使わなくなったEndpointは削除してください。

## 利用条件

LTX・10Eros・Gemmaはそれぞれの上流ライセンスおよび利用条件が適用されます。規約・Notice・公式ポリシーをOCIの追加レイヤーに同梱しています。元モデル作者と本リポジトリは別主体であり、作者による推奨・保証を示しません。[ライセンスと出典](NOTICE-THIRD-PARTY.md)

[公開準備状況](docs/STATUS.md)

# LTX 2.3 / 10Eros v1.4 — RunPod Serverless

画像1枚から動画を生成する、自分専用のRunPod Endpointを作る手順です。**Docker・GitHub・モデルのダウンロード操作は不要です。**

> **現在：動画用GHCRイメージは準備中。** 次のイメージの実際のDigestが掲載されるまで、有料Endpointを作成しないでください。

## 1. GHCRイメージ

完成後に、確認済みの固定OCI Digestをここへ掲載します。

~~~text
ghcr.io/open-video-recovery/ltx23-10eros-licensed@sha256:【公開後に記載】
~~~

既存のLTX 2.3 / 10Eros v1.4モデル、Worker、Workflowは維持し、配布に必要なライセンス文書だけを追加する方針です。

## 2. RunPodでEndpointを作成

1. [RunPod](https://www.runpod.io/)に登録し、支払い設定を行います（GPU利用は有料）。
2. RunPod Console → **Serverless → New Endpoint**。
3. **Import from Docker Registry** を選び、上のGHCRイメージを入力。
4. **Queue**タイプを選び、公開時に指定するGPU・Disk・Timeoutを設定。
5. 初回は **Active Workers = 0、Max Workers = 1** として **Deploy Endpoint**。

既存のEndpointを使う場合は、Endpointの編集画面でContainer Imageを新しいGHCRの固定Digestに変更します。

GHCRがPrivateの場合はRunPodで**Registry Authentication**を設定する必要があります。初心者向けには、公開条件が整ったイメージを案内します。

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

[LTX・10Eros・Gemma・ComfyUIのライセンスと出典](NOTICE-THIRD-PARTY.md)を確認してください。ライセンス文書の追加だけで、第三者のPythonやWorkflowの再配布権限まで自動的に得られるわけではありません。

[公開準備状況](docs/STATUS.md)

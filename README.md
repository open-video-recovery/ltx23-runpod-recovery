# LTX 2.3 / 10Eros v1.4 — RunPod Serverless

画像1枚から動画を生成する、自分専用のRunPod Endpointを作る手順です。**Docker・GitHub・モデルのダウンロード操作は不要です。**

> **公開前監査中：一般利用向けイメージの案内は停止しています。** GHCRの登録は成功しましたが、法務・匿名性の確認が未了です。RunPodでのGPU動画生成も未検証です。

## 1. GHCRイメージ

公開前の監査が完了したら、確認済みのGHCR固定Digestを掲載します。**監査未完了のイメージ参照先は案内していません。**

既存のLTX 2.3 / 10Eros v1.4モデル、Worker、Workflowを再利用し、GHCRの10GB/レイヤー制限のため巨大レイヤーを分割しました。実行時に元のレイヤー内容を復元してからWorkerを起動します。ライセンス文書も同梱しています。

## 2. RunPodでEndpointを作成

1. [RunPod](https://www.runpod.io/)に登録し、支払い設定を行います（GPU利用は有料）。
2. RunPod Console → **Serverless → New Endpoint**。
3. **Import from Docker Registry** を選び、公開審査後に掲載するGHCRイメージを入力。
4. **Queue**タイプを選び、公開時に指定するGPU・Disk・Timeoutを設定。
5. 初回は **Active Workers = 0、Max Workers = 1** として **Deploy Endpoint**。

既存のEndpointを使う場合は、公開審査後にEndpointの編集画面からContainer Imageを変更します。

GPU利用は有料です。配布条件と動作確認が整うまではEndpointの作成を控えてください。

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

LTX・10Eros・Gemmaは、各ライセンスの条件に従って再配布します。必要な規約・NoticeをOCIの追加レイヤーへ同梱します。[ライセンスと出典](NOTICE-THIRD-PARTY.md)

[公開準備状況](docs/STATUS.md)

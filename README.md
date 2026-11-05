# LTX 2.3 + 10Eros v1.4 | RunPod Serverless

**画像1枚から動画（MP4）を生成するための、モデル・Worker・Workflow同梱のコンテナです。** Dockerのインストールやモデルの手動ダウンロードは不要。RunPodのServerless Endpointから利用できます。

## 動作確認

- **2026年11月5日、RunPodの24GB GPU（RTX 4090系）で画像→MP4生成に成功。**
- 出力：**640 × 960 / 24fps / 約5.04秒 / H.264 MP4（121フレーム）**。FFmpegで全フレームのデコードに成功しています。
- モデル本体・Worker・Workflowを含む22レイヤーは、実機確認したイメージから**変更していません**。最新リリースではライセンス／NOTICEとOCIメタデータのみ更新しています。
- 映像の仕上がりの良し悪しや、すべてのプロンプトでの動作を保証するものではありません。

## 1. コンテナイメージ

以下をRunPodのContainer Imageに指定してください。**公開GHCRから匿名取得可能**で、Docker Hubアカウントは不要です。

```text
ghcr.io/open-video-recovery/ltx23-10eros-licensed@sha256:cb6dc2a1dac7945f154c3ed48bd3493d921fe3bbb430a251db954f6596780082
```

## 2. RunPod Serverlessの設定

[RunPod](https://www.runpod.io/) → Serverless → New Endpoint → **Import from Docker Registry**（画面表記は変わる場合があります）。上のイメージを設定し、以下を目安にしてください。

| 設定 | 24GBでの検証構成 |
| --- | --- |
| GPU | RTX 4090 / 24GB（ADA_24） |
| Container Disk | **150 GB** |
| Type | Queue |
| Active / Min Workers | **0** |
| Max Workers | **1** |
| Idle Timeout | **5秒** |

必要な環境変数（実機検証時と同じ値）：

```env
HF_HUB_OFFLINE=1
RIRUKA_MODEL=ltx23
WORKER_BUILD=i2vltx-2.3-quality-profiles-v1
```

**注意：イメージは約36.5GiBと大きいです。** 初回はダウンロードとモデル展開で長時間初期化することがあります。実機テストでは最初のジョブが完了するまで約12分でした（環境により変動）。RunPodのGPU料金が発生します。

## 3. 画像→動画のテスト

RunPodのEndpoint → **Requests** から、次のJSONを実行します。`JPEG_BASE64`を入力用JPEG画像のBase64文字列（`data:image/jpeg;base64,` の接頭辞なし）に置き換えてください。

```json
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
    "prompt": "A gentle camera pan across a colorful geometric scene.",
    "files": [{"name": "input.jpg", "data": "JPEG_BASE64"}]
  }
}
```

ジョブが `COMPLETED` になったら出力動画を確認してください。**料金を抑えるにはMin Workers=0を維持**し、不要になったEndpointは削除してください。

## 利用規約・作者へのクレジット

LTX-2、10Eros、Gemma、ComfyUIなどのモデルとソフトウェアにはそれぞれの上流ライセンス・利用制限が適用されます。ライセンス全文、Gemma NOTICE、LTX AUP、Gemma禁止用途ポリシーなどはOCI内の `/opt/recovery-licenses/` に同梱されています。

詳しくは [第三者ライセンスと出典](NOTICE-THIRD-PARTY.md) をご確認ください。元のモデル・ソフトウェアの作者と、この再パッケージ提供者は別主体です。作者による推奨・保証を意味しません。

[技術的な検証範囲と更新履歴](docs/STATUS.md)

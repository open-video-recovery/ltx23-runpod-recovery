# 公開者向け：4モデル同梱OCIの構築（開発用）

更新日：2026-11-05

**これは公開者の技術資料です。パソコン初心者に要求する操作ではありません。** 初心者はルートREADMEで完成済みOCIをRunPodに指定する予定です。

## 目標

RirukaChan同様、10Eros v1.4、Gemma 3、LTX dynamic LoRA、Upscaler、ComfyUI、必要なCustom Nodes、Worker、WorkflowをOCIに同梱します。

**元のRirukaChan Docker Hub/OCIイメージの複製は禁止。** モデルは各正規配布元からクラウドビルダー上へ取得し、固定revision・サイズ・SHA256を検証します。RunPod起動時に外部ネットワークからモデルをダウンロードさせません。

通常のGitHub Actions ubuntu-24.04のディスクは14GBで、モデル合計約42GBには足りません。空きSSD **250GB以上を目安とするLinuxクラウドビルダー**を使用し、実際のDocker作業は公開者側で行います。ここに書くコマンドを初心者のPCで実行させないでください。

## 1. モデルを直接ダウンロードして検証

~~~bash
python3 -m pip install 'huggingface_hub>=0.30,<2'
python3 scripts/download_models.py --model-root /mnt/build/models
python3 scripts/verify_models.py --model-root /mnt/build/models
~~~

取得先は models.lock.json の4件。非公開HF_TOKENが必要な場合はクラウドビルダーのSecretに限定し、Dockerfileやイメージに含めないこと。SHA256不一致なら停止。

## 2. 2GiBチャンクに分割し、OCIの個別レイヤーを準備

~~~bash
python3 scripts/prepare_embedded_bundle.py \
  --model-root /mnt/build/models \
  --out /mnt/build/oci-context \
  --chunk-bytes 2147483648
~~~

元モデルのサイズとハッシュを検証したうえで、モデルごとのpartsとbundle.jsonを作ります。単一の約29GBモデルを1つのGHCRレイヤーに収めないため、生成Dockerfileでは各partsを個別のCOPYにします。

ステージングフォルダは新規の空ディレクトリである必要があります。モデルや分割ファイルをソースGitHubへPushしないこと。

## 3. WorkflowとCustom Nodesを揃える

**2026-11-05時点で元のI2V Workflowが未復元であり、Custom Nodesの完全な組み合わせも未実証です。** 実モデルがあっても完成した動画は作れません。

- 元のI2V Workflowを正当な許諾のもとに復元するか、公開資料に基づき独立実装する。
- 全Custom Nodes、依存ライブラリ、ComfyUI/PyTorch/CUDAのバージョンを固定する。
- ライセンスの全文、NOTICE、著作権表示、変更点、GPLに必要なソース提供の条件を満たす。

候補Dockerfileを生成するコマンド：

~~~bash
python3 scripts/render_embedded_dockerfile.py \
  --staging /mnt/build/oci-context \
  --project .
~~~

**workflows/i2v.jsonがない場合はエラーで停止**する設計です。開発用の --test-only-no-workflow オプションで作ったものを本番公開しないでください。

候補DockerfileはNVIDIA CUDAベースを使用し、旧RirukaChanイメージをFROMに使わず、各モデルチャンクを別個のCOPYレイヤーで組み込む設計です。起動時にruntime/restore_model_bundle.pyが完全オフラインでSHA256を照合し、ComfyUI/modelsに復元します。

## 4. GHCRで実モデル入りOCIを検証

本番モデルの公開は legal/public-ghcr-release-gates.json でBLOCKEDです。先に正規の利用・再配布条件と、受領者に適用される規約、輸出管理を解決します。

条件が満たされてから、公開者は次の候補コマンドをクラウドビルダーで実行します。

~~~bash
# 注意：現時点では実行しない。法務・GPU検証が通った後の構築例。
docker build --platform linux/amd64 \
  -f /mnt/build/oci-context/Dockerfile.embedded-candidate \
  -t ghcr.io/open-video-recovery/ltx23-runpod-recovery:ltx23-10eros-v1.4 \
  /mnt/build/oci-context
docker push ghcr.io/open-video-recovery/ltx23-runpod-recovery:ltx23-10eros-v1.4
~~~

レジストリの公開設定、実OCIのSHA256 digest、RunPod GPU起動、音声付きMP4の生成成功を確認し、初めて初心者READMEに実際の固定イメージ参照先を記載します。

## 進捗の境界

- 完了：模擬モデルの複数OCIレイヤー化、GHCR Push/Pull、完全オフライン復元、法務資料同梱。
- 今回追加：4モデル全体のロックファイル検証・分割ステージング・モデル復元・COPY別レイヤー生成のCPUテスト。
- 未了：42GB実モデルのビルド、生成可能なWorkflow/Custom Nodes、RunPod GPU MP4実証、公開GHCRの法務条件解決。

配布権限・実生成を確認していない間は、初心者が利用できる完成版とは表記しません。

## 最新の自己所有GHCRベース（2026-11-05）

- GHCR build-and-push [run 41945520845](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41945520845)：**成功**。モデルは含まない。
- `ghcr.io/open-video-recovery/ltx23-runpod-recovery@sha256:6eddba26842c6f6d02e9f07ef3a409d11eee3b54425e5b7890b1666e1e3aa07e`
- `scripts/render_embedded_dockerfile.py`は、この自前GHCRイメージをFROMとして4モデルの分割レイヤーを追加します。他者のモデル同梱OCIを丸ごとコピーしません。
- ビルドのみのGitHub Actions：`[.github/workflows/ghcr-private-model-build.yml](../.github/workflows/ghcr-private-model-build.yml)`。`ltx-oci-large`ラベル付き大容量self-hosted runnerが必要で、現在この匿名アカウントに登録済みであることは確認できていません。
- CPU・Workflow・GPUのテストはこのビルドジョブには含みません。4モデル入りの候補イメージは、Workflow未復元のため**動画生成不可**と明示します。最終的な公開は配布条件が満たされてからです。

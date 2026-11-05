# LTX 2.3 / 10Eros ― RunPod Serverless 復旧キット

**パソコン初心者向け・日本語手順書（2026年11月5日）**

> **重要：現在は準備中です。動画を生成できる公開OCIは、まだ完成・検証できていません。**
>
> このREADMEの**診断テスト用イメージでは動画を作れません**。今すぐ課金して動画生成を試すことはおすすめしません。完成した場合は、冒頭に「動画生成：実機確認済み」と実行記録・固定OCI digestを表示します。現時点でその表示はありません。

## 何ができるようになる予定？

写真1枚と文章を送ると、音声付きMP4動画を作れる、自分専用のRunPod Serverless Endpointを持てるようにするものです。

**完成後、初心者がするのは「RunPod登録 → 完成済みGHCRイメージを選ぶ → Endpointを作る → サンプルを送る」の4段階だけ。**

- パソコンにDockerをインストール：**不要**
- コマンド入力・Linux・GitHub Actions：**不要**
- パソコンでモデル約42GBをダウンロード：**不要**
- Hugging Faceのモデル4点を手作業で配置：**不要**
- Network Volume作成：**不要**

完成版OCIは、10Eros v1.4 / Gemma 3 / dynamic LoRA / x2 Upscaler / ComfyUI / Worker / Workflowをあらかじめ同梱する**RirukaChan型**です。RunPodは初回に大容量OCIを取得するため、その時間は必要です。

## 最初に：どれを使えばいい？

| 名前 | 役割 | 動画は作れる？ |
| --- | --- | --- |
| GHCR「release」完成イメージ | 目標：本番RunPod Endpoint | **未公開・未検証。まだ指定しない** |
| GHCR「diagnostics」 | RunPodがイメージを実行できるか確かめる小型Worker | **作れない（接続診断だけ）** |
| GHCR「engine-base」 | **実際にGHCRビルド・Push成功したComfyUI/RunPodベース**（2026-11-05） | **作れない（モデル・Workflowは未同梱）** |
| GHCR「oci-contract」 | 分割された模擬モデル＋法務書類の同梱を確認する技術試験 | **作れない（RunPod用Workerではない）** |

**ベースイメージの固定Digest**：`sha256:6eddba26842c6f6d02e9f07ef3a409d11eee3b54425e5b7890b1666e1e3aa07e`（[GitHub ActionsでPush成功](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41945520845)）。これは**動画生成用ではありません**。

**正規の動画生成用イメージ名・digest・JSONテストは、実GPU生成後に確定します。** 他サイトから「動くかもしれない」イメージを適当に指定しないでください。

## A. 完成版が公開された後の初心者向け手順

### 1. RunPodに登録する

1. ブラウザで https://www.runpod.io/ を開き、Sign Up（登録）からアカウントを作ります。
2. メール認証と支払い設定を済ませます。**RunPodのGPUは従量課金**です。
3. 「Serverless」の画面を開きます。無料で利用できるとは限りません。
4. APIキーは自分だけの秘密情報です。GitHubの公開ページ、5ch、スクリーンショットに書かないでください。

### 2. 完成済みイメージを選ぶ（まだ使用不可）

完成後に、ここに**検証済みの実際の**イメージ参照先を記載します。

~~~text
モデル同梱の本番イメージ：公開・動作検証待ち
現在指定してよい実モデルのイメージ参照先：なし
~~~

イメージの最後の @sha256:... は「この内容で固定する」という意味です。公開後は **latest ではなく固定digest** を使います。知らない相手のイメージや古いRirukaChan Docker Hubイメージを指定しないでください。

### 3. Endpointを作る（完成後）

1. RunPod Console → **Serverless** → **New Endpoint** を開きます。
2. **Import from Docker Registry**（画面によりDocker/Container Image）を選びます。
3. 上記の検証済みGHCRイメージ参照先をContainer Image欄に貼ります。
4. Endpoint Typeは **Queue** を選びます。
5. GPUは、このREADMEで公開時に**実機検証済みとした機種**を指定します。未検証のため今は指定推奨を断定しません。
6. 費用を抑えて試す場合、Active Workersを **0**、Max Workersを **1** とする設定から始めます。Max Workersの上限と利用可能GPUはアカウント・地域・在庫で異なります。
7. 完成版の実測値に基づくExecution Timeout・Disk・Idle Timeoutを入れ、**Deploy Endpoint** を押します。
8. 作成されたEndpoint IDを控えます。APIキーは他人に見せないでください。

**Active Workers 0でも、ジョブ中・起動中・Idle中のGPUには料金が発生し得ます。** Workerの課金状態はRunPodで確認してください。

### 4. 動画生成をテストする（完成後）

1. Endpoint画面の **Requests** を開きます。
2. 公開後にここへ追記される**検証済みサンプルJSON**をコピーします。
3. **Run** で送信して、COMPLETEDになるかを確認します。
4. 実際にMP4を再生し、音声が含まれるかを確認します。
5. 失敗したら、**Logs / Workers / Requests** を見ます。APIキーや個人の画像は公開せず、エラーの文章だけを共有してください。
6. 使わない場合はEndpoint設定でWorkersを0にし、不要になったらEndpointを削除します。削除前に必要な履歴や出力を保存してください。

**現段階では動作するWorkflowが欠けているため、動画用の偽サンプルJSONは掲載しません。**

## B. 現時点で試せる範囲：GHCR診断テスト（動画は生成しない）

小型の公開可能な診断コンテナで「RunPodが自分のコンテナを起動できるか」だけを確認するための手順です。診断用のGHCRパッケージが**Public**で、後述のCIが成功している場合のみ使えます。

**診断用イメージ**（本番用ではありません）

~~~text
ghcr.io/open-video-recovery/ltx23-runpod-recovery:diagnostics
~~~

- 未認証Pullできるかは、GitHubのパッケージ公開設定で確認してください。GitHubの**公開リポジトリとGHCRパッケージ公開設定は別**です。
- RunPodのServerless → New Endpoint → Import from Docker Registryを開き、診断用イメージを入力します。
- Endpoint TypeはQueue、利用可能なGPUを選択し、Active Workers 0、Max Workers 1でDeployします。**診断でもGPU課金が発生し得ます。**
- EndpointのRequestsで以下を送ります。

~~~json
{
  "input": {
    "task": "diagnostics"
  }
}
~~~

成功すればレスポンスのoutput内に次の項目が入ります。

~~~json
{
  "status": "OK",
  "build_kind": "diagnostics-only",
  "ready_for_video": false,
  "has_ltx_models": false,
  "has_workflow": false,
  "gpu_generated": false
}
~~~

これは**コンテナが呼び出せるだけ**のテストです。モデルを含むGHCRイメージが完成したことを示すものではありません。検証を終えたらEndpointを削除してください。

## C. 配布ライセンスと利用条件

本キット独自のソースコードのMITライセンスは、以下の別々のモデルやソフトウェアをMITへ変更するものではありません。

| 対象 | 配布条件 |
| --- | --- |
| LTX 2.3 / 10Eros / LTX LoRA・Upscaler | [LTX-2 Community License (2026-01-05)](third_party_licenses/LTX-2-Community-License-2026-01-05.txt) と [Acceptable Use Policy](https://static.lightricks.com/legal/ltx-acceptable-use-policy.pdf) |
| Gemma 3 text encoder | [Gemma Terms](https://ai.google.dev/gemma/terms)、[Gemma prohibited use policy](https://ai.google.dev/gemma/prohibited_use_policy)、[必須NOTICE](third_party_licenses/Gemma-NOTICE.txt) |
| ComfyUI / Custom Nodes | [GPL-3.0全文](third_party_licenses/ComfyUI-GPL-3.0.txt)、各Custom Nodeの別ライセンスと著作権表示 |

10Eros作者は [Hugging Face discussion #37](https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37) でLTX-2ライセンスの適用を説明しています。利用条件には生成用途や下流配布に関する制限があります。**適切な利用とモデル再配布は別問題**です。利用者は規約と地域の法令を守る必要があります。

公開モデル入りGHCRには、第三者の公開事例と同様に、モデル出典・全規約・必須Notice・変更点・使用制限を用意します。ただし**「他も公開している」ことだけで、匿名Pullが契約・輸出規制条件に適合したことにはなりません**。一方、規約上の条件を守る再配布に個別の特別許諾が常に必要とも書かれていません。現状の公開可否判定は [こちら](legal/public-ghcr-release-gates.json)。必要な条件を満たすまでは実モデルの一般公開を行いません。

## D. 開発・公開状況（専門家向け）

- [実証済み項目・未完了項目](docs/STATUS.md)
- [GHCR / Hugging Face / Docker Hub の公開事例比較](docs/REDISTRIBUTION_PRECEDENTS_20261105.md)
- [モデル別の出典・権利表示・変更点](NOTICE-THIRD-PARTY.md)
- [ライセンスと配布義務の監査](docs/LEGAL_AUDIT.md)
- [配布判断の日本語説明](docs/DISTRIBUTION_POLICY_JA.md)
- [権利者への照会文案](docs/RIGHTSHOLDER_INQUIRIES.md)
- [モデル4点の固定revisionとSHA256](models.lock.json)
- [公開者向け・モデル同梱OCIのクラウド構築手順](docs/OCI_BUILDER_OPERATOR_JA.md)
- [旧Workflowの出典・未復元事項](workflows/README.md)

**OCI同梱の原則**：公開する予定の本番イメージにはモデル4点・Worker・ComfyUI・API Workflowを収録します。起動時に大容量モデルをDocker HubやHugging Faceから毎回取得する設計は採用しません。現在検証済みなのは**模擬ウェイト**を使ったGHCR Push/Pull・ネットワーク無しの復元のみです。

## よくある質問

**Q. パソコンにDockerを入れますか？** いいえ。完成版はRunPod上の操作だけで使う想定です。

**Q. 完成版は今すぐ使えますか？** いいえ。公式の実モデル同梱イメージとGPU動画生成は未検証です。

**Q. 診断イメージで15秒動画が作れますか？** いいえ。接続確認専用です。

**Q. GHCRのイメージが見えません。** リポジトリがPublicでもパッケージはPrivateのことがあります。公開者側の設定が必要です。

**Q. 完成後、料金はどこで確認しますか？** RunPodのBilling/UsageとEndpointのWorker/Requestsで確認します。無料サービスではありません。

**Q. 動かなければ？** エラーの本文、イメージのdigest、EndpointのGPU名、Workerの状態を記録してください。APIキー・個人画像は共有しないでください。

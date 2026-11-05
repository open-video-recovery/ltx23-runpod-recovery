# 公開者向け：既存OCIにライセンスを追加してGHCRへ登録

初心者は[README](../README.md)だけを読んでください。本手順は公開者向けです。

## 一度だけの設定

1. 匿名GitHubアカウントの [Secrets and variables / Actions](https://github.com/open-video-recovery/ltx23-runpod-recovery/settings/secrets/actions) を開く。
2. Repository Secret **OCI_SOURCE_IMAGE** を作り、所有しているDocker HubのLTX 2.3 / 10Eros v1.4イメージ参照先（タグまたはDigest）を入力する。既存アカウントの認証情報や個人情報を公開READMEへ記載しない。
3. Docker Hub側のイメージは匿名Pullが可能であること。プライベートなら追加のDocker Hub認証設定が必要です。

## GHCRへ登録

1. [GitHub Actions / GHCR publish existing OCI + license overlay](../.github/workflows/ghcr-legacy-license-overlay.yml)を開く。
2. **Run workflow** をクリック。
3. Workflowは、元のOCIマニフェストを読み、LTX・Gemma・ComfyUIのライセンス文書、LTX AUP、Gemma利用禁止事項を1つの追加レイヤーにまとめます。
4. **元のWorker・Python・Workflow・モデルのレイヤーは再構築せず**、GHCRへ送信します。テストジョブはありません。
5. ActionsのSummaryに出力された**実際の固定Digest**を確認します。

保存先：ghcr.io/open-video-recovery/ltx23-10eros-licensed:ltx23-v14

**LTX・Gemma・10Erosは既存ライセンスに基づく条件付き再配布とし、特別許諾待ちにはしません。** 追加レイヤーに必要な規約・Noticeを同梱します。GHCRをPublicにする前に、元Worker・Workflowなどモデル以外の権利と、利用条件・配布先の遵守を別途確認してください。

### GHCRの1レイヤー10GB上限

元OCIはDocker Hubで合計約39GBのレイヤーを持っています。GHCRは**1レイヤー10GB未満**という制限があり、複数レイヤーの合計容量とは異なります。

Workflowはビルド前に元OCIのレイヤーサイズを読み取ります。1つでも上限を超える場合は、そのレイヤーを変更せず移す方法ではGHCRに登録できないため、**その時点で停止**します。ライセンス追加レイヤーが問題なのではありません。モデルを再ダウンロードしたり、テストを実行したりはしません。

### RunPodで利用

GHCRがPrivateならRunPodのRegistry Authenticationに読み取り専用の認証を登録します。その後、EndpointのContainer Image欄へ**GHCRの固定Digest**を貼ります。新規Endpointまたは既存Endpointの設定画面からイメージを指定できます。

GPU生成の結果を確認していないイメージを「実機生成確認済み」と表示しないでください。

[公式GHCRドキュメント](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

# LTX 2.3 / 10Eros ― 検証済みの状態

更新日：2026-11-05。**モデル同梱の動画生成用RunPod Endpointはまだ完成していません。**

## 今回までに実際に成功したこと

- [初心者向けREADME](../README.md)：日本語、RunPod画面操作を順番に案内。無料でないこと、診断と本番の違い、秘密のAPIキー、停止方法も記載。
- [GHCR diagnostics のPush/Pull・実コンテナ自己診断成功](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41940661980)
  - image: ghcr.io/open-video-recovery/ltx23-runpod-recovery:diagnostics
  - immutable digest: sha256:dd8358bff45ff98386c95cd0dafa089eb5eeba336d255cb53387b026ab67a1e5
  - **NO MODELS, NO VIDEO**。GitHub Actionsの認証付きPullとオフライン自己診断成功。匿名Pull、RunPod GPU起動は未検証。
- [模擬モデルを別OCIレイヤーに分けてGHCRへ登録・Pull・オフライン復元成功](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41937445861)
  - image: ghcr.io/open-video-recovery/ltx23-runpod-recovery:oci-contract
  - immutable digest: sha256:61ff87fc59a4938bc1dfb472074e8b04dca881a340c8c27bef705cbf4ba6f1d4
  - **FAKE MODEL BYTES**。RunPod用動画Workerではない。
- [ライセンス・AUP・Gemma規約の公式サイト取得・SHA256記録成功](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41936823780)。
- [OCI内のライセンス文書・公式ポリシーを検証してGHCR Push/Pull成功](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41937445861)。
- [全4モデル用の分割OCIステージング・ローカル復元・Dockerfile生成のCPU検証](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41941448557) 成功。
- 第三者モデルのライセンス、出典、変更点・Notice一覧を [NOTICE-THIRD-PARTY.md](../NOTICE-THIRD-PARTY.md) に記録。

## まだ完了していないこと

1. 正規配布元から実モデル約42GBをクラウドビルダーに取得し、GHCRへフルモデルOCIをビルド・Push/Pullすること。GitHubの一般Runnerはディスク14GBなので使えない。
2. 元のI2V Workflowの再現または独立実装と許諾、Custom Nodes/依存ソフトの固定。現在のDockerfileは実験版で、動画生成エンジンとして未完成。
3. 実RunPod GPUで画像→音声付きMP4を生成し、出力とコスト・イメージDigestを検証すること。
4. LTX/Gemmaの下流利用制限を契約に取り込む仕組みと輸出・制裁対象の条件について、モデル入り**公開GHCR**としての実際の適合性を確保すること。第三者の公開例が存在するだけでは本キットの法的適合性を証明できない。
5. GHCRの公開可視性と匿名Pullを実証すること。リポジトリPublicとパッケージPublicは別。現在、診断用の認証付きPullのみ確認済み。

## 方針

**完成版には全4モデル、ComfyUI、Worker、WorkflowをOCIへ同梱する**。起動ごとにDocker HubやHugging Faceから巨大モデルをダウンロードしない。初心者はRunPodへ完成済みの固定digestを貼るだけで利用できる設計を目指す。

モデルの独自利用・再配布にはLTX-2 Community License、Gemma Terms、ComfyUI GPL、各Custom Nodesの条件が適用される。公開可能なモデル入りOCIは未リリース。

公開条件の台帳：[legal/public-ghcr-release-gates.json](../legal/public-ghcr-release-gates.json)
技術担当手順：[docs/OCI_BUILDER_OPERATOR_JA.md](OCI_BUILDER_OPERATOR_JA.md)

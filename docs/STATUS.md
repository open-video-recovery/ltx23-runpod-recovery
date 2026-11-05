# LTX 2.3 / 10Eros ― 検証済みの状態

更新日：2026-11-05。**モデル同梱の動画生成用RunPod Endpointはまだ完成していません。**

## 最新：配布様式の整理とGit履歴の匿名化

- 通常のOSS／モデル配布と同様に、上流の**ライセンス全文・NOTICE・利用条件・出典**をOCI追加レイヤーへ同梱する方式を採用します。独自の特別許諾書や弁護士意見書を一律の追加必須条件とはしません。各上流規約の適用がなくなるわけではありません。
- [履歴匿名化Actions](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41998525863) **成功**：`main` と開発ブランチ9本の履歴を書換え、到達可能なGitオブジェクト547件から元Docker Hub所有者名の検出0件。匿名コミットメールは維持。
- **例外**：GitHubが保持する過去PR参照9件と古いSHA直接URLはまだ取得可能です。全GitHubキャッシュ・他人のコピーまで消去したという意味ではありません。
- GHCR本番モデルOCIは既に匿名Pull可能です。元のライセンス・Notice・公式ポリシー同梱も確認済み。RunPod GPUの実生成は未確認です。
- 更新後のREADME/NOTICEはGitHubソースへ反映済みですが、**現在公開中の固定Digestに収録されているNoticeは移行実行時点の版**です。OCIの文書を更新するには別Digestの再登録が必要です。
- モデル同梱GHCR自動再公開は停止中。現在の配布・記載内容に関する技術的検証や、既知の権利不明点の確認は別途進めます。

## 2026-11-05 公開前監査 — 当時の判定（その後に履歴書換え・README更新あり）

- **実際の匿名GHCR Pull成功**：2026-11-05 [監査 run 41989198610](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41989198610)。すでに匿名取得可能であり、未公開という以前の認識は誤り。
- **READMEの公開モデル参照リンクを一時撤去済み**。ただし、リンク撤去はGHCR取得の停止や過去Gitコミット削除にはならない。
- **公開Git履歴に元Docker Hubアカウントを示す古いコミットがある**。匿名性を保証できない。
- **完成OCI実物のライセンス・Noticeの存在は確認済み**（LTX/Gemma/ComfyUI、AUP、公式ポリシー）。一方、元Python/Workflowと全Custom Nodesの再配布権限・義務、利用制限の下流契約実装は未確認。
- モデルを登録する**自動公開Workflowは停止済み**。監査中に起動済みの再公開run 41989261449はキャンセル要求が受理された。
- GitHub公式仕様では一度PublicのパッケージをPrivateに戻せない。削除は別途ユーザーの判断・承認が必要。
- 結論と監査証拠：[2026-11-05 公開前リーガル・匿名性監査](PUBLIC_GHCR_RELEASE_AUDIT_20261105.md)／[公開可否台帳](../legal/public-ghcr-release-gates.json)。

**以下に残る旧ステータスの「Private」「未登録」「準備中」は過去時点の記述です。上記の最新監査結果を優先してください。**

## 2026-11-05 15:08 JST：GHCRモデル同梱OCI登録成功

- [GitHub Actions run 41976344090](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41976344090) が **success**。
- 登録イメージ：`ghcr.io/open-video-recovery/ltx23-10eros-licensed:ltx23-v14`
- 確認済み固定Digest：`sha256:434141dc283fe49808b93139de7905a9fb190071fbbe811809b1f021d9f1ceb5`
- 元OCIの15レイヤーを基に、22GiB超の第7レイヤーを8分割し、元圧縮データのSHA-256照合を実施。追加の利用条件・復元起動スクリプトも同梱。
- **まだ未確認**：GHCR PackageのPublic/Private設定と匿名Pull、RunPod Serverless実起動、GPUによる実動画生成、Endpointのイメージ差し替え。
- 大型の元レイヤーはコンテナ起動後に復元するため、ディスク容量・コールドスタート時間に影響します。正常な動画生成は未実証です。
- 既存文書中の「モデル同梱OCI未構築」「GHCR未登録」は、過去の状態です。現時点では上記の実登録結果を優先します。

## 2026-11-05 最新方針（従来の再構築案より優先）

**既存モデル同梱OCIを再利用し、ライセンス文書の追加レイヤーだけを重ねてGHCRへ登録します。**

- [GHCR publish workflow](../.github/workflows/ghcr-legacy-license-overlay.yml) をmainへ実装済み。手動実行のみ。CPU/GPU/Workflowテストなし。
- [初心者用README](../README.md) はGHCR → RunPod Endpoint → Requestsだけに短縮。
- 追加するレイヤー：LTX/Gemma/ComfyUIのライセンス全文・NOTICE・公式AUP/禁止事項（元のPython/Workflow/モデルは変更なし）。
- GHCR書き込みには一度だけGitHub Actionsの**Repository secret** `OCI_SOURCE_IMAGE`（Public Docker HubのモデルOCI参照先）を設定する必要があります。Docker Hubの認証トークンは不要です。移行完了後はSecretを削除できます。既存アカウントとの関連を公表しないため、公開リポジトリのファイルにはその名前を記載しません。
- **GHCR登録は現時点では未実行、RunPod EndpointのGHCR差し替えも未実行です。** 元OCIのいずれかのレイヤーがGHCRの10GB上限を超える場合、変更なしのレイヤー転送はできず、ワークフローは停止します。
- **モデルのライセンス方針は確認済み：** LTX・Gemma・10Erosは既存ライセンスに従った条件付き再配布とし、別途の包括的な特別許諾を取得することを前提としません。規約全文・Notice・利用制限を追加レイヤーに同梱します。元Python等の権利や下流利用条件の履行はモデルの許諾とは別に確認します。GHCR PackageのPublic化はこれらの条件を満たした時点で行います。

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

## 2026-11-05 GHCR build-only priority

- Automated CPU tests, diagnostics and fake-OCI workflows have been switched to **manual-only**. No scheduled/push-triggered test workflows are needed for future builds.
- **GHCR engine-base build + Push: SUCCESS** (CUDA-enabled PyTorch + pinned ComfyUI + RunPod, **NO MODEL WEIGHTS**) via [GitHub Actions run 41945520845](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41945520845). Immutable digest: `sha256:6eddba26842c6f6d02e9f07ef3a409d11eee3b54425e5b7890b1666e1e3aa07e`. No pull test or GPU generation test was requested/performed.
- The full four-model OCI Dockerfile now builds FROM our **own pinned GHCR engine-base digest**, not the old RirukaChan or third-party model-inclusive Docker images.
- **Real four-model OCI private candidate** has a build-only workflow: [.github/workflows/ghcr-private-model-build.yml](../.github/workflows/ghcr-private-model-build.yml). It requires a self-hosted runner labeled `ltx-oci-large` with >=200GiB **free** disk (250GiB recommended), and `HF_TOKEN` if a publisher requires authentication. **No such runner has been verified for the anonymous account; this workflow is not executed.**
- The private candidate targets a new separate GHCR package `ghcr.io/open-video-recovery/ltx23-model-oci-candidate`. GitHub documentation says first-published packages default to **private**, independent of a public source repository's visibility. Confirm package visibility before any wider sharing.
- Model-inclusive candidate can package chunks before a complete generation workflow is ready, but cannot generate videos until Workflow/custom nodes are available.
- **Legal approval for public model-weight distribution remains pending** and is separately tracked in `legal/public-ghcr-release-gates.json`.

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

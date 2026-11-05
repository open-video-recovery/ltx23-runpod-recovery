# Megane6 自宅PCで匿名GHCRを構築する手順

更新：2026-11-05。これは公開利用者向けではなく、公開者向け一度だけの設定です。

## 方針

Megane6のWindows 11 + WSL2 Ubuntuを再利用します。既存Self-hosted runner（i2v-ci-megane6、Linux/x64、i2v-ci）は別アカウントのI2V-Lab専用なので、そのまま残します。

**既存Runnerの停止・登録解除・Dockerグループ追加をしない。**

**家庭用PCのRunnerを公開GitHubリポジトリへ登録しない。** GitHub公式も公開リポジトリでのSelf-hosted Runner利用を強く警告しています。
https://docs.github.com/en/actions/reference/security/secure-use

同じMegane6上に追加のRunnerを立て、新匿名アカウントの**別の非公開リポジトリ**へ登録します。

## 1. 非公開のビルドリポジトリを作成（一度だけ）

1. GitHubで新アカウント open-video-recovery にログインする。
2. https://github.com/new を開き、Ownerをopen-video-recoveryとする。
3. Repository name：ltx23-private-builder
4. Visibility：**Private** を選んで作成する。
5. 非公開リポジトリに .github/workflows/ghcr-private-model-build.yml を作り、公開キットの同名ファイルをコピーする。

公開キットのソース：
https://github.com/open-video-recovery/ltx23-runpod-recovery/blob/main/.github/workflows/ghcr-private-model-build.yml

このWorkflowには「リポジトリがPrivateであること」と「登録先がltx23-private-builderであること」の実行制限を設けています。

## 2. Megane6に2本目のRunnerを登録（一度だけ）

1. 非公開リポジトリの Settings → Actions → Runners → New self-hosted runner。
2. **Linux / x64** を選ぶ。
3. GitHub画面に表示された公式インストールコマンドをMegane6のWSL Ubuntuで実行する。
4. 作業ディレクトリは既存Runnerと別の場所（例：ホームディレクトリ内のltx-private-runner）とする。
5. Runner名はltx-oci-megane6。
6. 追加ラベルは**ltx-oci-large**（このラベルがないとWorkflowは起動しない）。
7. 新Runnerだけを ./run.sh で起動し、非公開GitHubのRunners画面でOnline/Idleと表示されることを確認する。

**登録トークンはChatGPT・公開ページ・スクリーンショットに貼らないこと。**
GitHubが現在のRunner版と短命トークンを表示するので、固定の古いURLや偽トークンは本手順に書いていません。既存Runnerのサービスを停止しないでください。

## 3. ディスクとDocker確認

モデル約42GBとダウンロードキャッシュ、チャンク、Docker BuildKitの領域が必要です。

- モデル作業用：空き200GiB以上（250GiB推奨）。
- Docker layer格納先：空き100GiB以上。
- **同じ物理ディスクの場合は空き容量を二重計上しない**。
- Hドライブ側へ移したWSLの実ディスク残量を確認し、Cドライブへ勝手に巨大データを書き込まない。
- Docker CLIだけでは不足。Docker daemonが動き、その保存先が適切な大容量ディスク上である必要がある。
- 既存i2v-ciアカウントへDocker groupを付与しない。追加Runner用の独立したユーザー／環境を推奨する。

Megane6のWSLで見る確認コマンド：

~~~bash
df -h / /mnt/h 2>/dev/null || df -h /
docker info --format '{{.DockerRootDir}}'
~~~

非公開リポジトリ → Settings → Secrets and variables → Actions → Variablesで、必要ならLTX_BUILD_ROOTを設定してください。Linux絶対パスで、200GiB以上の空きディスクを持つ場所を指定します。デフォルトは/mnt/ltx23-oci-buildです。

## 4. HF_TOKEN（必要な場合のみ）

非公開リポジトリ → Settings → Secrets and variables → Actions → Secretsに、モデル配布元から取得するためのHF_TOKENを登録します。各配布元の利用条件を守ってください。トークンは公開ソース、Dockerfile、ログへ出しません。

## 5. モデル同梱GHCRのビルド開始

非公開リポジトリ → Actions →
Private GHCR model OCI build (Megane6 self-hosted, no tests) → Run workflow。

- 公開ソースから4モデルの配布元とSHA256記録を取得。
- Megane6のHドライブ等の実際の大容量作業領域に正規のモデルをダウンロード。
- 全ファイルのSHA256を検証し、2GiB単位に分割。
- 自前GHCRのエンジンベースをFROMに使い、各モデルを別OCIレイヤーに収録。
- **実モデル入り候補イメージを別のPrivate GHCR packageへPush**。
- イメージの不変DigestをActions Summaryに記録。

GHCR候補名：
ghcr.io/open-video-recovery/ltx23-model-oci-candidate:unverified-(コミットSHA)

**ビルドだけ。CPU・Workflow・GPU動画生成テストは含みません。**
ただし、モデルSHA256と空き容量の確認は破損・ディスク事故を防ぐため必須です。

**注意：** 元I2V WorkflowとCustom Nodesは未完成なので、モデル入りOCIができても動画は生成できません。再配布条件が最終確定するまでGHCRパッケージをPublicへ変えないでください。

## 未完了

- 新アカウントの非公開ビルドリポジトリの作成
- 追加Runnerの登録とオンライン確認
- Megane6のDocker daemonと大容量作業ディスクの確認
- 実モデルのGHCR Push

これらは2026-11-05時点で、まだ実行済みとは確認できていません。

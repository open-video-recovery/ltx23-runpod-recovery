# 自分専用の非公開GHCRビルド用Runnerを接続する方法

この手順は**モデルイメージを作る公開者向け**です。動画を利用するだけの初心者には必要ありません。

## 重要：Runnerは公開ソースリポジトリへ登録しない

家庭用PCのSelf-hosted Runnerは、**必ず別のPrivateリポジトリ**に登録します。GitHubも公開リポジトリにSelf-hosted Runnerを置くことを推奨していません。
https://docs.github.com/en/actions/reference/security/secure-use

既存プロジェクトのRunner・登録情報・サービスは変更しません。同じホストで別のRunnerインスタンスを使います。本人のPC名、ユーザー名、旧アカウント名、NAS名、トークン、実ディスクパスは公開リポジトリに記載しません。

## 1. 匿名アカウントのPrivateリポジトリを作る

1. https://github.com/new にアクセスする。
2. Owner：open-video-recovery
3. Repository name：ltx23-private-builder
4. Visibility：**Private** にする。
5. 新しいリポジトリの .github/workflows/ghcr-private-model-build.yml に、[公開ソースのビルド専用Workflow](../.github/workflows/ghcr-private-model-build.yml)をコピーする。

公開リポジトリ上では、WorkflowにPrivate判定があるのでモデル構築ジョブは実行されません。

## 2. ビルド用の追加Runnerを登録する

1. **Privateリポジトリ**の Settings → Actions → Runners → New self-hosted runner。
2. Operating system：**Linux**、Architecture：**x64** を選ぶ。
3. GitHubの画面に表示される現行バージョンのセットアップコマンドを、独立したLinuxの作業ディレクトリで実行する。
4. 追加ラベル：**ltx-oci-large**。
5. GitHubにOnline/Idleと表示されたら、Runnerの接続は完了。

登録トークンは短い有効期限があります。GitHub画面の指示を使い、秘密情報をChatGPTや公開Issueに貼らないでください。

## 3. ディスクとDockerを事前確認

- モデル取得・分割作業に**空き200GiB以上**、250GiB以上推奨。
- Dockerイメージのレイヤー格納先に**空き100GiB以上**。同じ物理ディスクなら二重計上不可。
- Linuxから参照する作業領域とDocker daemonの保存先を両方確認し、システムディスクを枯渇させない。
- Docker CLIだけではBuildはできず、**動いているDocker daemon / BuildKit**が必要。
- 既存の非特権Runnerへ無条件にDocker group（実質root権限）を追加しない。

確認コマンド（ビルドホストのLinux側）：

~~~bash
df -h /
docker info --format '{{.DockerRootDir}}'
~~~

Privateリポジトリの Settings → Secrets and variables → Actions → Variables に、必要に応じて **LTX_BUILD_ROOT** を登録します。Linux絶対パスで作業領域が200GiB以上空いている場所を選んでください。未設定時は /mnt/ltx23-oci-build です。

必要なら、PrivateリポジトリのActions Secretsに**HF_TOKEN**を保存してください。公開ファイルやログには書きません。

## 4. Buildだけ実行

Privateリポジトリ → Actions → **Private GHCR model OCI build (self-hosted, no tests)** → Run workflow。

Workflowは：
- 匿名の公開ソースからコードを取得。
- モデル4件をHugging Faceの正規配布元から取得し、SHA256を検証。
- 2GiB単位のパーツに分割し、自前GHCRのエンジンベースにCOPYしてOCI構築。
- **非公開の別GHCR候補パッケージ**にPush。
- 固定DigestをSummaryに記録。

出力先は ghcr.io/open-video-recovery/ltx23-model-oci-candidate:unverified-（SHA） です。

**CPUテスト・GPUテスト・動画生成テストは実行しません。** 破損したモデルを配布しないためのSHA256、ディスク容量確認はビルド必須工程として残します。

**実モデル入りイメージの公開はまだ許可されていません。** 新しいPrivate GHCR packageをPublicにしないでください。元のI2V Workflowは未復元なので、候補イメージは動画生成できません。

このリポジトリには、Runner登録トークンの発行やホスト上でのコマンド実行を代行するアクセス権はありません。ホスト側の初回Runner登録後は、GitHub Actionsからビルドを実行できます。

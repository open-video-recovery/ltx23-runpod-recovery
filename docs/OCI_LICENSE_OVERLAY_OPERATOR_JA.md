# 公開者向け：既存OCI → ライセンス同梱GHCR

初心者は[README](../README.md)をご覧ください。

## 公開の方法

GitHub Actionsは**自動起動**します。モデルの再ダウンロードやMegane6でのDocker Build、手動のRun workflow、CPU/GPUテストは不要です。

1. GitHub ActionsのRepository Secret `OCI_SOURCE_IMAGE` に、所有するPublic Docker HubのLTX 2.3 / 10Eros v1.4イメージ名を一度だけ登録します。Docker Hubの認証トークンは不要です。
2. 公開WorkflowのファイルまたはOCI再構成スクリプトが `main` に更新されると、[GHCR公開Actions](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/workflows/ghcr-legacy-license-overlay.yml) が自動起動します。
3. 完了したActions Summaryの**GHCRイメージとDigest**をRunPodのContainer Imageへ指定します。モデルのライセンス文書もOCI内に同梱されます。

保存先：`ghcr.io/open-video-recovery/ltx23-10eros-licensed:ltx23-v14`

## GHCRの10GBレイヤー制限

元OCIは15レイヤーのうち1つが約22GiBで、そのままではGHCRへ転送できません。新しい公開スクリプトは以下を行います。

- 小さい14レイヤーは**元の圧縮バイトとSHA256を維持**してコピーする
- 約22GiBの圧縮済み元レイヤーを3GB以下の分割ファイルにして、それぞれを小さなOCIレイヤーに格納する
- 追加レイヤーにライセンス、Notice、公式AUP・禁止事項および起動用の復元スクリプトを格納する
- RunPodコンテナの初回起動時に元の圧縮済みレイヤーを再結合・展開してから、**既存Workerを変更せず実行する**

モデルファイルや既存Python・Workflowのバイトを改変しませんが、**OCIのレイヤー構造と起動スクリプトは変更**します。したがって、元イメージと起動時間・ディスク使用量は同じではありません。RunPodのコンテナDiskは120GBを目安に設定してください。

## 匿名性・公開設定

- Source名はSecretで渡します。公開Workflowの現行ファイルに、元のDocker Hubアカウント名は記載しません。
- 元OCIのレイヤー、ビルド履歴・ラベルの調査記録：[OCIメタデータ監査](OCI_PRIVACY_AUDIT_20261105.md)。
- 元の独自プロジェクト名は新しいイメージの設定情報から整理します。モデルの著作者表示・配布規約はNoticeに保持します。
- 公開Gitの**過去コミットやActionsログ**まで完全に匿名化したと保証するものではありません。
- LTX・Gemma・10Erosは既存ライセンスに基づく条件付き再配布です。モデル以外のWorker・Workflow、下流利用条件も順守が必要です。
- GHCRパッケージの可視性はGitHub側で確認し、公開可能になってからPublicへ変更します。モデル同梱GHCRのPush成功とPublic設定は別です。

移行完了後、不要になった `OCI_SOURCE_IMAGE` Secretは削除可能です。

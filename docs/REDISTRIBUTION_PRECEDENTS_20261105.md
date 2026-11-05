# 公開されているLTX-2.3 / Gemma-3再配布事例の実地調査

調査日：2026-11-05

## 調査の前提

- **「公開されている」＝「法的に適法と判断された」ではない。**
- **GitHubにDockerfileがあること**と**実際のDocker/OCIにモデル重みを含めて公開していること**は異なる。
- GHCRやDocker Hubでの「Build and Push成功」は**レジストリ登録の技術的証拠**であり、**匿名Pullの可否・権利者による承認の証明ではない**。
- モデル重みのダウンロードを起動時に行う設計なら、コンテナイメージ自体はモデル重みを再配布していない。

## 具体的な事例

### 1. SceneWorks/ltx-2.3-mlx：LTXとGemmaを同じ公開モデルリポジトリに同梱

出典：https://huggingface.co/SceneWorks/ltx-2.3-mlx

- LTX-2.3由来のMLX量子化モデル(q4/q8)、Gemma-3-12B-ITエンコーダー（5シャード）を同一Hugging Faceリポジトリで配布。ページ上の合計サイズ約124 GB。
- モデルの由来（LightricksとGoogle、変換元）を説明。
- LTX-2 Community LicenseとGoogle Gemma Terms of Useを**別のライセンス**として明示。
- READMEは両者の利用・配布制限を引き継ぐ旨と「ダウンロード・利用により両ライセンスに同意する」旨を説明。
- **公開Model Card上の注意書きが、あらゆる法域で拘束力ある契約を成立させると認められたという資料は未確認。**
- Hugging Faceのリポジトリ配布であり、GHCRのOCI配布例ではない。技術・契約方式を同一視しない。

### 2. Unsloth/LTX-2.3-GGUF：大規模な公開量子化モデル配布

出典：https://huggingface.co/unsloth/LTX-2.3-GGUF/tree/main

- LTX-2.3 GGUFの量子化済み重みを公開。ファイル一覧に巨大なモデルウェイトと約21 KBの `LICENSE`。
- Hugging Face上のライセンスタグは `ltx-2-community-license-agreement`。
- これは**LTX派生モデルを公開配布し、元ライセンスを添える実例**。
- 一覧に `text_encoders/` はあるが、調査対象としての**Gemma-3重みの同梱範囲・Notice義務充足は別途検証が必要**。

### 3. dgrauet/ltx-2.3-mlx：LTXのライセンス全文を同梱

出典：https://huggingface.co/dgrauet/ltx-2.3-mlx/tree/main

- モデル派生ウェイト公開。リポジトリに約19 KBの `LICENSE`。
- READMEで量子化/形式変換は元モデルの派生物であり、LTX-2 Community Licenseの全文が適用されると明記。
- **元のライセンス全文をモデルファイルとともに配る**先例。

### 4. e-dream-ai/gpu-container-ltx：モデル同梱型のGHCRビルド・Push実績

ソース：
- https://github.com/e-dream-ai/gpu-container-ltx/blob/main/Dockerfile
- https://github.com/e-dream-ai/gpu-container-ltx/blob/main/.github/workflows/build-and-push.yml
- GitHub Actions successful run https://github.com/e-dream-ai/gpu-container-ltx/actions/runs/34061620082

- Dockerfile `final` ステージで `wget` によりLTX-2.3 FP8 transformer、Gemma 3 fpmixed、LoRA、VAE、Upscaler等を取得してOCIに同梱する設計。
- ワークフローは `ghcr.io/e-dream-ai/gpu-container-ltx:latest` 等をターゲットにBuild&Push。
- **2026-09-06のBuild and PushジョブはGitHub Actions上でsuccess**（GitHub REST jobsの各ステップもsuccess）。
- リポジトリのルート `LICENSE` はAGPL-3.0。調査したルートREADME・Dockerfileに**LTX/Gemma規約全文の組込み・Gemma指定Notice・受領者への同意導線は確認できない**。**実OCIの全レイヤーの法務ファイルまでは監査していない**ため、「必ず規約違反」と断定しない。
- GHCRパッケージの**匿名Pull可否は未検証**。GitHub Actions Push成功と公開配布は分ける。
- **技術の先行事例**にはなるが、法的にクリアした先例として扱うことはできない。

### 5. Lightricks公式 LTX Desktop：ライセンスNotice＋配布元からのモデル取得

ソース：
- https://github.com/Lightricks/LTX-Desktop/blob/main/NOTICES.md
- https://github.com/Lightricks/LTX-Desktop/blob/main/docs/models-and-loras.md
- https://github.com/Lightricks/LTX-Desktop

- `NOTICES.md` がLTXとGemma 3の権利者・別個のライセンスを列挙し、第三者ソフト依存のライセンスも一覧化。
- デスクトップアプリ自体は配布するが、モデルの重みはユーザーが別途取得する設計。
- ゲート付きモデルについてはHugging Faceへのログイン、モデルのライセンス同意を案内。
- **権利者自身が配布するアプリでさえモデルを個別取得させる設計を採用**している。ただし、これは他の再配布方式を禁止する証拠ではない。

### 6. AlayaLab/AlayaWorld：LTX派生ウェイト公開／Gemmaは除外

出典：
- https://github.com/AlayaLab/AlayaWorld/blob/main/LICENSE
- https://github.com/AlayaLab/AlayaWorld/blob/main/NOTICE
- https://github.com/AlayaLab/AlayaWorld/blob/main/THIRD_PARTY_LICENSES.md

- LTX-2.3由来の派生モデルを配布し、LTX-2ライセンス全文を`LICENSE`に収録。
- `NOTICE`と`THIRD_PARTY_LICENSES.md`で元モデル、改変内容、別の権利者、利用制限を明示。
- **Gemma 3重みは再配布せず、各ユーザーが元配布先から取得する**と明言。

### 7. RunPod/Docker Hub：モデルをイメージに入れない例

- https://github.com/Reuben-Fernandes/LTX23 — Dockerイメージにモデルを含めず、初回起動でHugging Faceから取得。
- https://hub.docker.com/r/maximkramarenko/ltx-trainer-runpod — Docker Hub説明に「The image does not embed model weights」と明記。起動時ダウンロード／永続ボリューム。
- https://hub.docker.com/r/notrius/ltx-23-serverless — 永続ストレージへモデルをPreloadし、Gemmaなどの資産は初回生成時に追加取得される場合あり。
- https://hub.docker.com/r/ai/ltx-2.3 — ページのHugging Faceダウンロード例は、**OCIレイヤーにモデルが同梱されている証明ではない**。

## 実務上、何を参考にできるか

1. **モデルの由来と変更箇所を表にする**（SceneWorks / AlayaWorld）。
2. **LTX、Gemma、ComfyUI、Custom Nodesごとにライセンスを分離し、全文と必須NoticeをOCI内に収録**（AlayaWorld / Lightricks公式のNotice運用）。単なるルートMITやAGPL文書一つでは、モデルの別ライセンスが自動で免除されない。
3. **ダウンロード・利用の規約を明確化し、下流利用制限を法的に有効な形で適用すること**。SceneWorksはモデルカードに規約適用を明記。ただし、契約上の強制力を保証する判例や個別の許可確認は見つけていない。
4. **匿名Pull時の受領者管理、制裁対象への提供、輸出管理は別問題**。公開Model Cardの実例だけで解決したとしない。
5. **GHCR上の実モデル同梱は技術的に実装されている**（e-dream-ai）。しかし先例のライセンス遵守状況は独立に検証する。
6. **公開GHCRと自己所有の非公開GHCRを切り替えられる設計**を保持すると、条件の明確化まで技術開発を続けられる。

## 原文の主要条項

- LTX-2 Community License (2026-01-05) 第3条：
  https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2
  （利用制限の拘束力ある契約への包含、全文・Attachment A・利用ポリシー提供、変更表示、通知維持）
- Gemma Terms of Use (2026-04-01) 第3.1条：
  https://ai.google.dev/gemma/terms
  （利用制限の拘束力ある契約への包含、規約全文提供、変更表示、所定のNoticeファイル）
- 上記条項には、「常にダウンロード前クリック同意が必須」との一律の文言は見当たらない。一方、**公開READMEを読んだだけで法的に十分な契約が成立するとも断定できない**。自動的に法律違反、または必ず合法のどちらにも決めつけない。

## 本キットへの評価

**公開GHCRは引き続き技術・ライセンス両面で成立し得る方針。ただしモデル入りイメージの公開はまだ許可しない。**

関連実例があることは再配布が制度上禁止されていない可能性を強めるが、個々の法務条件の履行を不要にする根拠にはならない。今後は、受領者向け使用条件の実装案を整え、必要に応じて権利者・法律専門家へ個別確認する。並行して実際のOCIとRunPod GPUによる技術検証を進める。

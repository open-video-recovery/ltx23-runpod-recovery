# LTX 2.3 RunPod Recovery Kit

**Independent recovery research — source scaffold, NOT a verified RunPod video endpoint.**

This repository records the historical **LTX 2.3 / 10Eros v1.4** four-model bundle with source URLs, immutable Hugging Face revisions, SHA256 checksums, a CPU-only verification suite, and an experimental independently authored RunPod/ComfyUI worker adapter.

It does **not** use any owner's Docker Hub image as a build dependency, ship model weights, include access tokens, or assert GPU generation has succeeded.

## 完成時の利用方法：2つのコース（配布ライセンスが判断基準）

**A. 公開GHCRの完成済みイメージを指定する** — 再配布条件が満たされた場合の初心者向け最短コース。利用者はGitHubやDockerの操作なしに、自分のRunPod Endpointを作成できます。**現時点では実際のモデル同梱・生成可能な公開イメージは存在しません。** 既存の `oci-contract` / diagnosticsイメージは偽のモデルデータによる転送試験用で、動画は作れません。

**B. 各利用者が自分のGitHubで構築する** — 10Eros等の再配布許諾が未確認、地域・受領者制限がある、公開配布を避けたい場合の独立コース。正規配布元からモデルをクラウドビルド環境へ直接取り込み、SHA256検証後、各自の非公開GHCRにモデル同梱OCIを作る設計です。現時点ではこの巨大モデルの自動ビルドも未完成です。自分用の構築であってもモデルの利用条件は適用されます。

両コースとも**最終的なOCIには4モデル・ComfyUI・Worker・Workflowを同梱**するRirukaChan型を目指します。Network Volumeにモデルを別置きする方式ではありません。利用者のPCへの巨大ダウンロードを必須としませんが、GHCRとRunPodの間では大容量イメージの転送が必要です。

### 公開GHCRへ切り替える法的な条件

- LTX 2.3の **LTX-2 Community License (2026-01-05版)** は再配布を条件付きで許諾しています。第3条では契約として有効な利用制限の継承、全文とAttachment Aの提供、著作権表示維持、変更箇所の告知等が要求されます。単なる地域注意書きだけで全部を満たすとは限りません。
- Gemma 3も条件付き再配布を認めますが、Gemma Terms of Use 3.1で利用制限の契約への組込み、規約全文と所定のNoticeファイルなどが求められます。
- **10Eros作者TenStripは、公式ディスカッション#37でLTX-2ライセンスが適用されると明言しています。** 元のSulphur-2-baseにもLTX-2 Community License全文が含まれています。ただし、作者の回答は無条件のGHCR公開許諾ではなく、元のLTX条件の履行が必要です。
- 禁輸・制裁対象など、実際に配布禁止となる先への提供は、READMEの注意書きでは合法化できません。
- GPLのComfyUIや各Custom Node、Python依存パッケージの条件も別途確認します。

10Eros作者の回答：[Hugging Face Discussions #37](https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37)。元モデルのライセンス：[Sulphur-2-base/LICENSE.txt](https://huggingface.co/SulphurAI/Sulphur-2-base/blob/main/LICENSE.txt)。

法的に配布可能と確認し、必要な受領者向け規約の有効な適用方法を整えた場合に限り、**公開GHCR完成版を初心者コースの先頭にします**。それまではソースとCPU試験用の模擬OCIだけを公開します。技術的・法的な詳細は [配布判断記録](docs/LEGAL_AUDIT.md) にまとめています。


## 公開GHCRのライセンス対応（2026-11-05）

モデル4点を同梱した**公開GHCR版は現在も未承認**です。10Eros作者がLTX-2ライセンスの適用を明言したため、条件付き再配布の道はありますが、匿名Pullでは配布先への拘束力ある条件適用と輸出管理を確認できていません。

対応済み：LTX規約全文（Attachment A含む）、Gemma規約の2026-04-01版保存、Gemma必須Notice、ComfyUI GPL全文の収録。CPUテストでは、未承認のモデル入り公開イメージを拒否する仕組みを検証します。GitHub Actionsで模擬OCIのGHCRビルド・Pull・オフライン復元は実証済みです。

詳細：[配布可否の最新状態](legal/public-ghcr-release-gates.json) / [日本語の判断記録](docs/DISTRIBUTION_POLICY_JA.md) / [権利者への具体的な質問文案](docs/RIGHTSHOLDER_INQUIRIES.md)。

**このリポジトリのMITライセンスはモデル自体をMITに変えるものではありません。** モデル同梱の無審査公開・地域制限の注意書きだけの対応は行いません。

## Status (2026-11-05)

| Component | Status |
| --- | --- |
| Four historical models: files, locations, sizes, SHA256 | Recorded in `models.lock.json` |
| Hugging Face download / independent integrity check | Implemented, CPU fixtures pass |
| Original Python / workflow SHA256 metadata | Recorded in `docs/PROVENANCE.md` |
| Original `workflows/i2v.json` source bytes | **NOT RECOVERED / NOT DISTRIBUTED** |
| Independent `runtime/worker.py` | Experimental, unit-tested only |
| `Dockerfile.experimental` | Incomplete reference, no GPU validation |
| RunPod Endpoint, real MP4, independent image digest | **NOT VERIFIED** |

**Do not deploy or announce this scaffold as a functioning replacement for the retired RirukaChan image.**

## Offline checks

Python 3.10 or newer:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/inspect_workflow.py /path/to/a/candidate/i2v.json
```

The second command requires an actual candidate workflow. This repository intentionally does not ship a guessed workflow JSON.

## Download and verify the four model files

```bash
python3 -m pip install 'huggingface_hub>=0.30,<2'
python3 scripts/download_models.py --model-root /path/to/ComfyUI/models
python3 scripts/verify_models.py --model-root /path/to/ComfyUI/models
```

This downloads **over 42 GB** of weights into a Hugging Face cache and copies them into the target directory; allow more disk space for cache and staging. Model download alone does not implement video generation. Follow each upstream model's access and redistribution terms, including any gated requirements.

All binaries are downloaded by the **individual user directly from the upstream publishers** and verified against recorded SHA256 values. This project does not redistribute any models.

## Historical technical structure

- 10Eros v1.4 FP8 mixed checkpoint (video/audio VAE and vocoder bundled)
- Gemma 3 12B FP4 mixed text encoder
- LTX 2.3 distilled 1.1 **dynamic rank-111 LoRA** (not the different condsafe variant)
- LTX 2.3 spatial upscaler x2 v1.1
- Two-stage sampling: eight first-stage sigmas followed by three refine-stage sigmas
- Native LTX I2V graph and RunPod Worker used several custom nodes

See [OCI and source metadata](docs/PROVENANCE.md) and [workflow provenance](workflows/README.md). Recorded SHA256 values are **historical artifact evidence**, not proof of current Docker image availability.

## Experimental Worker

`runtime/worker.py` demonstrates a newly written input image + prompt → ComfyUI API graph → MP4 bridge. It requires an audited workflow with `__INPUT_IMAGE__`, `__PROMPT__`, and `__SEED__` placeholders, and a working `SaveVideo` output node. It fails closed without the workflow.

`Dockerfile.experimental` is a **non-production prototype**: it neither includes the four model files nor locks the GPU/PyTorch/custom-node stack. It cannot replace the retired endpoint as-is.

## Next milestones

1. Obtain a distributable exact legacy workflow *or* independently implement a matching public ComfyUI API workflow.
2. Pin ComfyUI, Custom Nodes, Torch and CUDA versions; audit file paths and graph compatibility.
3. Build an independently owned Docker image and record immutable manifest digest.
4. Validate a real image-to-video job with a supported RunPod GPU; collect verified MP4, job ID and cost.
5. Only then mark a public release as usable.

## References

- [Original 10Eros model publisher](https://huggingface.co/TenStrip/LTX2.3-10Eros)
- [10Eros author's workflows](https://huggingface.co/TenStrip/LTX2.3-10Eros_Workflows)
- [ComfyUI](https://github.com/Comfy-Org/ComfyUI)
- [RunPod Serverless documentation](https://docs.runpod.io/serverless/overview)
- [日本語での確認手順](docs/PUBLISH_JA.md)

## License and redistribution

This project's newly written experimental code is separate from historical RirukaChan code, whose redistribution terms have not been established here. Original Python and Workflow bytes are **not** committed. Third-party model and node licenses are separate; no permission is inferred from a publicly readable image digest.

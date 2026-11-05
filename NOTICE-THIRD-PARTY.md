# Third-party licenses and notices / 使用条件・出典

This image packages existing third-party model weights and runtime components for RunPod Serverless. The model authors and component developers are not affiliated with this repository and do not endorse or warrant this distribution.

**The repository's MIT license applies only to original recovery-kit code. It does not replace the terms for third-party models, weights, ComfyUI, extensions, or software.**

## Models and upstream sources

| Component | Upstream source | Applicable license / terms |
| --- | --- | --- |
| LTX 2.3 / 10Eros v1.4 fine-tuned checkpoint | [TenStrip / LTX2.3-10Eros](https://huggingface.co/TenStrip/LTX2.3-10Eros) | [LTX-2 Community License](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2); [author's license explanation](https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37) |
| Sulphur model lineage | [SulphurAI / Sulphur-2-base](https://huggingface.co/SulphurAI/Sulphur-2-base) | LTX-2 Community License |
| LTX 2.3 Distilled LoRA | [Comfy-Org / ltx-2.3](https://huggingface.co/Comfy-Org/ltx-2.3) | LTX-2 Community License |
| LTX 2.3 x2 upscaler | [Lightricks / LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3) | LTX-2 Community License |
| Gemma 3 text encoder (conversion) | [Comfy-Org / ltx-2](https://huggingface.co/Comfy-Org/ltx-2) | [Gemma Terms](https://ai.google.dev/gemma/terms) and [Gemma Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy) |
| ComfyUI | [Comfy-Org / ComfyUI](https://github.com/comfyanonymous/ComfyUI) | GPL-3.0 |
| RunPod Python SDK | [RunPod SDK](https://github.com/runpod/runpod-python) | MIT |
| Other runtime dependencies and custom nodes | Original projects indicated by their installed distributions | Their respective upstream licenses and notices apply |

Original developers retain their copyright, trademarks and attribution. Recipients remain responsible for complying with applicable terms, including LTX and Gemma use restrictions and any conditions on further redistribution.

## Legal documents included in the OCI image

The image includes these materials under `/opt/recovery-licenses/`:

- `third_party_licenses/LTX-2-Community-License-2026-01-05.txt` (including Attachment A)
- `third_party_licenses/Gemma-Terms-of-Use-2026-04-01.md` (archived snapshot)
- `third_party_licenses/Gemma-NOTICE.txt` (required notice)
- `third_party_licenses/ComfyUI-GPL-3.0.txt`
- `official-policies/LTX-Acceptable-Use-Policy.pdf`
- `official-policies/Gemma-Terms-Official.html`
- `official-policies/Gemma-Prohibited-Use-Policy-Official.html`
- `official-policies/policy-snapshot.json` (document checksums)
- `NOTICE-THIRD-PARTY.md` (this notice)

The official source websites control where a document has changed. A copy of the Gemma terms here is a dated snapshot; use the current official terms when required.

## Packaging changes and attribution

This release reuses an existing model-bearing OCI image. It repackages one oversized compressed OCI layer into smaller transport layers to meet registry limits and adds a startup restoration script plus license documents. The repository does not claim authorship of third-party checkpoints, source conversions, Python Workers, workflows, or custom nodes.

The packaged software is supplied **as-is**, without a guarantee of fitness for a particular GPU, workflow, or use case. Additional licenses in installed third-party packages are preserved; this NOTICE does not grant rights beyond the applicable upstream licenses.

# Legal and provenance review / リーガルチェック

Reviewed: 2026-11-05. **Technical compliance screening only, not legal advice.**
This review applies to the currently published `Dockerfile.ghcr-smoke` diagnostic
image, NOT a future full image-to-video package.

## A. Diagnostic-only GHCR image

| Item | Assessment |
| --- | --- |
| New `runtime/ghcr_smoke.py` | Authored for this project. MIT license in repository. |
| Python official `python:3.12-slim-bookworm` | Official public base; contains Python/Debian components with their own licenses/notices. |
| `runpod==1.8.1` Python SDK | RunPod Python upstream advertises MIT; preserve notices and verify transitive dependency licenses. |
| RirukaChan / source-account-redacted code or OCI layers | **Not incorporated**. |
| ComfyUI | **Not incorporated in smoke image**. |
| LTX / 10Eros / Gemma / LoRA / VAE binaries | **Not incorporated**. |
| Private keys, HF_TOKEN, RunPod API key | **Not embedded**. |
| GHCR smoke publication | **No identified model redistribution blocker**; final license/secret scan should remain enabled. |

Sources:
- https://github.com/runpod/runpod-python/blob/main/LICENSE
- https://hub.docker.com/_/python
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry

## B. Full future video image: NOT LEGALLY CLEARED

1. **LTX 2.3 and derivatives:** Lightricks distributes under the
   **LTX-2 Community License Agreement**, not a generic permissive software
   license. Usage restrictions and redistribution requirements apply.
   Its public terms identify a USD 10 million annual-revenue threshold for
   entities requiring separate commercial licensing. Read the full terms and
   Attachment A before running or redistributing.
   https://huggingface.co/Lightricks/LTX-2.3/blob/main/LICENSE
2. **10Eros weights:** A public Hugging Face page is not unconditional permission
   to republish binaries. Confirm the exact release's author license and
   applicable LTX derivative obligations before any model redistribution.
   https://huggingface.co/TenStrip/LTX2.3-10Eros
3. **ComfyUI:** GPL-3.0. A future Docker image bundling ComfyUI should retain
   applicable copyright/license notices and provide compliant source access,
   including modifications. The precise implications for integrated work
   require review.
   https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE
4. **Gemma 3 and Custom Nodes:** Review Google's Gemma terms, the exact
   model publisher's conditions, and each custom node's license separately.
5. **Legacy RirukaChan Python and workflows:** File SHA256s and OCI historical
   metadata are published; their source bytes are NOT redistributed, and an
   old accessible layer does not by itself establish reuse permission.
6. **User-provided files, generated content, and service terms:** The person
   creating an endpoint remains responsible for model access terms, RunPod
   service terms, copyrighted inputs, privacy, and applicable content rules.

## C. Required publish gates

- **Smoke image:** PASS on source scope (no legacy code/weights); publishing
  must still pass automated repository scans, image build, self-test, GHCR pull.
- **Full video image:** HOLD. Do not publish third-party binaries, GPL-derived
  code, or legacy workflows without a separate complete license audit.
- **"Working I2V" announcement:** HOLD until a full real GPU run produces an
  independently verified playable MP4 with reproducible image digest.

This project uses a first-party image build and RunPod network-volume model
storage, *not* cross-repository blob copying of a vanished third-party image.

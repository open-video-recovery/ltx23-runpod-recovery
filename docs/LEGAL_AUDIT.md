# Legal and provenance review / 配布条件の確認

Date: 2026-11-05. **Technical licensing assessment, not a legal opinion.**

## Decision (two paths)

**PUBLIC GHCR (full-weight I2V): CONDITIONAL / NOT CLEARED YET.** A publicly
reachable container image containing all four weights may be lawful, but only
if **every** third-party component permits that distribution AND all required
downstream terms, notices, recipients/territory restrictions, source duties,
and export controls are implemented. A disclaimer alone may not satisfy
license clauses requiring **enforceable agreements**.

**USER-BUILT GHCR: FALLBACK / NOT AUTOMATIC LEGAL IMMUNITY.** Users may build
their own bundled OCI through cloud infrastructure and place it in a
private GHCR package to avoid public weight redistribution. The person's
model download, use and transfer to RunPod are still subject to the licenses.
This option is not yet GPU- or large-OCI-build-verified.

**PUBLIC REPOSITORY: SOURCE + FAKE-WEIGHTS OCI TESTS ONLY until gates pass.**
No third-party weight binaries, original legacy source, original RirukaChan
OCI blobs, or working I2V image are currently distributed here.

## Component-by-component assessment

| Component | Governing terms, public-redistribution screening |
| --- | --- |
| Lightricks LTX-2.3 and derivatives | **Conditional redistribution expressly contemplated.** [LTX-2 Community License dated 2026-01-05](https://huggingface.co/Lightricks/LTX-2.3/blob/main/LICENSE), §3. Must include original terms/Attachment A, pass on restrictions as enforceable end-user terms, retain notices, identify changes; §7 export controls/sanctions. It is **not** public-domain or an unrestricted open-source grant. Significant commercial-use/revenue restrictions also apply. |
| TenStrip 10Eros v1.4 FP8 mixed | Derivative of LTX-2.3, and [publisher's model card](https://huggingface.co/TenStrip/LTX2.3-10Eros/raw/main/README.md) says it relies on Sulphur. The README front matter does **not** specify a standalone license or independently authorize all republication terms. **Need to verify publisher's and upstream derivative-specific rights/terms before republishing this checkpoint.** |
| Sulphur source material | [SulphurAI original README](https://huggingface.co/SulphurAI/Sulphur-2-base/raw/main/README.md) credits TenStrip with the I2V derivative. The LTX base terms remain relevant, but separately validate any additional terms imposed by the source model publisher. |
| Gemma 3 / converted Gemma 3 text encoder | [Google Gemma Terms of Use (2026-04-01)](https://ai.google.dev/gemma/terms), §3.1 explicitly contemplates redistribution **subject to** an enforceable downstream use restriction, furnishing the full terms, modification notices and mandatory **Notice** file. Determine treatment of the particular Comfy-Org FP4 conversion. |
| LTX-2.3 distilled rank-111 LoRA, x2 spatial upscaler | Verify the exact revisions' licensing (including LTX derivative grant and Comfy-Org packaging) and carry along applicable notices. Current model-lock hashes show provenance, not legal clearance. |
| ComfyUI | [ComfyUI GPL-3.0 license](https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE). Bundling may require source distribution/access, preservation of notices, and fulfillment of GPL obligations. License compliance of worker integration requires independent review. |
| Custom Nodes and Python dependencies | Individually inspect license files, upstream pins, copies/modifications and dependencies. Do not copy unlicensed legacy Python by assuming OCI readability equals consent. |
| GitHub Container Registry / RunPod | Separate service terms and image distribution settings apply. Public packages may be pulled without the recipient explicitly accepting a click-through. **Confirm how enforceable downstream restrictions will actually be applied before publishing a full-weight public image.** |

## Important distinction: regional notice vs restricted recipient

A regional warning is appropriate **only** when the actual license and relevant
law allow the distribution and merely require an informational warning.

LTX-2.3 §7 addresses export control and sanctions compliance, including
prohibited recipients and jurisdictions. If a transfer is forbidden under
applicable law or the license, a regional disclaimer **does not authorize it**.

This is one reason a public GHCR package may need more than a README: a package
may be downloadable globally without an effective recipient-acceptance gate.
If the requirements cannot be met via public GHCR, use an appropriately
restricted distribution channel or independent recipient builds.

## Public GHCR release gates (must all be checked)

- [ ] TenStrip 10Eros v1.4 redistribution rights and relevant Sulphur-derived
      obligations are independently established, with source references.
- [ ] LTX-2 Community License, full Attachment A, other applicable license
      texts and copyright notices are included with the OCI distribution.
- [ ] Gemma 3 Terms of Use, full terms, mandatory Notice file and
      user restrictions are included/implemented.
- [ ] Real, legally adequate downstream license/acceptance terms exist;
      any required territory/recipient restrictions and service controls work.
- [ ] ComfyUI GPLv3 and every custom node/dependency obligation is fulfilled.
- [ ] Weights and technical build constraints (GHCR layer size/upload timing)
      pass; full image is served by GHCR and pulled at RunPod.
- [ ] Independently verified real GPU generation produces a playable MP4.
- [ ] Distribution is lawful for the operator and intended users under all
      applicable rules. Seek qualified legal review if the enforceable-term or
      territory issues cannot be resolved.

Until all gates are met, **no public full model-weight GHCR package**.

## Technical tests that can proceed now

A tiny OCI image with `FAKE TEST BYTES` can test model chunks split across
separate Docker image layers, GHCR publish/pull, and an offline reconstruction
SHA256 check **without distributing any actual checkpoint**.

These tests do not clear the full production image for distribution and do not
prove ComfyUI/RunPod GPU execution.

## Current distribution scope

This repository uses a cloud-built **image-bundled-model** design: in the
finished version, model weights, ComfyUI, the Worker and the API workflow
must be inside the OCI image. It does NOT require a RunPod Network Volume.
No third-party model binaries are currently redistributed by this repository.

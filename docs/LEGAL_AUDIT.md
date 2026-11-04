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

## 10Eros licensing finding (verified 2026-11-05)

**AUTHOR CONFIRMATION LOCATED.** In [TenStrip's answer to issue/discussion #37,
"Can you add a license for this model?"](https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37),
the original 10Eros creator stated: "It's LTXV2 license, I don't control it."
The reply additionally distinguishes use of generated media from offering a
commercial generation service. This provides material evidence that the author
intends 10Eros to be governed by the original LTX-2 licensing scheme, not a
separate unannounced independent license.

The [upstream Sulphur-2-base repository](https://huggingface.co/SulphurAI/Sulphur-2-base/blob/main/LICENSE.txt)
also ships the January 5, 2026 **LTX-2 Community License**, corroborating
the derivative licensing chain.

[Official Lightricks license index](https://github.com/Lightricks/LTX-2/blob/main/LICENSE)
clarifies that **LTX-2.3 is under the January 5, 2026 LTX-2 Community License**
and should not be silently replaced with the newer license for later releases.

**Assessment:** no independent TenStrip-specific licensing prohibition has been
found, and the author explicitly points to LTX-2 terms. This supports a
*conditional* redistribution route for 10Eros v1.4 under LTX-2 Section 3,
not an unrestricted public GHCR grant. Note that the FP8 mixed learned
checkpoint also credits a quantizer, so verify any separately applicable
contribution conditions if any are identified.

**Not resolved by this confirmation:** LTX-2 Section 3 requires enforceable
downstream-use restrictions, the entire license and Attachment A, source
attribution and change notices; Section 7 imposes export/sanctions obligations.
Gemma 3 separately requires enforceable terms, a complete copy of its terms,
and a mandatory Notice file. These obligations still apply to the full
model-bundled GHCR image even if no new permission from TenStrip is needed.

**Release gate interpretation:** 10Eros-specific author-position evidence
is now **FOUND**. Public GHCR full-weight distribution remains **ON HOLD**
until the other licenses, distribution mechanisms, and technical checks are
satisfied. Do not claim that an informational README is by itself
an enforceable agreement or a sanctions/access-control mechanism.

## Component-by-component assessment

| Component | Governing terms, public-redistribution screening |
| --- | --- |
| Lightricks LTX-2.3 and derivatives | **Conditional redistribution expressly contemplated.** [LTX-2 Community License dated 2026-01-05](https://huggingface.co/Lightricks/LTX-2.3/blob/main/LICENSE), §3. Must include original terms/Attachment A, pass on restrictions as enforceable end-user terms, retain notices, identify changes; §7 export controls/sanctions. It is **not** public-domain or an unrestricted open-source grant. Significant commercial-use/revenue restrictions also apply. |
| TenStrip 10Eros v1.4 FP8 mixed | Derivative of LTX-2.3. **TenStrip confirmed in [official discussion #37](https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37) that the LTX-2 license applies**, and Sulphur upstream includes the same LTX license. No separate creator-specific prohibition was identified. Conditional LTX Section 3 redistribution rules still must be fulfilled; the creator response is not blanket permission to redistribute irrespective of downstream contracts. |
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

- [x] TenStrip author publicly identifies LTX-2 as governing license;
      Sulphur upstream has LTX-2 license text. Remaining conditions apply.
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

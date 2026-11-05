# Third-party attribution and distribution notices

Project: LTX 2.3 / 10Eros RunPod Recovery Kit
Snapshot prepared: 2026-11-05

This repository's MIT license applies **only to independently authored,
copyrightable recovery-kit code**. It does **not** relicense any of the
following third-party models, ComfyUI, custom nodes, converted files or
software packages.

## Models to be included in a future video-enabled OCI

| Component | Upstream model source | License / terms |
| --- | --- | --- |
| 10Eros v1.4 FP8 mixed learned | https://huggingface.co/TenStrip/LTX2.3-10Eros | LTX-2 Community License (2026-01-05), per author https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37 |
| Sulphur-derived lineage | https://huggingface.co/SulphurAI/Sulphur-2-base | LTX-2 Community License; original authors retained |
| Gemma 3 12B FP4 mixed conversion | https://huggingface.co/Comfy-Org/ltx-2 | Gemma Terms of Use and Google's Prohibited Use Policy |
| LTX 2.3 distilled rank-111 LoRA | https://huggingface.co/Comfy-Org/ltx-2.3 | LTX-2 Community License; respect conversion/packaging notices |
| LTX 2.3 x2 spatial upscaler | https://huggingface.co/Lightricks/LTX-2.3 | LTX-2 Community License |
| ComfyUI | https://github.com/Comfy-Org/ComfyUI | GPL-3.0 |
| RunPod Python SDK | https://github.com/runpod/runpod-python | MIT, subject to verification of pinned version |
| Custom Nodes | Future complete pinned dependency manifest | Each original project license; **not audited yet** |

The precise model revisions, SHA-256 hashes and checkpoint destinations
are in models.lock.json. The 10Eros file is a fine-tuned / converted model,
not created by this repository. **No proprietary weights are currently
present in the public source repository or its diagnostic OCI image.**

## Licenses included with this project

* third_party_licenses/LTX-2-Community-License-2026-01-05.txt
  (including Attachment A and use restrictions)
* third_party_licenses/Gemma-Terms-of-Use-2026-04-01.md
  (archived snapshot; compare against official current terms)
* third_party_licenses/Gemma-NOTICE.txt
  (exact required Notice statement)
* third_party_licenses/ComfyUI-GPL-3.0.txt
* The LTX AUP, official Gemma terms and prohibited-use policy:
  snapshots are fetched into OCI by GitHub Actions for technical fixture
  and verified via SHA-256. See scripts/collect_official_policies.py.

The LTX and Gemma licenses require downstream use restrictions to be
included in an **enforceable agreement governing redistribution and use**.
LTX also imposes export/sanctions obligations. Inclusion of these texts
is necessary compliance material; it is **not an automatic legal clearance**
for anonymous public GHCR downloads.

## Change notices

* New RunPod Worker and diagnostic scripts are independent recovery-kit code.
* The intended full OCI applies upstream model conversions already
  distributed by publishers; this project does not claim to have authored
  any checkpoint, conversion, distillation or quantization.
* The project may package third-party files into an OCI image without
  modifying them; any actual modifications must be documented at release.

## Must complete before real model GHCR release

1. Produce a complete software bill of materials with pinned ComfyUI,
   custom nodes, Python wheels, license texts, and corresponding GPL source.
2. Verify license conditions for the 10S nodes or use independently
   authored equivalents if no redistribution grant exists.
3. Include binding downstream use terms, actual policy documents, notices,
   and a compliant distribution/access model.
4. Satisfy applicable export/sanctions restrictions for intended recipients.
5. Audit a full model-bearing OCI, RunPod GPU execution and playable MP4.

Do not suggest endorsement by TenStrip, Lightricks, Google, or RunPod.

# Third-party attribution and distribution notices

Project: LTX 2.3 / 10Eros RunPod Recovery Kit
Snapshot prepared: 2026-11-05

This repository's MIT license applies **only to independently authored,
copyrightable recovery-kit code**. It does **not** relicense any of the
following third-party models, ComfyUI, custom nodes, converted files or
software packages.

## Models in the model-bearing GHCR OCI

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
not created by this repository. **No model weights are committed to this public source repository or its diagnostic OCI image. Model-bearing OCI weights are distributed separately via GHCR and remain subject to the upstream license and acceptable-use terms noted here.**

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

Recipients must comply with the applicable LTX-2 and Gemma model terms,
including their restrictions on permitted uses, redistribution and export.
The upstream license documents govern their respective components; this
NOTICE does not override or weaken those requirements.

## Change notices

* Diagnostic scripts are independently authored recovery-kit code. The full OCI preserves the original legacy third-party Python Worker and Workflow bytes. Their respective redistribution terms and required source/attributions have not been conclusively verified.
* The intended full OCI applies upstream model conversions already
  distributed by publishers; this project does not claim to have authored
  any checkpoint, conversion, distillation or quantization.
* The project may package third-party files into an OCI image without
  modifying them; any actual modifications must be documented at release.

## Distribution and attribution practice

- Keep the model licenses, Gemma NOTICE, acceptable-use terms and this third-party NOTICE together with the image, as bundled in `/opt/recovery-licenses/`.
- Retain original third-party authorship notices and link to upstream projects.
- Follow the relevant terms for redistribution, acceptable use and export.
- Where custom nodes or other bundled runtime components require separate license texts or corresponding source, provide them under their own licenses; no such third-party code is relicensed under this repository's MIT license.
- The image is provided as-is and its compatibility with a given RunPod GPU must be validated independently.

Do not suggest endorsement by TenStrip, Lightricks, Google, or RunPod.

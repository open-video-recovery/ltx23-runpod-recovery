# LTX 2.3 Recovery: verified status — 2026-11-05

## Reproducible CI / GHCR results

- **PASS** official policy snapshot collection and SHA-256 checks: https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41936823780
- **PASS** CPU tests: https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41937445880
- **PASS** build to GHCR, pull published image, and reconstruct split fake-weight fixture with **no network access**: https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41937445861
- **PASS** in the GHCR image: vendored LTX license, Gemma Notice, Gemma terms snapshot, ComfyUI GPL plus three official policy source snapshots, with offline SHA-256 integrity check.
- **FAKE WEIGHTS ONLY** immutable GHCR manifest digest: `sha256:61ff87fc59a4938bc1dfb472074e8b04dca881a340c8c27bef705cbf4ba6f1d4`
- OCI image tag: `ghcr.io/open-video-recovery/ltx23-runpod-recovery:oci-contract` (testing only; package public visibility/anonymous pull not proven).

## Technical / legal unresolved

- Original LTX 2.3 I2V workflow bytes are not recovered or publicly licensed; independent functional equivalent remains unvalidated.
- No full 42GB model-bearing GHCR image has been constructed or distributed.
- No RunPod GPU MP4 generation test for this independent project has been completed.
- **LEGAL RELEASE GATE: BLOCKED.** Public anonymous pulls may not satisfy the enforceable downstream agreement requirements of LTX-2 §3(a) and Gemma §3.1; export/sanctions obligations remain unresolved.
- The included LTX AUP and Gemma Prohibited Use Policy impose restrictions on sexually explicit and other content. A model's ability to generate content does not authorize uses prohibited by its governing license.
- Full model image also needs all dependent custom-node license obligations and a legitimate model/worker provenance chain.

See `legal/public-ghcr-release-gates.json`, `docs/LEGAL_AUDIT.md`,
`docs/RIGHTSHOLDER_INQUIRIES.md` for the exact pending criteria.

**This project is not ready to be described as a successful RunPod endpoint recovery.**

# Historical technical evidence (no binary distributed)

A CPU-only scan of the original image's OCI layers recorded these details on
2026-11-03. These are **technical identifiers, not redistribution permission**.

- Original source: `rirukachan/nend-ltx23@sha256:48e97e1de054d07fbd089dbbfe91432918b8200d1169df4bffcd46d858686441`
- Native model root: `/opt/riruka-ltx/models/`
- App and workflow layer 4: `sha256:9a5114437df38922b3c7590c8201337e30e4b13e09259effd8a88aabbbe125fb`
- Graph layer 5: `sha256:aae00fa6d1657b0481b67efbd8efd08e0432a12e84711346868ccba8d10969a8`
- Worker layer 12: `sha256:6cdef37697012de5cb87a5b5bf8cd2e399b7179aa1504e84533481a29e6fefa4`
- `worker.py` SHA-256: `b9e42d1fe2feba84eac095f071b1a1c1c3aa38dda820567c779fbdab83c7f1e4`
- `ltx_graph.py` SHA-256: `22d69ebe2410dcd7d0e57bf9254350c70a3c03fad1f01d04b36529f281f6326e`
- `workflows/i2v.json` SHA-256: `5af9645230f38e41e5f9e8ed1946f206732cf236ab54b535a71443ca40a2e761`
- Original custom nodes included `hf_ltx_extensions` and `hf_mx`.
- Native 4-model verifier checked that the checkpoint embeds video VAE,
  audio VAE and vocoder tensor groups.

The original pipeline uses 8-step first-stage sigmas and a 3-step refine.
The four model OCI blob digests and exact Hugging Face file hashes are
recorded in `models.lock.json`.

Independent worker, custom nodes, and ComfyUI compatibility remain under
development. No GPU test, completed MP4, or Docker image digest is claimed.

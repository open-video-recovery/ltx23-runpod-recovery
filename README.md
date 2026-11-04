# LTX 2.3 RunPod Recovery Kit

**Independent recovery research — source scaffold, NOT a verified RunPod video endpoint.**

This repository records the historical **LTX 2.3 / 10Eros v1.4** four-model bundle with source URLs, immutable Hugging Face revisions, SHA256 checksums, a CPU-only verification suite, and an experimental independently authored RunPod/ComfyUI worker adapter.

It does **not** use any owner's Docker Hub image as a build dependency, ship model weights, include access tokens, or assert GPU generation has succeeded.

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

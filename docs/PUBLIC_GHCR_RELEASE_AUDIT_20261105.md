# Public GHCR release audit — 2026-11-05

## Decision: BLOCKED (Public exposure already confirmed)

This is a practical compliance and provenance review, **not** a legal opinion.

The immutable image `sha256:434141dc283fe49808b93139de7905a9fb190071fbbe811809b1f021d9f1ceb5` was inspected directly using GHCR Registry API. The [read-only audit run](https://github.com/open-video-recovery/ltx23-runpod-recovery/actions/runs/41989198610) successfully downloaded its manifest, config and final license layer. It deliberately exited nonzero because of unresolved release risks.

**Urgent finding:** GHCR accepted an anonymous bearer token and returned the immutable image manifest without a GitHub login. This image is **already anonymously pullable**, although approval for public distribution has not been established. GitHub's [package visibility instructions](https://docs.github.com/en/packages/learn-github-packages/configuring-a-packages-access-control-and-visibility) say that once a package is Public, it cannot be made Private again. The owner should decide whether to delete the public package/version; deletion does not recall already-downloaded data. No delete or visibility change was performed by this audit.

## README and public repository

- Current root README contains no personal name, source account username, or original Docker Hub reference. The direct model image digest/link was removed while review is pending.
- **Historical Git commit exposure exists:** an older public commit included the originating Docker Hub account in a workflow's source image reference. Editing the latest README or rewriting image config does not remove Git history, PR patches, forks, caches or copies.
- No claim of full anonymous provenance is justified while this public history remains searchable.

## Pinned GHCR image — config and layer inspection

- 23 OCI layers; 74 build history entries. Image config, labels, environment, manifest annotations, entrypoint and build history were inspected.
- No exact source Docker Hub owner marker or legacy project marker was detected in the inspected config/history. One build-history entry still contains a generic home-directory-shaped path; its relation to an individual is unproven.
- 10 small layers had archive entries and selected small text examined. One small legacy layer contains a home-directory-shaped path; another contains GitHub repository references. Such links require attribution/personal ownership classification before asserting anonymity.
- **12 large layers were not scanned end-to-end.** The absence of personal material within model binaries, node packages and large compressed tar entries cannot be guaranteed.
- The license/bootstrap overlay was read directly from the published GHCR image, not inferred from build source.

## License files actually found in GHCR overlay

| Embedded item | Result |
| --- | --- |
| LTX-2 Community License + attachments | Present, 19,197 bytes |
| Gemma Terms snapshot | Present, 10,757 bytes |
| Gemma NOTICE | Present, 97 bytes |
| ComfyUI GPL-3.0 | Present, 35,149 bytes |
| Third-party NOTICE | Present, 3,817 bytes |
| LTX AUP PDF | Present, 83,649 bytes |
| Official Gemma terms HTML | Present, 144,324 bytes |
| Official Gemma prohibited-use HTML | Present, 135,357 bytes |
| Policy snapshot manifest | Present; 3/3 official document SHA-256 hashes match |

Presence **does not prove** that every included third-party runtime component is covered. This image inherits a legacy Python Worker, API workflows, ComfyUI custom nodes and dependencies. Their complete license permissions, applicable notice obligations and availability of corresponding GPL source have **not** been verified.

## Additional legal release blockers

1. [LTX-2 §3(a)](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2) and [Gemma §3.1](https://ai.google.dev/gemma/terms) require downstream use restrictions in enforceable distribution terms. No mechanism ensuring this before anonymous GHCR Pull is confirmed.
2. Original third-party Worker/Workflow redistribution and custom-node license terms are not fully documented. Merely adding model licenses cannot grant additional rights in proprietary runtime code.
3. Export, restricted recipient and applicable use limitations are not enforced by a worldwide anonymous pull.
4. RunPod GPU video generation and distribution usability are unverified; publication is not technical validation.
5. Git history and large layer content have not been cleared for the requested separation of identities.

**Decision:** Do not announce or endorse the image as a cleared public release. Automatic model republishing was disabled pending review. Existing exposure requires a separate package deletion/containment decision; changing README does not revoke anonymous Pull. Any future release should use a clean identity/provenance chain, carry complete relevant rights and terms, and undergo final checks against the exact shipped digest.

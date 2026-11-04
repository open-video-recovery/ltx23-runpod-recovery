# Draft questions for rights holders / 権利者への照会文案

**Not sent.** This is a ready-to-send technical licensing question. Use a
dedicated project address rather than a personal email if anonymity is desired.

## Lightricks / LTX-2.3 licensing

Possible channel: the contact for commercial licensing cited by Lightricks
(`licensing@ltx.io`) or the official GitHub Discussions. Verify that it
accepts redistribution-compliance questions before sending.

**Subject:** Clarification: public GHCR container redistribution of LTX-2.3 10Eros weights

Hello LTX licensing team,

We maintain a noncommercial, community-oriented recovery kit to help individual
users deploy **LTX-2.3 / 10Eros v1.4** in their own RunPod Serverless Endpoint.

The proposed image would contain LTX-2.3-derived checkpoint weights, a Gemma 3
FP4 text encoder, the associated LTX LoRA and upscaler, plus ComfyUI, its
license texts, required notices and the latest applicable acceptable-use
policy. We do **not** sell or host a generation API for others.

The LTX-2 Community License, dated January 5, 2026, §3(a) requires an
**enforceable** downstream agreement carrying §4 and Attachment A. §3(b)
requires a copy of the full license and policies. §7 covers export/sanctions.

1. If our GHCR package is **publicly pullable without login or click-through**,
   can we comply with §3(a) by including the entire LTX-2 license, an explicit
   terms-of-use agreement as an OCI file and GitHub README, and mandatory
   acceptance before first container execution? Or is some form of **consent
   before the image pull** required?
2. If approval before download is required, is there an approved distribution
   channel or published compliance example you recommend for a container
   registry image?
3. Would the public availability of an image that includes the checkpoint pose
   additional concerns under §7 that a standard publisher must address?
4. Please confirm that the 2026-01-05 LTX-2 license governs the LTX-2.3
   checkpoint and any TenStrip 10Eros v1.4 derivatives, consistent with the
   creator's [public explanation](https://huggingface.co/TenStrip/LTX2.3-10Eros/discussions/37).

We will not publish real model weights in a public container until we clarify
the licensing and downstream distribution mechanisms.

Thank you.

## Google Gemma legal / licensing support

**Subject:** Clarification: Gemma 3 FP4-derived text encoder in a public container registry

Hello Gemma team,

We plan to include a ComfyUI-format FP4 conversion of **Gemma 3 12B** as a
text encoder inside a public Docker/OCI image for LTX-2.3 video generation.
The image would include the full April 1, 2026 Gemma Terms of Use, the exact
mandatory Notice file from §3.1, and the prohibited-use policy.

Section 3.1(1) requires downstream use restrictions to be an **enforceable
provision**. Because anyone can pull a public GitHub Container Registry image
without a click-through, would a license and terms inside the image and on
the public repository, plus first-run acceptance, satisfy that requirement?
If not, what acceptance or distribution model is required? Are there specific
obligations for redistributing an FP4 conversion of the text encoder?

We will hold the public model-bearing image pending clarification.

Thank you.

**Neither request has been sent.** A reply from a rights holder is evidence
for the release register, not an automatic substitute for other obligations or
a competent legal assessment.

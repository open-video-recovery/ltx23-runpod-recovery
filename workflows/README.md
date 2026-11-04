# I2V workflow provenance

The historical `workflows/i2v.json` was recorded by a SHA-pinned OCI audit.
Its original file SHA-256 was:

`5af9645230f38e41e5f9e8ed1946f206732cf236ab54b535a71443ca40a2e761`

**The original workflow bytes have not been recovered into this public project.**
Do not substitute an invented workflow or claim that GPU generation is ready.

`python scripts/inspect_workflow.py /path/to/i2v.json` checks a candidate's
hash, required node types, and sigma schedules. An original SHA match is
stronger evidence than a structural match alone.

Recover the original small OCI code layer only through authorized access;
inspect its redistribution terms before publishing any third-party source.
Alternatively, develop a separate workflow from public ComfyUI documentation
and validate it by actually generating video on a GPU.

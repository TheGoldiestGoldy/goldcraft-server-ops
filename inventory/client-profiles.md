# Generated client profiles

Generated: 2026-11-22T00:02:13+00:00. All three archive sizes and SHA-256 values below were independently recomputed from the generated files during the 22 November audit and matched the profile manifest.

| Profile | Target hardware | Recommended heap | Render / simulation | Mods | Shader default | Archive | Size | SHA-256 |
|---|---|---:|---:|---:|---:|---|---:|---|
| Amethyst + Podium | Modern Android phone, Java 21, 3–4 GB heap | 3 GiB | 5/4 | 71 | included, off by default | `goldcraft-profile-mobile-amethyst.zip` | 383,855,165 bytes (366.1 MiB) | `50ba6eb8cd6fdadf34e41adf0407420fbaf7cc79f1731ee60f6b37e77737478b` |
| Basic 8 GB laptop | Older Intel i5, integrated/old laptop GPU, 8 GB RAM | 3 GiB | 6/4 | 70 | included, off by default | `goldcraft-profile-basic-laptop.zip` | 383,837,123 bytes (366.1 MiB) | `3d36b38d912df36e409a71df02b8e1d2fbe7e018903a2c08c48d4fa450602205` |
| 16 GB / GTX 1060 class | i5/i7, 16 GB RAM, GTX 1060-class or 4–6 GB VRAM GPU | 6 GiB | 8/5 | 70 | enabled | `goldcraft-profile-nice-laptop.zip` | 383,837,181 bytes (366.1 MiB) | `20a62ef99733c1047fd3c21a16a8ece0330dc659e0197443fbf89db597106aeb` |

## Validation meaning

The generator's `validated` flag means its Fabric dependency check completed without unresolved dependencies. It does **not** mean the archive was launched on each target device or that the FPS target was measured. The stated **35–45 FPS** is a starting target, not a benchmark or guarantee.

The Amethyst + Podium archive includes Podium 1.1.1; the profile generator refreshed MakeUp Ultra Fast 9.6a. The mobile and basic-laptop profiles ship the shader disabled by default. The 16 GB / GTX 1060-class profile enables it and omits Distant Horizons by design.

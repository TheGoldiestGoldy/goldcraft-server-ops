# Generated client profiles

Generated: 2026-11-23T00:02:13+00:00. All three archive sizes and SHA-256 values below were independently recomputed from the generated files during the 23 November audit, matched the profile manifest, and passed ZIP CRC validation with no bad members.

| Profile | Target hardware | Recommended heap | Render / simulation | Mods | Shader default | Archive | Size | SHA-256 |
|---|---|---:|---:|---:|---:|---|---:|---|
| Amethyst + Podium | Modern Android phone, Java 21, 3–4 GB heap | 3 GiB | 5/4 | 71 | included, off by default | `goldcraft-profile-mobile-amethyst.zip` | 383,855,165 bytes (366.1 MiB) | `f6cc28c3784eb8106dc99756ec16ef6cafb37b8f7cee53d53cb45ec61458fcce` |
| Basic 8 GB laptop | Older Intel i5, integrated/old laptop GPU, 8 GB RAM | 3 GiB | 6/4 | 70 | included, off by default | `goldcraft-profile-basic-laptop.zip` | 383,837,123 bytes (366.1 MiB) | `d3797d3c3e64d42b9e769ced98d81252c7198976281d94d56c768790178c3914` |
| 16 GB / GTX 1060 class | i5/i7, 16 GB RAM, GTX 1060-class or 4–6 GB VRAM GPU | 6 GiB | 8/5 | 70 | enabled | `goldcraft-profile-nice-laptop.zip` | 383,837,181 bytes (366.1 MiB) | `c7a385c44c5bb0d7a2e5f4c6e408f8fc5c0fd12ed66782b7a8b6b7a3d4129a17` |

## Validation meaning

The generator's `validated` flag means its Fabric dependency check completed without unresolved dependencies. It does **not** mean the archive was launched on each target device or that the FPS target was measured. The stated **35–45 FPS** is a starting target, not a benchmark or guarantee.

The Amethyst + Podium archive includes Podium 1.1.1; the profile generator refreshed MakeUp Ultra Fast 9.6a. The mobile and basic-laptop profiles ship the shader disabled by default. The 16 GB / GTX 1060-class profile enables it and omits Distant Horizons by design.

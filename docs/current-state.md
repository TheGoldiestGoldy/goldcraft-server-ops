# Current state

Snapshot generated: 2026-11-16T23:14:33.598396+00:00

## Runtime and hardware

| Item | Value |
|---|---|
| Minecraft | 1.21.1 |
| Loader | Fabric |
| OS / kernel | CachyOS / 7.3.3-1-cachyos |
| CPU | Intel(R) Core(TM) i7-10700F CPU @ 2.90GHz |
| Logical CPUs | 16 |
| GPU | VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 3060 Ti Lite Hash Rate] (rev a1) |
| RAM / swap | 31.25 GiB / 31.25 GiB |
| Disk total / free | 472.94 GiB / 158.32 GiB |

## Server baseline

| Setting | Value |
|---|---|
| Max players / tested target | 20 / 15 |
| View / simulation distance | 8 / 5 chunks |
| Game mode / difficulty | creative / peaceful |
| Heap | 4 GiB initial, 12 GiB maximum, 10 GiB soft maximum |
| GC | Generational ZGC |
| Region compression | lz4 |
| Synchronous chunk writes | false |

## Storage

| Component | Size |
|---|---:|
| Entire server directory | 69.42 GiB |
| Active world | 28.54 GiB |
| Overworld region data | 20.36 GiB |
| VSS/Voxy derived LOD store | 5.01 GiB |
| Archived logs | 10.7 MiB |
| BlueMap | 188.5 MiB |

## Current Distant Horizons values

| Key | Value |
|---|---|
| synchronizeOnLoad | false |
| enableRealTimeUpdates | true |
| maxSyncOnLoadRequestDistance | 128 |
| maxGenerationRequestDistance | 128 |
| generationRequestRateLimit | 4 |
| syncOnLoadRateLimit | 8 |
| globalBandwidthLimit | 4096 |
| playerBandwidthLimit | 2048 |
| enableAdaptiveTransferSpeed | true |
| numberOfThreads | 2 |
| generatorPlan | SURFACE_THEN_CHUNKS |
| chunkGeneratorMode | FEATURES |
| rendererMode | DEFAULT |

## Current VSS/Voxy values

- enabled: false
- max_size_mib: 30720

The VSS service is currently disabled, but the active world's derived store remains on disk.
Read the current incident record in docs/issues/lod-download-loop.md before changing DH or VSS.

## Read-only configuration audit: 20 November 2026 (UTC)

This is a newer **filesystem observation**, not a successful startup or player-load test. The 16 November snapshot above is retained for historical comparison. The dedicated server was not running as a Java process during this inspection, so the values below are **on-disk configuration**, not independently verified active runtime settings.

| Checked item | 16 Nov repository snapshot | 20 Nov local disk observation |
|---|---|---|
| Server mod JAR files | 85 inventoried entries | 82 `.jar` files |
| Disabled mod files | 1 disabled (README) | 1 `.disabled` file |
| DH `synchronizeOnLoad` | false | false |
| DH `enableRealTimeUpdates` | true | false |
| DH `generationRequestRateLimit` | 4 | 20 |
| DH `syncOnLoadRateLimit` | 8 | 50 |
| DH `globalBandwidthLimit` | 4096 | 0 |
| DH `playerBandwidthLimit` | 2048 | 4096 |
| DH `numberOfThreads` | 2 | 2 |
| Server view / simulation distance | 8 / 5 | 8 / 5 |
| Server max players | 20 | 20 |
| Region compression | lz4 | lz4 |
| Synchronous chunk writes | false | false |

**Important:** The changed DH rate limits and bandwidth configuration have not been validated for transfer behavior, memory use, TPS, MSPT, or client FPS. A configured global bandwidth limit of `0` must not be described as a proven effective unlimited rate without confirming the mod's semantics. No recommendation to deploy these settings is implied. The JAR count difference is an inventory discrepancy, not proof that three mods were deliberately removed or that the server can start successfully.

The locally inspected MTR 4.1.0-beta.2, Distant Horizons 3.3.3, and Voxy Server Side JAR SHA-256 hashes **match** their existing entries in [the server mod inventory](../inventory/server-mods.md). No binaries, raw logs, addresses, player data, or live configuration files were uploaded. A full sanitized mod inventory regeneration and controlled restart/performance validation remain outstanding.

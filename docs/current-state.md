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

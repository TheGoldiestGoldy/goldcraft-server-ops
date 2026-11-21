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


## Follow-up snapshot: 21 November 2026 (UTC)

### Server inventory reconciliation

A read-only scan found **82 top-level server JAR files** and one separate disabled file. Of the JARs, **81 top-level Fabric metadata records parsed successfully**; one Feature Recycler JAR has a structurally valid ZIP container but malformed JSON in its fabric.mod.json description. Its loader activation is not established. The 81 parsed IDs, versions and SHA-256 hashes match the current inventory rows. Three old inventory rows are no longer present: Moonlight Lib, PolyWeather and Region Discovery. Their removal reason is unknown. See [server mod inventory](../inventory/server-mods.md).

### Java and host memory snapshot

At 04:02 UTC, the server and client Java processes were both present. The server launcher remained at 4 GiB initial / 12 GiB maximum heap, 10 GiB ZGC soft maximum and 300-second uncommit delay. The client remained at 2,000 MiB initial / 10,336 MiB maximum, with the same 10 GiB soft maximum and 300-second delay. Both live process arguments agreed with those persistent settings.

That single host snapshot showed approximately 2.88 GiB MemAvailable, 12.21 GiB swap used, server RSS 10.46 GiB and client RSS 11.33 GiB. Memory PSI avg10/avg60/avg300 were all 0.00 at the sample instant. These are point-in-time values, not a capacity or stability benchmark. Server view/simulation distance remained 8/5.

The brief 8 GiB soft-maximum / 60-second uncommit-delay experiment was not retained: persistent configuration and the 04:02 live processes were back at 10 GiB / 300 seconds. No controlled before/after test demonstrated an improvement. See [memory-pressure incident](issues/memory-pressure-2026-11-20.md).

### Automation state

The user-level server boot-start unit is enabled. Its 20 November run requested a start through the dashboard bridge and confirmed that the server accepted connections. This proves one successful run, not every reboot or failure mode.

The separate root-owned daily OS update timer was **not installed** at 04:02 UTC on 21 November; systemd reported the unit as not found. The requested 07:00 update schedule must not be treated as active. The temporary memory sampler timer is disabled, and its PSS columns were zero in all 16 captured rows.

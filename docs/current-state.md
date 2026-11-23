# Current state

Historical baseline generated: 2026-11-16T23:14:33.598396+00:00

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

## 16 November Distant Horizons baseline (historical)

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
| generatorPlan | Conflicting historical entries; see the 22 November on-disk audit |
| chunkGeneratorMode | FEATURES |
| rendererMode | DEFAULT |

## Latest VSS/Voxy configuration on disk (file modified 16 November 2026)

- `service.enabled`: true
- `generation.enabled`: false
- `lod.distance.default_chunks`: 256
- `network.bandwidth.per_player_mib_per_second`: 25
- `network.bandwidth.global_mib_per_second`: 75
- `network.send_queue_limit_per_player`: 1024
- `storage.lod_store.enabled`: true
- `storage.lod_store.max_size_mib`: 30720
- `storage.lod_store.backfill.enabled`: false
- `privacy.request_no_map_ingestion`: true
- `far_players.mode`: `on`

The file's last-modified time is 2026-11-16 23:57:48 UTC. This is configuration on disk only. The 22 November audit found no Java server process, so actual VSS serving was not observed. The previous statement that VSS service was disabled was incorrect: the current file enables the service and LOD store while disabling generation and backfill. The active world's derived store remains on disk.
Read the current incident record in docs/issues/lod-download-loop.md before changing DH or VSS.

## Read-only configuration audit: 20 November 2026 (UTC)

This is a newer **filesystem observation**, not a successful startup or player-load test. The 16 November snapshot above is retained for historical comparison. The dedicated server was not running as a Java process during this inspection, so the values below are **on-disk configuration**, not independently verified active runtime settings.

| Checked item | 16 Nov repository snapshot | 20 Nov local disk observation |
|---|---|---|
| Server mod JAR files | 82 JAR files: 81 parseable metadata entries, 1 malformed metadata JAR | 82 `.jar` files |
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

**Important:** The changed DH rate limits and bandwidth configuration have not been validated for transfer behavior, memory use, TPS, MSPT, or client FPS. A configured global bandwidth limit of `0` must not be described as a proven effective unlimited rate without confirming the mod's semantics. No recommendation to deploy these settings is implied. The previous 85-row inventory was stale: three listed IDs (Moonlight Lib, PolyWeather and Region Discovery) are absent from the current folder. The remaining 81 parseable IDs, versions and hashes match; one additional JAR has malformed metadata. This establishes file-level absence, not deliberate removal or loader status.

The locally inspected MTR 4.1.0-beta.2, Distant Horizons 3.3.3, and Voxy Server Side JAR SHA-256 hashes **match** their existing entries in [the server mod inventory](../inventory/server-mods.md). No binaries, raw logs, addresses, player data, or live configuration files were uploaded. The server inventory is now reconciled to 82 JAR files (81 parseable metadata entries and one malformed metadata JAR). Controlled restart/performance validation remains outstanding.


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


## Latest read-only observation: 22 November 2026, 04:33 UTC

This is a filesystem and process snapshot, not a successful restart or gameplay test.

### Server process state

- No Java server process was present at the 04:33 UTC recheck. The dashboard control bridge remained active.
- The latest server log was last modified at 23:44:57 UTC on 21 November. It records a successful startup completion at 22:56:15 UTC, followed later by a player disconnect and a server-console-handler `java.io.IOException: Input/output error`.
- No clean shutdown marker was found in the latest log. The newest file in the crash-reports directory is dated 1 November. No OOM or systemd-oomd event was found in the host journal between 23:30 and 00:10 UTC on 21–22 November.
- The cause of the process disappearance is **unknown**. The console-input exception is an observed event, not proof that it caused the exit. See [the investigation](issues/server-process-exit-2026-11-21.md).
- The user-level boot-start unit is enabled and one invocation on 21 November completed after the bridge reported the server accepting connections. That one success does not establish persistent availability; the server was absent at this later audit.

### Distant Horizons configuration on disk

The file was modified at 22:56:10 UTC on 21 November. These are on-disk values; the server was not running to confirm their effective runtime state.

| Setting | Current file value |
|---|---:|
| realTimeUpdateDistanceRadiusInChunks | 256 |
| maxSyncOnLoadRequestDistance | 256 |
| maxGenerationRequestDistance | 256 |
| generationRequestRateLimit | 20 |
| syncOnLoadRateLimit | 50 |
| synchronizeOnLoad | false |
| enableRealTimeUpdates | false |
| globalBandwidthLimit | 0 (the config comment says 0 disables the limit) |
| playerBandwidthLimit | 4096 KB/s |
| numberOfThreads | 2 |

Compared with the previously published config snapshot, the real-time radius and request distances are now 256; generation/sync request limits are 20/50; real-time updates are disabled; the global cap is disabled; and the per-player limit is 4096 KB/s, and `generatorPlan` is `DISABLED` (the config comment says no distant terrain will be generated). Transfer behavior, memory use, TPS, MSPT and client FPS have not been tested with this configuration. The sanitized snapshot is [configs/DistantHorizons.toml](../configs/DistantHorizons.toml).

### VSS configuration on disk

The current `config/vss-server-config.yaml` was last modified at 23:57:48 UTC on 16 November. The 04:33 UTC recheck confirmed `service.enabled: true`, `generation.enabled: false`, `storage.lod_store.enabled: true`, and `backfill.enabled: false`. Network limits are 25 MiB/s per player and 75 MiB/s globally, with a 1024-item send queue limit. No Java server process was present, so runtime serving was not observed. The sanitized snapshot is [configs/vss-server-config.yaml](../configs/vss-server-config.yaml).

### Server mod inventory

The server directory contains 82 JAR files: 81 parseable metadata records and one malformed Feature Recycler JAR; one separate disabled file is present. At 04:47 UTC the published server CSV was reconciled from 85 to 82 rows by removing three entries for absent files (Moonlight Lib, PolyWeather, Region Discovery). The remaining 82 rows match the on-disk JAR filenames, sizes and SHA-256 values. All 81 parseable IDs, versions and hashes match; Feature Recycler's ID/version remain unverified.

### Client inventory and profile archives

The daily inventory job completed successfully at 00:02:19 UTC on 22 November.

- 100 client JARs; all 100 Fabric metadata records parsed.
- The 00:02 inventory manifest's filenames and byte sizes match the active PollyMC instance's files during the 04:33 audit.
- 14 resource-pack entries, 12 active; 2 shader packs, one active.
- Three generated profiles contain 71, 70 and 70 mods. Their SHA-256 hashes match the generated profile manifest, and a full ZIP CRC check returned no bad members for all three archives.
- systemd reported a 2.9 GiB peak for this one-shot inventory job. This is the job's observed peak, not server memory use.

The profile generator's validation checks dependency resolution. Its 35–45 FPS target is not a hardware benchmark. See [client mod inventory](../inventory/client-mods.md), [client assets](../inventory/client-assets.md) and [generated profiles](../inventory/client-profiles.md).

### Automation state

- `goldcraft-inventory.timer` is enabled for a daily run and completed successfully at 00:02:19 UTC. Its next scheduled trigger was 00:01 UTC on 23 November, with up to five minutes of randomized delay.
- `goldcraft-server-boot.service` is enabled and had one successful observed invocation at 16:45 UTC on 21 November. It is a one-shot start helper, not a continuously supervising service.
- `arch-update.timer` is enabled, but its service runs `arch-update --check`. The installed command's help defines this as checking for available updates and sending a notification; it does not install packages.
- The separate root-owned `goldcraft-daily-upgrade.timer` and service are absent from installed system and user unit paths. Draft source files exist locally but are not installed or end-to-end tested. Daily 07:00 OS installation/reboot automation is therefore **not active**.
- The temporary memory-sampler timer remains disabled.

### Host memory point-in-time

At approximately 04:01 UTC, the host reported about 21 GiB available RAM and 10 GiB swap used. This is a single observation while the Minecraft server process was absent, not a capacity or performance benchmark. No TPS, MSPT or FPS measurements were collected.


## Latest read-only observation: 23 November 2026, 04:35 UTC

This observation follows a host reboot. It is a read-only audit; no server, world, client, or configuration changes were made.

### Server runtime and post-boot start

- Host boot time: 02:12:07 UTC.
- goldcraft-server-boot.service started at 02:12:17. The bridge requested a server start at 02:12:18 and reported Minecraft accepting connections at 02:12:42.
- The Java server process remained present at 04:35:24 UTC (8,586 seconds after its 02:12:17 start), and the configured game TCP listener was present.
- Live JVM arguments remained 4 GiB initial / 12 GiB maximum heap, Generational ZGC, 10 GiB soft maximum, and 300-second uncommit delay.
- This is a second successful observed boot-start after the 21 November invocation. It does not validate unattended OS updates or every failure/recovery path.
- No local Minecraft client Java process was present during this audit.

### LOD service startup and DH/SeedGen evidence

- The server Distant Horizons file was rewritten at 02:12:44 UTC. Its parsed settings match the 22 November snapshot: synchronizeOnLoad=false, real-time updates false, request distances 256 chunks, request limits 20/50, global bandwidth cap 0, per-player cap 4096 KB/s, and generatorPlan=DISABLED.
- The VSS server config matches the published snapshot exactly. It sets service enabled, generation disabled, LOD storage enabled, and backfill disabled; network limits remain 25 MiB/s per player and 75 MiB/s global with a 1024-item queue.
- The startup log confirms the VSS LOD request-processing service started at 02:12:46 and the LOD store became active at 02:12:48. Runtime initialization is confirmed; no client request, transfer byte count, or serving throughput was measured.
- SeedGen 0.9.1 loaded alongside Distant Horizons 3.3.3. It skipped RetrievalQueueDepthMixin and SchedulerPriorityMixin with DH API/constant mismatch warnings. seedgen.json has enabled=true and serverGeneration=false; the DH config has generatorPlan=DISABLED.
- Despite those values, the startup log also emits four "now generating LODs" messages and says distant terrain is full detail because the DH plan asks for it. It also prints a generic note about enableDistantGeneration, but that key is absent from the current DH file. This is contradictory startup evidence, not proof that clients are receiving generated LODs. See [LOD download loop](issues/lod-download-loop.md).
- The startup log contains 3,000 repeated "Trying to mark a block for PostProcessing" warnings and five Seed Renderer "could not grow" warnings. Cause and gameplay impact are unknown.

### Client inventory and configuration

- The configured PollyMC source instance contains 100 client JARs and all 100 Fabric metadata files parse. A fresh sorted filename/size/SHA-256 comparison matches all 100 rows in the published client CSV.
- The server contains 82 JARs: 81 metadata records parse and Feature Recycler metadata remains malformed. A fresh filename/size/SHA-256 comparison matches all 82 server CSV rows.
- The 23 November inventory job completed at 00:02:49 UTC: 14 resource-pack entries (12 active), two shader packs, configured active shader Complementary Unbound r5.9.3, and profiles with 71/70/70 mods. All three profile archives match their manifest SHA-256 values and pass ZIP CRC checks.
- The client-side DH config file differs from the server file: client synchronizeOnLoad=true, real-time updates true, sync distance 384, sync rate 80, and generatorPlan=SURFACE_THEN_CHUNKS; server values are false, false, 256, 50 and DISABLED. The client VSS config enables LOD receive with a 96-chunk client distance. These are on-disk client settings only; no local client process or client-side handshake was captured to establish effective values. Sanitized excerpts are in [client DH settings](../configs/client-DistantHorizons-settings.toml) and [client VSS settings](../configs/vss-client-settings.yaml).

### Automation and measurement status

- goldcraft-inventory.timer remains enabled and its 23 November run succeeded.
- The user-level boot-start helper is enabled and the 23 November post-boot run succeeded.
- arch-update.timer remains a check/notification task (arch-update --check); the root daily-upgrade unit is absent.
- goldcraft-memory-sampler.timer remains disabled because the previous PSS values were invalid.
- No TPS, MSPT, FPS, Spark profile, player-capacity, LOD queue, or client transfer benchmark was collected.

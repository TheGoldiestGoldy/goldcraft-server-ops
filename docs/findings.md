# Findings: what worked and what did not

Baseline snapshot date: 16 November 2026; follow-up findings through 22 November 2026.

## Confirmed successes

### Stable controlled startup

**Status: Confirmed**

The active Linux launcher:

- requires the intended world and Fabric launcher JAR;
- refuses duplicate launches using both a file lock and a port check;
- uses Java 21;
- allocates 4 GiB initially and 12 GiB maximum;
- uses Generational ZGC with a 10 GiB soft maximum;
- writes rotating GC and safepoint logs.

This is a material improvement over earlier launchers that allowed overlapping starts or used inconsistent Java versions.

### World trim

**Status: Confirmed**

The 22 October trim:

- retained 1,883 terrain region files;
- retained 1,925,135 stored chunk slots;
- removed 5,548 terrain regions plus related POI/entity files;
- recovered 23.09 GiB;
- preserved MTR route, station, platform, depot, siding and lift records;
- passed a post-trim smoke start at 20 TPS with 0.7 ms P95 tick time while idle.

The recovery copy of removed files was verified, but the separate full-world backup was incomplete.

### Modern Furniture server patch

**Status: Confirmed**

The stock server JAR called a client-only rendering event and failed on a dedicated server. The locally patched server JAR preserves registration while omitting that event. Validation covered a fresh world, block placement/persistence, a clean save, and a restart.

**Revisit:** check for an upstream fixed release before every mod update.

### Daily operations automation

**Status: Confirmed**

The dashboard bridge and daily inventory timer are enabled. The inventory job publishes exact mod metadata, resource packs, shaders and three tuned client profiles with SHA-256 checksums. Downloads support byte ranges.

### LOD data preservation

**Status: Confirmed**

The active world contains a 5.01 GiB VSS/Voxy derived store. The latest on-disk `config/vss-server-config.yaml` sets `service.enabled: true`, `generation.enabled: false`, and `storage.lod_store.enabled: true`; backfill is disabled. The server was not running at the 22 November audit, so runtime serving was not observed. A separate 5.01 GiB restore artifact also exists under maintenance.

## Confirmed failures or regressions

### Automatic DH/VSS client downloads

**Status: Confirmed symptom; mixed root cause**

Players received large automatic LOD transfers that made normal play impractical. Disabling one in-game DH command did not reliably stop all observed activity because DH and VSS are independent systems. Real-time DH updates were enabled during the earlier symptom period, but are disabled in the latest on-disk config.

Latest on-disk configuration (22 November 2026; the server process was absent, so runtime state is unverified):

- DH `synchronizeOnLoad`: false
- DH real-time updates: false
- DH generation/sync request distances: 256 chunks
- DH generation/sync rate limits: 20 / 50 requests per second
- DH global bandwidth limit: 0 (the config comment says 0 disables the cap)
- DH per-player bandwidth limit: 4096 KB/s
- VSS `service.enabled`: true
- VSS `generation.enabled`: false
- VSS `storage.lod_store.enabled`: true
- VSS backfill: disabled
- VSS network limits: 25 MiB/s per player, 75 MiB/s global; queue limit 1024

The previous statement that VSS serving was disabled was incorrect. The current file enables the service and LOD store, but no Java server process was running during the audit, so active serving was not observed. None of these settings has been validated for transfer behavior, queue growth, memory use, TPS, MSPT or client FPS.

See [LOD download loop](issues/lod-download-loop.md).

### Oversized pregeneration

**Status: Confirmed**

The old Chunky task covered an extremely large area and was force-stopped near 43.2%. It risked generating outside the retained city/rail mask and produced long stalls. Automatic resume is disabled and the old task file was renamed.

### High view distance

**Status: Confirmed regression**

Earlier 24-chunk and 16-chunk server view distances were associated with severe chunk-loading stutter. The current setting is 8 chunks with simulation distance 5.

### ScalableLux

**Status: Confirmed disabled**

ScalableLux 0.3.0 alpha is in the disabled-mod directory. It is not part of the current working baseline.

## Tentative findings

### Rubberbanding with separated players

**Status: Tentative**

The symptom becomes worse when players are far apart. That increases simultaneously active chunk regions, disk reads, entity ticking and potential generation. Historical logs contain 1,227 "can't keep up" matches and 1,369 tick-stall matches, but these are not controlled measurements.

A two-player Spark comparison is still required before attributing the problem to CPU, storage, a specific mod, or networking.

### Error volume

**Status: Tentative interpretation**

The log collector counted more than one million ERROR-labelled lines across 160 files. Many are repeated "No data fixer registered" messages and do not represent one million independent failures. Use targeted crash descriptions and Spark evidence, not the raw total, for decisions.

## Unknowns

- Maximum stable simultaneous player count.
- Busy-city TPS and frame-time behavior at 5, 10 and 15 players.
- Whether every retained legacy chunk is free of removed block IDs.
- Whether the current DH/VSS on-disk settings can serve LODs without forced bulk queues or gameplay impact.
- Actual client LOD transfer rate after the latest restore.
- Which mod dominates two-player separated-region stalls.


## Follow-up findings: 21 November 2026

### Host memory-pressure incident

**Status: Confirmed systemd-oomd action; cause not isolated.**

At 14:24:39 UTC on 20 November, systemd-oomd marked the PollyMC application scope for termination. Its journal recorded 32,621,010,944 of 33,558,482,944 bytes of memory (97.21%) and 30,204,407,808 of 33,557,573,632 bytes of swap (90.01%). The scope then reported 233 processes killed. This confirms a host memory-pressure event and a process-scope kill; it does not establish that every killed process was Minecraft or isolate which application drove the pressure.

A temporary server/client JVM trial lowered the ZGC soft maximum from 10 GiB to 8 GiB and the uncommit delay from 300 to 60 seconds. The persistent files were restored to 10 GiB / 300 seconds by 15:10 UTC. At 04:02 UTC on 21 November, both live Java processes again showed 10 GiB / 300 seconds. No controlled A/B test or TPS/MSPT/FPS measurement proves that the temporary settings helped. Full evidence and limitations are in [the incident report](issues/memory-pressure-2026-11-20.md).

### Server mod inventory reconciliation

**Status: Confirmed filesystem and hash audit; one JAR's load state unknown.**

The current server folder contains 82 JAR files and one separate disabled file. Eighty-one JARs have parseable top-level Fabric metadata, and all 81 IDs, versions and SHA-256 hashes match the updated inventory. Three older rows (Moonlight Lib, PolyWeather and Region Discovery) are absent from the current folder; the reason is unknown. Feature Recycler's ZIP container passes integrity, but its metadata contains an unescaped line break in a JSON string. No matching entry was found in the current latest log, so the loader's treatment of that JAR is not established. Do not count it as a confirmed loaded mod.

### OS update automation status

**Status: Incomplete; daily updates are not active.**

The user-level server boot-start unit is enabled and one run on 20 November completed successfully, requesting a dashboard start and confirming that the server accepted connections. The separate root-owned 07:00 OS update timer was not installed; systemd reported it as not found on 21 November. Draft host-side scripts were not installed or end-to-end tested and are not included in this public repository. Do not claim that daily OS updates or automatic post-update reboot/restart are operational.

### Measurement limitations

The temporary sampler recorded 16 one-minute observations, but every PSS value was zero, so it provides no usable PSS evidence. Its memory-used column was calculated as MemTotal minus MemAvailable, not a strict process-memory total. Three samples did not detect a client process. No TPS, MSPT, FPS, player-count or controlled gameplay measurements were collected. The sampler timer is disabled.


## Follow-up findings: 22 November 2026

### Server process disappearance

**Status: Confirmed process absence and console-input exception; cause unknown.**

At 04:05 UTC on 22 November, no Java server process was present. The latest server log was last modified at 23:44:57 UTC on 21 November and ended with a console-handler `java.io.IOException: Input/output error` after a player disconnect. The log contains no explicit clean-stop marker. The newest crash-report file is dated 1 November, and no OOM/systemd-oomd event was found in the host journal window 23:30–00:10 UTC. The dashboard bridge remained active. None of this establishes why the server process disappeared or whether the console exception caused it. See [the focused investigation](issues/server-process-exit-2026-11-21.md).

### Distant Horizons configuration drift

**Status: Confirmed on-disk change; runtime behavior untested.**

The 21 November 22:56 UTC config file has a real-time update radius and maximum generation/sync request distances of 256 chunks, generation/sync rate limits of 20/50, real-time updates disabled, global bandwidth limit set to 0 (the config comment defines 0 as disabling the cap), and a per-player limit of 4096 KB/s. The same config sets `generatorPlan = DISABLED`; its comment states that no distant terrain will be generated. The server was not running at the 22 November audit, so effective runtime state and transfer behavior are unknown. No performance recommendation is implied.

### Daily client inventory and profile generation

**Status: Confirmed successful one-shot job and verified artifacts.**

The daily inventory service exited successfully at 00:02:19 UTC. Its manifest lists 100 client JARs, 14 resource-pack entries (12 active) and 2 shader packs. A subsequent read-only audit confirmed all 100 metadata records parse and the manifest filenames and byte sizes match the active client directory. The three profile archives contain 71/70/70 mods; recomputed archive sizes and SHA-256 values match the profile manifest. systemd reported a 2.9 GiB peak for the inventory job. The profile script's validation is a dependency-resolution check; the advertised 35–45 FPS is a starting target, not measured performance.

### OS update automation

**Status: Update checks active; unattended installation not active.**

The user-level `arch-update.timer` is enabled, but its service invokes `arch-update --check`. The command help says this checks for updates and sends a notification; it does not install packages. The separate root-owned 07:00 upgrade timer and service are absent from installed systemd paths. Draft source files remain local and uninstalled. Do not claim unattended OS installation, reboot or automatic server recovery is operational.

### Measurement limitations

No TPS, MSPT, FPS, player-count, or controlled gameplay measurement was collected in this audit. The current DH values have not been validated against transfer queues, server tick time, memory or client frame pacing.

# Change and backup timeline

Derived from configuration backups and dated maintenance artifacts. Existence does not prove success.

| Modified (UTC) | Artifact | Type | Size |
|---|---|---|---:|
| 2026-10-21T02:14:27.235970+00:00 | server.properties.before-mtr-rail-distance.bak | file | 0.0 MiB |
| 2026-10-21T23:17:07.127884+00:00 | config/DistantHorizons.toml.before-manual-lod-2026-10-22.bak | file | 0.0 MiB |
| 2026-10-21T23:58:32.121852+00:00 | maintenance/lod-coverage-2026-10-22.csv | file | 0.3 MiB |
| 2026-10-22T00:02:10.866086+00:00 | maintenance/lod-coverage-2026-10-22.html | file | 0.6 MiB |
| 2026-10-22T00:03:13.105698+00:00 | maintenance/lod-coverage-2026-10-22.md | file | 0.0 MiB |
| 2026-10-22T00:09:22.347744+00:00 | config/vss-server-config.yaml.before-manual-lod-2026-10-22.bak | file | 0.0 MiB |
| 2026-10-22T01:52:42.811246+00:00 | server.properties.before-stutter-tuning-2026-10-22.bak | file | 0.0 MiB |
| 2026-10-22T02:57:21.371445+00:00 | maintenance/world-trim-preview-2026-10-22.csv | file | 0.5 MiB |
| 2026-10-22T02:57:21.377451+00:00 | maintenance/world-trim-preview-2026-10-22-mask.json | file | 0.1 MiB |
| 2026-10-22T02:57:22.183212+00:00 | maintenance/world-trim-preview-2026-10-22.png | file | 0.2 MiB |
| 2026-10-22T03:30:53.958559+00:00 | maintenance/world-trim-preview-2026-10-22.md | file | 0.0 MiB |
| 2026-10-22T03:32:43.583980+00:00 | maintenance/world-trim-result-2026-10-22.md | file | 0.0 MiB |
| 2026-10-22T03:40:00.167335+00:00 | config/c2me.toml.before-stutter-tuning-2026-10-22.bak | file | 0.0 MiB |
| 2026-10-23T20:17:22.009199+00:00 | start-server.bat.before-java26-zgc.bak | file | 0.0 MiB |
| 2026-10-24T05:48:54.865961+00:00 | config/vss-server-config.yaml.before-vss-reenable-20261103.bak | file | 0.0 MiB |
| 2026-10-25T02:50:08.460035+00:00 | config/DistantHorizons.toml.before-dh-channel-20261025.bak | file | 0.0 MiB |
| 2026-11-02T22:42:00.063264+00:00 | config/DistantHorizons.toml.before-100fps-baseline-20261103.bak | file | 0.0 MiB |
| 2026-11-03T00:23:09.180774+00:00 | config/DistantHorizons.toml.before-vss-reenable-20261103.bak | file | 0.0 MiB |
| 2026-11-06T23:21:14.396206+00:00 | maintenance/world-backup-before-feature-recycler-20261025-1700 | directory | 23394.6 MiB |
| 2026-11-06T23:22:06.386740+00:00 | stutter-audit-backup-20261024-064230 | directory | 1106.3 MiB |
| 2026-11-06T23:26:17.658982+00:00 | stutter-audit-backup-20261024-181925 | directory | 5882.8 MiB |
| 2026-11-06T23:26:41.662544+00:00 | stutter-optimization-backup-20261025 | directory | 29.3 MiB |
| 2026-11-07T02:48:25.999044+00:00 | start.sh.before-single-instance-20261116.bak | file | 0.0 MiB |
| 2026-11-14T03:45:07.524599+00:00 | maintenance/lod-repair-20261114-034507 | directory | 0.1 MiB |
| 2026-11-14T04:07:39.842755+00:00 | maintenance/startup-repair-20261114-040739 | directory | 0.5 MiB |
| 2026-11-16T01:01:59.725749+00:00 | config/DistantHorizons.toml.before-lod-sync-20261116-191319.bak | file | 0.0 MiB |
| 2026-11-16T01:39:05.764227+00:00 | maintenance/lod-cache-reuse-20261116-013746 | directory | 3703.8 MiB |
| 2026-11-16T19:41:04.376454+00:00 | config/DistantHorizons.toml.before-on-demand-lods-20261116.bak | file | 0.0 MiB |
| 2026-11-16T22:44:29.546210+00:00 | config/DistantHorizons.toml.before-range-validation-20261116.bak | file | 0.0 MiB |
| 2026-11-16T23:01:00.073403+00:00 | maintenance/vss-restore-audit-20261116 | directory | 5.9 MiB |
| 2026-11-16T23:06:49.471740+00:00 | maintenance/vss-restore-20261116 | directory | 5131.8 MiB |


## Operational events (UTC; 20–21 November 2026)

| Time | Event | Verified result / limitation |
|---|---|---|
| 2026-11-20 14:24:39 | systemd-oomd host memory-pressure action | PollyMC scope marked for termination at 97.21% memory and 90.01% swap; 233 processes in that scope were killed |
| 2026-11-20 14:42 | Temporary JVM memory trial | Server and client soft maximum changed from 10 GiB to 8 GiB; uncommit delay from 300 to 60 seconds; no controlled A/B result |
| 2026-11-20 14:52:30–15:09:34 | Temporary memory sampling window | 16 observations; minimum MemAvailable 875.3 MiB; maximum swap used 11,992.2 MiB; PSS fields all zero and excluded |
| 2026-11-20 15:10 | Memory experiment closed | Sampler timer disabled; persistent server/client settings observed restored to 10 GiB soft maximum / 300-second delay |
| 2026-11-20 15:27:42–15:28:10 | Server boot-start unit execution | Dashboard start requested; server confirmed accepting connections; one successful run, not a complete reboot/failure test |
| 2026-11-21 04:02 | Read-only runtime and automation check | Server/client processes present with 10 GiB / 300-second ZGC settings; root daily update timer not installed; memory sampler disabled |


## Operational events (UTC; 21–22 November 2026)

| Time | Event | Verified result / limitation |
|---|---|---|
| 2026-11-21 16:45:10 | User-level server boot-start unit | Bridge reported that Minecraft was accepting connections; one successful invocation only |
| 2026-11-21 22:56:10 | Distant Horizons config file modified | Real-time radius and maximum generation/sync request distances are now 256; rate limits and bandwidth settings also differ from the earlier public config snapshot. No performance test |
| 2026-11-21 23:44:57 | Latest server log update | Ends with console-handler input/output exception; no explicit clean-stop marker; process-exit cause unknown |
| 2026-11-22 00:02:05–00:02:19 | Daily client inventory service | Exited successfully; 100 client mods, 14 resource-pack entries (12 active), 2 shader packs; generated three profile archives |
| 2026-11-22 04:04–04:05 | Read-only host audit | No Java server process present; no OOM event found in the inspected journal window; latest crash report dated 1 November |

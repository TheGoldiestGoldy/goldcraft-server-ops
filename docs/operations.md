# Operations runbook

## Start

Use automation/start-server.sh or the installed Goldcraft dashboard.

The launcher refuses to start if:

- world/level.dat is missing;
- fabric-server-launch.jar is missing;
- another launch holds the lock;
- TCP port 25566 is already occupied.

## Stop

Preferred order:

1. Send the Minecraft stop command.
2. Wait for all dimensions to report saved.
3. Confirm the Java process and port 25566 have exited.

The dashboard bridge sends stop to a process it owns. For an externally started server it uses SIGTERM so Minecraft's shutdown hook can save the world.

## Refresh repository evidence

1. Stop or avoid heavy server experiments.
2. Run tools/collect_snapshot.py.
3. Run tools/render_reports.py.
4. Run tools/sanitize_repository.py.
5. Review git diff.
6. Commit only sanitized evidence.

## LOD safety

Normal play should keep VSS serving disabled and DH synchronizeOnLoad disabled until a deliberate test is planned.

**Historical on-disk warning (22 November 2026):** `config/vss-server-config.yaml` sets `service.enabled: true` and `storage.lod_store.enabled: true`, while generation and backfill are disabled. The latest audit found no Java server process, so runtime serving was not observed. Do not assume VSS is disabled when the server starts; verify the intended config before restarting or running an LOD test. The sanitized snapshot is `configs/vss-server-config.yaml`.

Do not delete world/vss-lod merely to stop transfers. The store is derived data and can be disabled without deleting it.

Before changing LOD settings:

- back up DistantHorizons.toml and vss-server-config.yaml;
- record current store size;
- record player count and location;
- capture a 10-minute Spark profile;
- record client transfer counters;
- change one system at a time.

## Pregeneration safety

Chunky is manual-only.

Before a new task:

- review exact center and radius;
- intersect the task with the retained-world boundary;
- verify free disk space and backup status;
- disable DH/VSS automatic work;
- run a short bounded test;
- measure TPS and disk growth.

Never resume the historical oversized task.

## Recovery priority

1. Preserve world/ and MTR data.
2. Preserve the VSS/Voxy store if LOD recovery is desired.
3. Preserve configuration backups.
4. Regenerate derived BlueMap, client archives and reports when needed.


## Host memory incident and current Java baseline

A host-level memory-pressure incident and systemd-oomd kill occurred on 20 November 2026. See [the incident report](issues/memory-pressure-2026-11-20.md) before changing JVM or operating-system memory settings.

The temporary 8 GiB soft maximum / 60-second uncommit-delay experiment was reverted. The verified persistent and live-process baseline on 21 November 2026 is 10 GiB soft maximum / 300-second uncommit delay for both client and server. Maximum heaps were not changed. Do not treat the temporary trial as a performance improvement: no controlled A/B, TPS, MSPT or FPS result exists.

The temporary memory sampler is disabled. Its 16-row CSV reported zero PSS in every row and used MemTotal minus MemAvailable as its host-memory estimate. Do not use those PSS values or column label as valid process accounting.

## OS updates and post-boot server recovery

**Daily OS updates are not currently enabled.** On 21 November 2026 at 04:02 UTC, the root-owned daily update timer was not found by systemd. A draft updater existed on the host, but its privileged installation did not occur and its full stop-update-reboot-restart path was not end-to-end tested. Do not assume a 07:00 package update will run.

The separate user-level server boot-start unit is enabled. Three observed executions on 20, 21 and 23 November requested a start through the dashboard bridge and confirmed that the server accepted connections. On 23 November, the server process and listener were still present at 04:35 UTC. These observations do not prove every reboot, update-failure or recovery path.

Before enabling a daily updater, require a portable reviewed implementation, root-owned installed files, explicit package-manager failure handling, a graceful world-save stop, verified reboot detection, a successful boot-start test, and a failure-path test proving that the server is either restored or the blocker is reported. Keep this separate from the already-working daily inventory/profile automation.


## Historical observed automation and server state (22 November 2026)

- The daily client inventory timer is enabled and its 00:02 UTC run completed successfully. It regenerated the 100-mod inventory, client asset manifest and three profile archives. The inventory job's observed systemd memory peak was 2.9 GiB.
- The boot-start helper is enabled and three invocations completed successfully on 20, 21 and 23 November. It does not supervise the server continuously; at the 22 November 04:33 audit, no Java server process was present. The 23 November post-boot audit later found the process and listener still present at 04:35 UTC.
- The enabled `arch-update.timer` runs `arch-update --check`, which checks and notifies but does not install packages. The separate root-owned 07:00 upgrade timer is not installed. Do not rely on unattended OS installation or reboot/restart.
- The memory sampler timer is disabled because its prior PSS measurements were invalid.
- The current VSS config enables service and LOD storage on disk, with generation/backfill disabled; actual serving is unverified because no Java server process was present at 04:33 UTC.

### Investigating an unexpected server disappearance

A console-input `IOException` is not by itself proof of a Minecraft crash, clean stop or world corruption. Check the Java process, latest log, dashboard bridge journal, kernel/systemd-oomd events, last world-write times and backup status. Do not restart or perform maintenance against an uncertain world state solely because the console handler reported an input error. Keep raw logs, player identifiers and coordinates out of public reports. See [the 21 November process-exit investigation](issues/server-process-exit-2026-11-21.md).


## Latest observed automation and server state (23 November 2026)

- The host rebooted at 02:12:07 UTC. The enabled boot helper requested a Minecraft start and confirmed the server accepting connections at 02:12:42. The server process and game listener were still present at 04:35:24 UTC. This is one more successful boot-start observation, not continuous supervision or proof of update/reboot recovery.
- The daily inventory job completed at 00:02:49 UTC. The current client and server CSV row sets match local JAR filenames, sizes and SHA-256 values (100 client / 82 server). All 100 client metadata records parse; one of 82 server JAR metadata files remains malformed.
- The startup log confirms VSS request processing and the LOD store initialized. VSS generation/backfill remain disabled, but the service is not disabled. No client transfer or gameplay impact was measured.
- SeedGen 0.9.1 reports two skipped mixins against DH 3.3.3 and emits generation messages that conflict with generatorPlan=DISABLED and serverGeneration=false. Treat this as unresolved; do not assume that the generation path is either working or inactive.
- The client DH/VSS config excerpts differ from the server settings. No local client process or client-side handshake was captured, so effective client settings are unknown.
- arch-update.timer remains check-only; the root-owned daily upgrade unit is absent. The memory sampler timer remains disabled. No TPS/MSPT/FPS or player-capacity measurement was collected.

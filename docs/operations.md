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

The separate user-level server boot-start unit is enabled. Its 20 November execution requested a start through the dashboard bridge and confirmed that the server accepted connections. This is one successful observed run, not proof of all reboot, update-failure or recovery paths.

Before enabling a daily updater, require a portable reviewed implementation, root-owned installed files, explicit package-manager failure handling, a graceful world-save stop, verified reboot detection, a successful boot-start test, and a failure-path test proving that the server is either restored or the blocker is reported. Keep this separate from the already-working daily inventory/profile automation.

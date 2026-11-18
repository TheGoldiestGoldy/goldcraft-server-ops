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

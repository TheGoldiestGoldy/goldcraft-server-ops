# Historical manual LOD control

**Status: archival evidence from the Windows-era workflow, 22–24 October 2026.**
This is not the current CachyOS runbook. The latest on-disk VSS config sets
`service.enabled=true`, `generation.enabled=false`, and
`storage.lod_store.enabled=true`. The server was not running during the
22 November audit, so runtime serving is unverified. Use [the current incident
record](../issues/lod-download-loop.md) and [operations runbook](../operations.md)
before changing either system.

The associated Windows launchers are preserved under
[`automation/windows/`](../../automation/windows/README.md). Their Java paths,
bandwidth limits and startup behavior do not necessarily match the live Linux
service.

## What the historical workflow attempted

1. Start the stopped server with
   [`start-server-with-vss.bat`](../../automation/windows/start-server-with-vss.bat)
   for a deliberately planned VSS session.
2. Enable native DH synchronization with
   `/dh config syncOnLoad.enable true`, then disable it after the test.
3. Export VSS diagnostics twice, roughly 60 seconds apart, and compare
   `receivedColumns` only when the connection identifier is unchanged.
4. Keep DH distant generation off until missing legacy block IDs, SQLite errors and
   server tick stalls were understood.

The intended design was to send already prepared LOD data without silently resuming
unbounded pregeneration. In practice, DH and VSS were independent systems, and
disabling one did not prove that the other had stopped. That ambiguity contributed
to the later client download-loop incident.

## Historical VSS backfill controls

The old workflow used
[`vss-backfill-on.bat`](../../automation/windows/vss-backfill-on.bat), followed by
`/vsslod reload`, to start a bounded backfill test. It used
[`vss-backfill-off.bat`](../../automation/windows/vss-backfill-off.bat) and another
reload to stop after the current column.

The last recorded backfill prepared **zero** new columns while skipping 54,305
already cached columns. Earlier sessions prepared roughly 67–85 columns per second.
Those figures measure server cache preparation, not client download speed.

## Historical speed observations

- One VSS configuration allowed 25 MiB/s per player and 75 MiB/s total.
- A client log nevertheless recorded an adaptive 64 KiB/s slowdown after a large
  latency spike.
- Native DH had a separate 500 KiB/s per-player cap in this older snapshot.
- Raising a byte-rate ceiling could not establish a safe chunks-per-second target
  while stalls and missing block IDs remained uncontrolled.

These values are retained as experiment evidence only. The generated
[current state](../current-state.md) is authoritative for today's configuration.

See the [sanitized coverage report](./lod-coverage-2026-10-22.md) for aggregate evidence from the terrain stored at the time. Exact-coordinate maps and CSV data are retained privately.

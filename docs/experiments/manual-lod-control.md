# Historical manual LOD control

**Status: archival aggregate from an older workflow.**

## What the workflow attempted

1. Keep ordinary server startup separate from deliberate LOD-transfer tests.
2. Enable one LOD transport at a time.
3. Compare diagnostics before and after a fixed test window.
4. Keep distant generation disabled until legacy block and database errors were understood.

## Confirmed result

Distant Horizons and the server-derived LOD system behaved as independent producers and transports. Disabling one did not prove that the other, real-time updates or client-local generation had stopped.

An earlier bounded backfill found that the requested columns were already cached and prepared no new data. Higher byte-rate ceilings did not solve latency spikes or prove acceptable gameplay.

## Retained decision

Bulk LOD delivery remains disabled during ordinary play. Future testing must isolate one transport, use a clean client, record queue and frame-time behavior, and define a rollback before enabling it.

See the [LOD incident record](../issues/lod-download-loop.md) and [aggregate coverage study](./lod-coverage-2026-10-22.md).

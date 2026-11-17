# LOD coverage study, October 2026

**Status: aggregate public summary.**

A read-only comparison examined three data sources:

- saved Overworld terrain;
- server-side derived LOD data;
- client-side Distant Horizons metadata and cached detail.

## Confirmed findings

- The server-derived store covered most, but not all, saved terrain.
- Client Distant Horizons data covered a much smaller and fragmented subset.
- Client hash and revision records were metadata, not proof that complete full-height LOD data existed.
- Large bounding boxes overstated real coverage because the stored areas contained gaps and narrow corridors.
- Different LOD systems used different cell sizes and could not be compared by row count alone.

## Operational implication

The presence of a large cache does not prove that a joining player already has complete usable LODs. Any delivery strategy must measure transferred bytes, queue behavior and frame-time impact on a clean client.

Exact coordinates, component boundaries, maps and per-region datasets remain in the private evidence archive.

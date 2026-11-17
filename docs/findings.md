# Findings: what worked and what did not

Last reviewed: 16 November 2026.

This public report contains aggregate technical evidence only. Player identifiers, raw logs, infrastructure addresses, machine-specific storage details and exact world coordinates are excluded.

## Confirmed successes

### Controlled startup

**Status: Confirmed**

The tested launcher uses the intended Fabric world, rejects duplicate server processes and uses Java 21 consistently. This corrected older startup methods that could overlap or select inconsistent Java installations.

### Reviewed world maintenance

**Status: Confirmed**

A reviewed world trim removed unused generated terrain while preserving the retained city/rail area and MTR records. A recovery copy was verified, and the retained world completed a post-maintenance smoke start at normal idle tick rate.

Exact masks and coordinate maps remain private.

### Modern Furniture compatibility patch

**Status: Confirmed**

The stock server build called a client-only rendering event and failed on a dedicated server. A local server-side patch preserved content registration while omitting that event. Validation covered a fresh world, block placement and persistence, clean save and restart.

**Revisit:** check for an upstream fixed release before every mod update.

### Client inventory and profiles

**Status: Confirmed**

The mod inventories, resource-pack list, shader selection and three client performance profiles are generated from the tested installation. Published SHA-256 values allow players to verify exact files without redistributing third-party binaries through this repository.

### LOD data preservation

**Status: Confirmed**

Previously generated LOD data was preserved while automatic bulk serving was disabled during troubleshooting. This allows later controlled comparison without forcing large transfers during ordinary play.

## Confirmed failures or regressions

### Automatic LOD transfers

**Status: Confirmed symptom; mixed root cause**

Clients received large background LOD queues that made ordinary play impractical. Distant Horizons and the server-side derived-data system are independent, so disabling one path did not necessarily stop the other or client-local generation.

Current containment keeps bulk synchronization disabled while preserving the generated data. See [LOD download loop](issues/lod-download-loop.md).

### Oversized pregeneration

**Status: Confirmed**

An earlier pregeneration plan covered an unnecessarily large area, caused long stalls and risked generating outside the reviewed play area. Automatic resume remains disabled. Future pregeneration must use a reviewed boundary and checkpointed tests.

### Excessive view distance

**Status: Confirmed regression**

Earlier high server view-distance settings were associated with severe chunk-loading stutter. The active baseline now uses a conservative distance while controlled capacity testing remains incomplete.

## Tentative findings

### Rubberbanding with separated players

**Status: Tentative**

Rubberbanding becomes worse when players are far apart, which increases simultaneously active chunk regions, reads, ticking and possible generation. Historical evidence supports tick pressure but does not identify CPU, storage, networking or one mod as the dominant cause.

A controlled comparison with server profiling is still required.

### Historical error volume

**Status: Tentative interpretation**

Archived logs contain many repeated data-fixer and startup messages. Their aggregate count is not a count of independent failures. Decisions should use targeted crash records and controlled profiling instead.

## Unknowns

- Maximum stable simultaneous player count.
- Busy-area tick and frame-time behavior at increasing player counts.
- Whether every retained legacy chunk is free of removed block identifiers.
- Whether real-time LOD updates can run without forced bulk synchronization.
- Which subsystem dominates separated-player stalls.

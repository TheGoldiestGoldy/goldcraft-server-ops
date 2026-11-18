# Findings: what worked and what did not

Snapshot date: 16 November 2026.

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

The active world contains a 5.01 GiB VSS/Voxy derived store. VSS serving is disabled, but the data is present. A separate 5.01 GiB restore artifact also exists under maintenance.

## Confirmed failures or regressions

### Automatic DH/VSS client downloads

**Status: Confirmed symptom; mixed root cause**

Players received large automatic LOD transfers that made normal play impractical. Disabling one in-game DH command did not reliably stop all observed activity because DH and VSS are independent systems and real-time DH updates remained enabled.

Current protective state:

- DH synchronizeOnLoad: false
- DH request distance: 128 chunks
- DH rate limits: 4 generation / 8 sync requests per second
- DH per-player bandwidth: 2 MiB/s
- VSS service: disabled
- VSS store: preserved

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
- Whether DH real-time updates alone can run without forced bulk sync.
- Actual client LOD transfer rate after the latest restore.
- Which mod dominates two-player separated-region stalls.

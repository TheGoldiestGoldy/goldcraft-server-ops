# Issue: rubberbanding when players separate

## Symptom

Rubberbanding becomes more noticeable when multiple players travel or build in distant areas.

## Confirmed evidence

- Historical logs contain repeated server-behind and tick-stall warnings.
- Earlier high server view-distance settings were associated with severe chunk-loading stutter.
- The world contains substantial generated terrain and many world-generation, biome, building, furniture, transit and LOD-related mods.
- Several historical crashes involved watchdog timeouts or chunk generation/loading.

## Tentative mechanism

Separated players keep multiple distant chunk regions active. This increases reads, lighting, entity and block-entity work, and possibly generation. The evidence supports server tick pressure but does not identify one bottleneck.

## Required experiment

Run three equal-duration server profiles under the same build and settings:

1. One player stationary in the main play area.
2. Two players together in the same area.
3. Two players separated into coarse test regions while moving.

For each run record:

- MSPT percentiles and TPS;
- hottest server-thread stacks;
- chunk generation and load time;
- disk utilization and I/O wait;
- heap occupancy and garbage-collection pauses;
- network throughput;
- only coarse test regions, never exact player home locations.

## Decision rule

- High server-thread CPU: reduce expensive ticking or world mods, or lower view distance.
- High I/O wait: improve storage behavior, pregenerate only reviewed regions, or reduce concurrent chunk loads.
- Low MSPT with client rubberbanding: investigate networking and client prediction.
- Large garbage-collection pauses: revisit heap sizing and allocation sources.

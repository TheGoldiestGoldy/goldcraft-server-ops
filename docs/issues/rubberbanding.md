# Issue: rubberbanding when players separate

## Symptom

Rubberbanding becomes more noticeable when two players travel or build far apart.

## Confirmed evidence

- Historical logs contain 1,227 "can't keep up" pattern matches and 1,369 tick-stall matches.
- The server previously used view distances of 24 and 16; current distance is 8 with simulation 5.
- The world contains about 20.36 GiB of Overworld region data.
- The server runs many world-generation, biome, building, furniture, MTR and LOD-related mods.
- Several historical crashes were watchdog or chunk-generation/loading failures.

## Tentative mechanism

Separated players keep multiple distant chunk regions active. This increases chunk reads, lighting, entity/block-entity work and possibly generation. The evidence supports server tick pressure, but it does not identify one bottleneck.

## Required experiment

Run three 10-minute Spark profiles under the same build and server settings:

1. One player stationary in the city.
2. Two players together in the city.
3. Two players at least 2,000 blocks apart while moving.

For each run record:

- MSPT percentiles and TPS;
- hottest server-thread stacks;
- chunk generation and load time;
- disk utilization and I/O wait;
- heap occupancy and GC pauses;
- network throughput;
- player coordinates only as coarse test regions, not exact home locations.

## Decision rule

- High server-thread CPU: reduce expensive ticking/world mods or view distance.
- High I/O wait: improve storage behavior, pre-generate only reviewed regions, or reduce concurrent chunk loads.
- Low MSPT but client rubberbanding: investigate network and client prediction.
- Large GC pauses: revisit heap, allocation sources and mod memory use.

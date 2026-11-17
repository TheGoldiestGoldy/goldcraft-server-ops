# Performance experiment history

## View-distance reduction

Early high-distance settings produced severe chunk-loading stutter. A lower conservative baseline improved stability, especially when players occupied distant regions.

**Decision:** keep conservative distances until a controlled capacity test justifies an increase.

## Reviewed world trim

A reviewed maintenance pass removed unused generated terrain, preserved the retained transit data and passed an idle smoke test at normal tick rate.

**Result:** successful and retained. Exact boundaries and recovery locations remain private.

## Modern Furniture validation

- Stock server build: failed because it initialized a client-only rendering event.
- Local server patch: started, registered content, saved placed blocks and loaded them after restart.

**Result:** patch retained; an upstream replacement remains preferable.

## Pregeneration

An oversized unattended generation task caused stalls and was stopped before completion.

**Result:** failed as an unattended strategy. Future tasks must be bounded, reviewed and checkpointed.

## LOD delivery

Automatic serving or backfill created unwanted client work. The available data remains useful, but automatic normal-play delivery is not accepted without controlled comparison.

**Result:** bulk delivery disabled; isolated testing required.

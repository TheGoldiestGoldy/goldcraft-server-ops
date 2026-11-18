# Performance experiment history

## View-distance reductions

| Stage | Server view distance | Result |
|---|---:|---|
| Early baseline | 24 | Severe chunk-loading stutter |
| First reduction | 16 | Better, but still costly for distant players |
| Current | 8 | Chosen stability baseline |
| Current simulation | 5 | Reduced active ticking radius |

**Decision:** keep 8/5 until a controlled player-capacity test justifies increasing it.

## World trim, 22 October 2026

- Removed 23.09 GiB.
- Preserved 1,883 terrain regions.
- Preserved MTR records.
- Idle post-trim Spark check: 20 TPS, 0.7 ms P95 tick.
- VSS, DH automatic work and Chunky were off during the smoke test.

**Result:** successful and retained.

## Modern Furniture validation

- Stock server JAR: failed due to client-only model initialization.
- Patched server JAR: started, registered content, saved placed content and loaded it after restart.

**Result:** patch retained; upstream replacement remains preferable.

## Chunky

- Historical task used oversized bounds.
- Force-stopped near 43.2%.
- Automatic resume disabled.
- Missing legacy registry entries were observed.

**Result:** failed as an unattended strategy. Future tasks must be small, reviewed and manual.

## DH and VSS

- Automatic serving/backfill created unwanted client work.
- VSS cache preparation once reached roughly 67-85 columns/s.
- Most recent backfill prepared zero new columns and skipped 54,305 cached columns.
- Native DH and VSS transfer limits are independent.

**Result:** data is useful, but automatic normal-play delivery is not accepted. Controlled A/B testing is required.

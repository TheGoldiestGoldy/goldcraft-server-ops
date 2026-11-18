# Issue: forced or repeating LOD downloads

## Symptom

Clients displayed large LOD download queues, sometimes hundreds of thousands of remaining items, even when pregeneration was not running. Disabling one DH command did not consistently stop the observed download behavior.

## Confirmed facts

- Distant Horizons and VSS/Voxy are separate LOD systems.
- The active world still contains a 5.01 GiB VSS/Voxy store.
- VSS serving is currently disabled.
- DH synchronizeOnLoad is currently false.
- DH real-time updates are currently true.
- DH request distance is currently limited to 128 chunks.
- A prior VSS backfill skipped 54,305 already cached columns and prepared zero new columns.
- A client log recorded adaptive slowdown to 64 KB/s after a latency spike.

## Likely explanation

More than one producer/transport was active during earlier tests. Turning off DH sync alone would not stop VSS, and turning off VSS would not necessarily stop DH real-time updates or client-local generation.

## Current containment

- VSS enabled: false
- DH synchronizeOnLoad: false
- DH generation/sync rates reduced
- Existing LOD stores preserved
- Automatic Chunky resume disabled

## Next controlled test

1. Start with both VSS and DH sync off.
2. Join one client and prove that no bulk queue starts.
3. Enable only VSS and measure for 10 minutes.
4. Reset and enable only DH synchronizeOnLoad.
5. Compare bytes, queue counts, TPS and client frame time.
6. Keep the better system and disable the other for normal play.

## Success criterion

Joining the server must not block ordinary play. Background LOD transfer may continue only if its queue, bandwidth and frame-time impact remain bounded and the player can opt out.

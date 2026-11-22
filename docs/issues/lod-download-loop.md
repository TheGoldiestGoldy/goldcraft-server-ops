# Issue: forced or repeating LOD downloads

## Symptom

Clients displayed large LOD download queues, sometimes hundreds of thousands of remaining items, even when pregeneration was not running. Disabling one DH command did not consistently stop the observed download behavior.

## Confirmed facts

- Distant Horizons and VSS/Voxy are separate LOD systems.
- The active world still contains a 5.01 GiB VSS/Voxy store.
- The current on-disk VSS config sets `service.enabled: true`, `generation.enabled: false`, and `storage.lod_store.enabled: true`; backfill is disabled.
- DH `synchronizeOnLoad` is false.
- DH real-time updates are false.
- DH generation/sync request distances are 256 chunks.
- DH generation/sync rate limits are 20/50 requests per second.
- DH global bandwidth limit is 0 (the config comment says 0 disables the cap); per-player limit is 4096 KB/s.
- The server was not running during the 22 November 04:33 audit, so runtime serving was not observed.
- A prior VSS backfill skipped 54,305 already cached columns and prepared zero new columns.
- A client log recorded adaptive slowdown to 64 KB/s after a latency spike.

## Likely explanation

More than one producer/transport was active during earlier tests. Turning off DH sync alone would not stop VSS, and turning off VSS would not necessarily stop DH real-time updates or client-local generation.

## Latest on-disk settings (22 November 2026; runtime unverified)

- VSS service: enabled in config; generation and backfill disabled; LOD store enabled
- DH synchronizeOnLoad: false
- DH real-time updates: false
- DH request distances: 256 chunks
- DH generation/sync rates: 20 / 50 per second
- DH global bandwidth limit: 0 (the config comment says this disables the cap)
- DH per-player bandwidth: 4096 KB/s
- Existing LOD stores preserved
- Automatic Chunky resume disabled

The server was not running at the 04:33 UTC audit. These are settings on disk, not measured serving or containment behavior. The earlier statement that VSS serving was disabled was incorrect; the current config sets `service.enabled: true`. No TPS/MSPT/FPS or queue behavior has been measured with these settings.

## Next controlled test

1. Prepare a test configuration with VSS `service.enabled: false` and DH `synchronizeOnLoad: false`; verify the effective config after reload/restart before allowing a client to join.
2. Join one client and prove that no bulk queue starts.
3. Enable only VSS and measure for 10 minutes.
4. Reset and enable only DH synchronizeOnLoad.
5. Compare bytes, queue counts, TPS and client frame time.
6. Keep the better system and disable the other for normal play.

## Success criterion

Joining the server must not block ordinary play. Background LOD transfer may continue only if its queue, bandwidth and frame-time impact remain bounded and the player can opt out.

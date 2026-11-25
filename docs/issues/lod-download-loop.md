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

## Historical on-disk settings (22 November 2026; runtime not observed at that audit)

- VSS service: enabled in config; generation and backfill disabled; LOD store enabled
- DH synchronizeOnLoad: false
- DH real-time updates: false
- DH request distances: 256 chunks
- DH generation/sync rates: 20 / 50 per second
- DH global bandwidth limit: 0 (the config comment says this disables the cap)
- DH per-player bandwidth: 4096 KB/s
- Existing LOD stores preserved
- Automatic Chunky resume disabled

The server was not running at the 04:33 UTC audit. These were settings on disk at that time, not measured serving or containment behavior. The earlier statement that VSS serving was disabled was incorrect; the current config sets `service.enabled: true`. No TPS/MSPT/FPS or queue behavior has been measured with these settings.

## Next controlled test

1. Prepare a test configuration with VSS `service.enabled: false` and DH `synchronizeOnLoad: false`; verify the effective config after reload/restart before allowing a client to join.
2. Join one client and prove that no bulk queue starts.
3. Enable only VSS and measure for 10 minutes.
4. Reset and enable only DH synchronizeOnLoad.
5. Compare bytes, queue counts, TPS and client frame time.
6. Keep the better system and disable the other for normal play.

## Success criterion

Joining the server must not block ordinary play. Background LOD transfer may continue only if its queue, bandwidth and frame-time impact remain bounded and the player can opt out.


## Runtime and compatibility follow-up: 23 November 2026

The server was running after the 02:12:07 UTC host reboot. Its startup log records the VSS LOD request-processing service starting at 02:12:46 and the LOD store becoming active at 02:12:48. The current VSS server config has service.enabled=true and storage.lod_store.enabled=true, while generation.enabled=false and backfill.enabled=false. Runtime initialization is therefore confirmed for serving existing stored LOD data. No client request, transfer byte count, queue depth or throughput was measured.

The same startup log records Distant Horizons 3.3.3 and SeedGen 0.9.1. SeedGen reports that RetrievalQueueDepthMixin was skipped because the DH method no longer uses the expected constant 20, and SchedulerPriorityMixin was skipped because the DH method signature differs. The current SeedGen config has enabled=true and serverGeneration=false. The current DH server config has generatorPlan=DISABLED, whose comment says no distant terrain will be generated. However, SeedGen's startup log also emits four "now generating LODs" messages, reports distantTerrain=AUTO and full detail, and prints a generic note that clients receive LODs through DH server generation. That same log line references enableDistantGeneration, which is absent from the current DH config. These messages conflict and do not prove that LODs are being generated for or transferred to clients.

The latest startup log also contains 3,000 PostProcessing warning-pattern matches and five Seed Renderer "could not grow" warnings. No root cause or player-visible impact is established. The raw log and all block coordinates, world identifiers and seed values are intentionally excluded.

The configured PollyMC client DH file differs from the server file: synchronizeOnLoad=true, enableRealTimeUpdates=true, maxSyncOnLoadRequestDistance=384, syncOnLoadRateLimit=80 and generatorPlan=SURFACE_THEN_CHUNKS, compared with server values false, false, 256, 50 and DISABLED. Its VSS client file has LOD receive enabled and distance_chunks=96. No local client process or client-side handshake was captured, so these are file-level observations only. Sanitized excerpts are [client DH settings](../../configs/client-DistantHorizons-settings.toml) and [client VSS settings](../../configs/vss-client-settings.yaml).

### Revised controlled-test requirements

1. In a maintenance window, record and verify the effective DH, VSS and SeedGen settings after reload/restart. Treat them as three separate LOD subsystems.
2. Join one test client and record baseline queue counts, bytes transferred, TPS/MSPT, memory and client frame time.
3. Test VSS alone with DH synchronization/generation and SeedGen generation held off; record actual bytes and queue behavior.
4. Reset, then test DH alone.
5. Reset, then test SeedGen separately. Resolve the two skipped-mixin warnings and the contradictory startup messages before treating its generation path as understood.
6. Compare results and retain the smallest bounded configuration that meets the success criterion. Do not change the live server during ordinary play.

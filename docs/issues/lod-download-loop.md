# Issue: forced or repeating LOD downloads

## Symptom

Clients displayed very large LOD download queues even when pregeneration was not running. Disabling one Distant Horizons command did not consistently stop the observed activity.

## Confirmed facts

- Distant Horizons and the server-side derived-data system are separate LOD paths.
- Previously generated LOD data remains preserved privately.
- Bulk server-side derived-data serving is currently disabled.
- Automatic Distant Horizons synchronization on join is currently disabled.
- Real-time updates and client-local generation are separate behaviors.
- Earlier client evidence recorded severe adaptive slowdown after a latency spike.

## Likely explanation

More than one producer or transport was active during earlier tests. Turning off one synchronization option would not stop the other server system, real-time updates or client-local generation.

## Current containment

- Bulk synchronization is disabled.
- Generation and synchronization rates use conservative limits.
- Existing LOD stores remain preserved.
- Automatic pregeneration resume is disabled.

## Next controlled test

1. Start with both server LOD transfer paths disabled.
2. Join one client and prove that no bulk queue starts.
3. Enable only one server path and measure for ten minutes.
4. Reset, enable only the other path and repeat.
5. Compare transferred bytes, queue behavior, tick rate and client frame time.
6. Keep the better system and disable the other during ordinary play.

## Success criterion

Joining the server must not block ordinary play. Background LOD work may continue only if queue growth, bandwidth and frame-time impact remain bounded and the player can opt out.

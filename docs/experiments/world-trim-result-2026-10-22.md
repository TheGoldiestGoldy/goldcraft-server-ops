# City and railway Overworld trim: applied

Applied on 22 October 2026 at 04:28 BST while the dedicated server was stopped.

- Kept exactly **1,883** terrain region files and **1,925,135** stored chunk slots inside the privately reviewed mask.
- Removed **5,548** terrain region files and their matching POI/entity files: **10,844 files, 23.09 GiB** in total.
- Verified that no terrain, POI, or entity region files remain outside the mask.
- Kept all MTR route, station, platform, depot, siding, and lift records. Four isolated rail records outside the boundary remain as metadata; see the [coordinate plan](./world-trim-preview-2026-10-22.md).
- Disabled the old oversized Chunky task by renaming its task file to `config/chunky/tasks/minecraft/overworld.properties.disabled`.

The removed files have matching size and timestamp copies under `<EXTERNAL_DRIVE>/backup\Minecraft-Fabric-1.21.1-lod-2026-10-22`, recorded by `TRIM-AFFECTED-FILES-VERIFIED.txt`. The **full-world copy in that folder remains incomplete**; do not treat it as a complete snapshot. The removed files themselves are recoverable.

## Smoke check

The dedicated server started with the reduced world at 04:29 BST, reached `Done`, listened on port 25566, and answered `list`. At 04:32, Spark reported 20 TPS and a 0.7 ms 95th-percentile tick time while no player was online. VSS serving, VSS backfill, and automatic DH generation/sync were off. The known DH–Chunky startup integration error still appeared once; the server continued to ready state.

The client shader is disabled for the next client launch and the server view distance is 16 chunks. These changes target the separate stutter reported before the trim. Loading retained legacy chunks may still log missing block IDs, so in-game smoothness needs a player test.

## Recovery

Cleanly stop the server, then run `python maintenance/apply-world-trim.py --restore` from the server root. This copies the removed files back from the verified affected-file backup and restores the saved Chunky task. Allow time to copy roughly 23 GiB back to C:. Restore before exploring outside the trimmed area; newly generated files at the same positions would need separate review.

Exact-coordinate preview, decision and coverage artifacts remain available only in the private evidence archive.

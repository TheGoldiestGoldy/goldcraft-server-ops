# Host memory pressure incident — 20 November 2026

**Status:** systemd-oomd action confirmed; root cause and application-level attribution not isolated.

## Confirmed host event

At 14:24:39 UTC, systemd-oomd marked the PollyMC application scope for termination. Its journal recorded:

- Memory used: 32,621,010,944 / 33,558,482,944 bytes (**97.21%**, approximately 30.38 / 31.25 GiB).
- Swap used: 30,204,407,808 / 33,557,573,632 bytes (**90.01%**, approximately 28.13 / 31.25 GiB).
- The scope then reported **233 processes killed**.

This confirms a host memory-pressure action against the PollyMC scope. It does not prove that all 233 processes were Minecraft processes or identify which application caused the pressure. The recorded action was systemd-oomd; it is not evidence of a kernel OOM-killer event.

## Temporary JVM experiment and rollback

After the event, server and client JVM settings were temporarily changed from a 10 GiB ZGC soft maximum / 300-second uncommit delay to 8 GiB / 60 seconds. Maximum heap values were not changed.

By 15:10 UTC, the persistent configuration files had been restored to 10 GiB / 300 seconds. A read-only check at 04:02 UTC on 21 November confirmed that both live Java processes again used 10 GiB / 300 seconds. The temporary change was not retained, and no controlled before/after test established a memory, TPS, MSPT or FPS improvement.

No server view-distance or simulation-distance change was part of this JVM experiment; the observed server values remained 8 / 5 chunks.

## Temporary memory samples

A temporary one-minute sampler recorded 16 rows from 14:52:30 through 15:09:34 UTC. The raw CSV remains private; only aggregate values are recorded here.

| Metric | Observed sample result |
|---|---:|
| Minimum MemAvailable | 875.3 MiB |
| Maximum MemTotal minus MemAvailable | 31,128.3 MiB |
| Maximum swap used | 11,992.2 MiB |
| Maximum client RSS sample | 21,965.7 MiB |
| Maximum server RSS sample | 9,069.9 MiB |
| Maximum whole-GPU VRAM used | 3,205 MiB |

Limitations:

- The client process was not detected in three of the 16 samples; zero in those rows means “not detected”, not zero memory use.
- Every PSS field in the CSV was zero. No PSS conclusion can be drawn.
- The sampler's host-memory field was calculated as MemTotal minus MemAvailable. That is a host-level estimate, not a strict process-memory total.
- GPU VRAM is whole-device usage, not attributable to Minecraft alone.
- The sample window began after the systemd-oomd event and cannot reconstruct the exact memory composition at the moment of the kill.
- No player count, TPS, MSPT, FPS, Spark profile or controlled gameplay benchmark was captured.

At 04:02 UTC on 21 November, a separate point-in-time check found approximately 2.88 GiB MemAvailable and 12.21 GiB swap used while both Java processes were present. Server RSS was approximately 10.46 GiB and client RSS approximately 11.33 GiB. Memory PSI avg10/avg60/avg300 were 0.00 at that instant. This is one snapshot, not evidence of sustained stability.

## Related automation status

The user-level server boot-start unit was enabled. Its 20 November run requested a start through the dashboard bridge and confirmed that the server accepted connections between 15:27:42 and 15:28:10 UTC. This is one successful execution, not a complete reboot or failure-recovery test.

The separate root-owned daily 07:00 OS update timer was **not installed** as of 04:02 UTC on 21 November; systemd reported the unit as not found. The host-side updater draft was not installed or end-to-end tested. Daily OS updates and automatic post-update reboot/restart must not be described as active.

The temporary memory sampler timer is disabled.

## Conclusions

1. Host memory pressure and a systemd-oomd process-scope kill are confirmed.
2. The process mix responsible for the pressure is not isolated.
3. The temporary 8 GiB / 60-second JVM setting is not a proven fix and was reverted.
4. The temporary sampler is not suitable as a PSS source until its all-zero PSS output and field semantics are corrected.
5. No gameplay-performance or player-capacity claim follows from these measurements.

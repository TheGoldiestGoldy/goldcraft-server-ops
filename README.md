# Goldcraft Server Operations

Live technical baseline, mod inventories, configurations, automation and evidence for a Minecraft Fabric 1.21.1 community server.

## Start here

- Live server status and client downloads are shared through the private community channel; the endpoint is intentionally omitted from this public repository.
- [Joining and client setup](docs/joining.md)
- [Current server state](docs/current-state.md)
- [What worked and what failed](docs/findings.md)
- [Client mod inventory](inventory/client-mods.md)
- [Server mod inventory](inventory/server-mods.md)
- [Resource packs, shader and performance profiles](inventory/client-assets.md)

## Current baseline

| Component | Confirmed value |
|---|---|
| CPU | Intel Core i7-10700F, 8 cores / 16 threads |
| Motherboard | Gigabyte Z490M |
| RAM | 32 GB DDR4-2666 |
| GPU | RTX 3060 Ti 8 GB |
| OS | CachyOS with GNOME |
| Minecraft | 1.21.1 |
| Loader | Fabric |
| Java | Temurin 21 |
| Server mods | 82 JAR files: 81 parseable metadata records, 1 malformed metadata JAR; 1 separate disabled file |
| Client mods | 100 detected; 100/100 Fabric metadata records parsed |
| Client assets | 14 resource-pack entries (12 active), 2 shader packs |
| Heap / GC | 4–12 GiB, 10 GiB soft maximum, Generational ZGC |
| View / simulation distance | 8 / 5 chunks |
| Capacity objective | 15 simultaneous players, not yet load-tested |

## Available generated client profiles

| Profile | Intended hardware | Initial settings |
|---|---|---|
| Amethyst + Podium | Modern Android phone | 3 GB heap, 5/4 render/simulation, shader off by default, 71 mods |
| Basic 8 GB laptop | Older Intel i5, integrated or weak GPU, 8 GB RAM | 3 GB heap, 6/4 distance, shader off by default, 70 mods |
| 16 GB / GTX 1060 class | i5/i7, 16 GB RAM, GTX 1060-class or 4–6 GB VRAM GPU | 6 GB heap, 8/5 distance, MakeUp Ultra Fast enabled, 70 mods |

The generator's 35–45 FPS figure is a starting target, not a measured benchmark. Its validation checks Fabric dependency resolution, not hardware performance. The full desktop setup remains the operator's active client, not a generated profile archive. See [the profile inventory](inventory/client-profiles.md).

## Repository map

| Path | What it contains |
|---|---|
| [docs/current-state.md](docs/current-state.md) | Hardware, runtime, storage, DH and VSS baseline |
| [docs/findings.md](docs/findings.md) | Confirmed successes, failures, tentative causes and unknowns |
| [docs/log-evidence.md](docs/log-evidence.md) | Aggregated evidence from archived logs and crash reports |
| [docs/change-timeline.md](docs/change-timeline.md) | Dated configuration and maintenance history |
| [docs/operations.md](docs/operations.md) | Start, stop, LOD, pregeneration and recovery runbook |
| [docs/security.md](docs/security.md) | Current exposure risks and hardening requirements |
| [docs/issues](docs/issues) | Host memory pressure, server process exit, LOD download-loop and rubberbanding investigations |
| [docs/experiments](docs/experiments) | Performance, LOD and world-maintenance results |
| [inventory](inventory) | Exact mod names, versions, sizes and SHA-256 hashes |
| [configs](configs) | Sanitized performance-relevant configuration snapshots |
| [automation](automation) | Server launcher, dashboard bridge and daily inventory/profile jobs |
| [tools](tools) | Snapshot, report, backup verification and maintenance utilities |

## Current conclusions
- The current Distant Horizons server config sets `generatorPlan` to `DISABLED`; its own comment says no distant terrain will be generated. This is an on-disk setting, not a live runtime test.
- The latest VSS config enables `service` and LOD storage on disk while generation/backfill are disabled; the server was absent at 04:33 UTC, so live serving is unverified.

- The client inventory refreshed successfully at 00:02 UTC on 22 November: 100 mods, 14 resource-pack entries (12 active), 2 shader packs and three checksum-verified profile archives.
- At 04:05 UTC on 22 November, no Java server process was present. The latest server log ends with a console-input I/O exception; the reason for the process disappearance is unresolved ([investigation](docs/issues/server-process-exit-2026-11-21.md)).
- The active `arch-update.timer` invokes `arch-update --check` only. It checks and notifies about updates; it does not install them. The separate 07:00 OS-upgrade timer remains uninstalled.

### Confirmed working

- Fabric 1.21.1 starts reproducibly with the intended world and mod set.
- The Linux launcher prevents duplicate processes and uses Java 21 with Generational ZGC.
- A reviewed world trim preserved MTR data and passed a post-maintenance smoke test.
- The Modern Furniture dedicated-server patch passed placement, save and restart validation.
- Daily client inventories, profile archive generation, dependency validation, checksums and resumable downloads are automated; FPS targets are not hardware benchmarks.
- Existing VSS/Voxy-derived LOD data remains preserved for controlled future testing.

### Confirmed problems or unfinished tests

- Stable capacity at 15 simultaneous players is unproven.
- Automatic DH/VSS transfers previously created large queues and poor client playability.
- Oversized pregeneration and high server view distance caused stalls and watchdog failures.
- Rubberbanding with distant players still needs a controlled Spark comparison.
- A 20 November host-memory incident triggered systemd-oomd to kill 233 processes in the PollyMC scope; cause and performance impact remain unisolated ([incident report](docs/issues/memory-pressure-2026-11-20.md)).
- The daily 07:00 OS update timer is not installed. The server boot-start helper has three successful observed invocations (20, 21 and 23 November), but it is a one-shot start helper, not a supervisor; update-and-reboot automation is not active ([operations runbook](docs/operations.md)).
- Connection details are distributed through the community channel; defensive settings remain private.

## Evidence standard

- **Confirmed:** directly observed in a file, hash, log, process or repeatable test.
- **Tentative:** supported by evidence but not isolated experimentally.
- **Unknown:** not measured.
- **Revisit:** an intentionally open decision.

Personal identifiers, credentials, raw logs and exact player/build coordinates are redacted. Operational settings, code, sanitized configs and aggregate measurements remain available because they are the useful part of this repository.

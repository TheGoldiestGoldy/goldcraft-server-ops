# Goldcraft Server Operations

Live technical baseline, mod inventories, configurations, automation and evidence for a Minecraft Fabric 1.21.1 community server.

## Start here

- [Live server status and client downloads](https://goldcraft-host.tail26d0f0.ts.net/)
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
| Server mods | 85 active, 1 disabled |
| Client mods | 102 detected |
| Heap / GC | 4–12 GiB, 10 GiB soft maximum, Generational ZGC |
| View / simulation distance | 8 / 5 chunks |
| Capacity objective | 15 simultaneous players, not yet load-tested |

## Available client profiles

| Profile | Intended hardware | Initial settings |
|---|---|---|
| Amethyst + Podium | Modern Android phone | 3 GB heap, 5/4 render/simulation, shader disabled |
| Basic laptop | Older Intel i5, integrated or weak GPU, 8 GB RAM | 3 GB heap, 6/4 distance, shader disabled |
| Balanced PC | i5/i7, 16 GB RAM, GTX 1060-class or 4–6 GB VRAM GPU | 6 GB heap, 8/5 distance, lightweight shader enabled |
| Full desktop | Current operator client | Complete mod/resource-pack setup and Distant Horizons |

Download the current archives from the [player dashboard](https://goldcraft-host.tail26d0f0.ts.net/). They are rebuilt from the active client installation every 24 hours.

## Repository map

| Path | What it contains |
|---|---|
| [docs/current-state.md](docs/current-state.md) | Hardware, runtime, storage, DH and VSS baseline |
| [docs/findings.md](docs/findings.md) | Confirmed successes, failures, tentative causes and unknowns |
| [docs/log-evidence.md](docs/log-evidence.md) | Aggregated evidence from archived logs and crash reports |
| [docs/change-timeline.md](docs/change-timeline.md) | Dated configuration and maintenance history |
| [docs/operations.md](docs/operations.md) | Start, stop, LOD, pregeneration and recovery runbook |
| [docs/security.md](docs/security.md) | Current exposure risks and hardening requirements |
| [docs/issues](docs/issues) | LOD download-loop and rubberbanding investigations |
| [docs/experiments](docs/experiments) | Performance, LOD and world-maintenance results |
| [inventory](inventory) | Exact mod names, versions, sizes and SHA-256 hashes |
| [configs](configs) | Sanitized performance-relevant configuration snapshots |
| [automation](automation) | Server launcher, dashboard bridge and daily inventory/profile jobs |
| [tools](tools) | Snapshot, report, backup verification and maintenance utilities |

## Current conclusions

### Confirmed working

- Fabric 1.21.1 starts reproducibly with the intended world and mod set.
- The Linux launcher prevents duplicate processes and uses Java 21 with Generational ZGC.
- A reviewed world trim preserved MTR data and passed a post-maintenance smoke test.
- The Modern Furniture dedicated-server patch passed placement, save and restart validation.
- Daily client inventories, performance profiles, checksums and resumable downloads are automated.
- Existing VSS/Voxy-derived LOD data remains preserved for controlled future testing.

### Confirmed problems or unfinished tests

- Stable capacity at 15 simultaneous players is unproven.
- Automatic DH/VSS transfers previously created large queues and poor client playability.
- Oversized pregeneration and high server view distance caused stalls and watchdog failures.
- Rubberbanding with distant players still needs a controlled Spark comparison.
- Connection details are distributed through the community channel; defensive settings remain private.

## Evidence standard

- **Confirmed:** directly observed in a file, hash, log, process or repeatable test.
- **Tentative:** supported by evidence but not isolated experimentally.
- **Unknown:** not measured.
- **Revisit:** an intentionally open decision.

Personal identifiers, credentials, raw logs and exact player/build coordinates are redacted. Operational settings, code, sanitized configs and aggregate measurements remain available because they are the useful part of this repository.

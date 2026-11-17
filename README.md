# Goldcraft Fabric 1.21.1

Public compatibility, troubleshooting and client-setup evidence for a community Minecraft Fabric 1.21.1 server.

This repository helps players answer four questions:

1. Which mods and versions are currently expected?
2. Which resource packs, shaders and client profiles are available?
3. Which recurring performance problems have been confirmed?
4. Which fixes worked, failed or still require controlled testing?

## Public baseline

| Component | Published value |
|---|---|
| Minecraft | 1.21.1 |
| Loader | Fabric |
| Server mod inventory | Exact names, versions and file hashes |
| Client mod inventory | Exact names, versions and file hashes |
| Client profiles | Android/Amethyst, basic laptop and balanced PC |
| Capacity objective | Up to 15 simultaneous players, not yet proven |

Private infrastructure details, server addresses, control endpoints, account identifiers, raw logs, player handles, UUIDs, IP addresses, world seeds and exact world-coordinate datasets are deliberately excluded.

## Repository map

| Path | Purpose |
|---|---|
| [inventory/client-mods.md](inventory/client-mods.md) | Client mod names and versions |
| [inventory/server-mods.md](inventory/server-mods.md) | Server mod names and versions |
| [inventory/client-assets.md](inventory/client-assets.md) | Active resource packs, shader and tuned profile checksums |
| [docs/findings.md](docs/findings.md) | Sanitized record of what worked, failed or remains unknown |
| [docs/issues](docs/issues) | Reproducible records for recurring symptoms |
| [docs/experiments](docs/experiments) | Aggregate experiment findings without exact coordinates |
| [docs/audits](docs/audits) | Compatibility audits based on static evidence |
| [SECURITY.md](SECURITY.md) | Security and privacy reporting policy |

## Evidence labels

- **Confirmed**: directly observed in a file, hash, log, process or repeatable test.
- **Tentative**: plausible interpretation supported by incomplete evidence.
- **Unknown**: not measured or not recoverable from available data.
- **Revisit**: a decision intentionally left open.

## Important limitations

- A listed mod or asset is evidence of the tested installation, not permission to redistribute its binary.
- SHA-256 values verify exact files but do not contain the files themselves.
- Performance figures are historical observations, not FPS guarantees.
- Maximum stable capacity has not yet been load-tested.
- Client configuration still depends on resolution, thermals, drivers and the loaded area.

## Privacy boundary

The public repository contains no intended player-level records. Raw logs and crash reports remain private because they may contain usernames, UUIDs, IP addresses, chat or machine paths. Generated machine snapshots and exact-coordinate maps also remain private.

Automated checks reject common identifiers, secret assignments, raw logs, world data, private snapshots and exact-coordinate artifacts. Every update must still receive a manual diff review.

## Contributing

Use [CONTRIBUTING.md](CONTRIBUTING.md) for evidence standards. Do not place a real server address, player identifier, IP address, UUID, access token, world seed, private message or raw log in an issue.

If you find private information in the repository, follow [SECURITY.md](SECURITY.md) and report the filename without repeating the private value.

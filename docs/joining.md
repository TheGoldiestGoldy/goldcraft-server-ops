# Joining Goldcraft

## 1. Check server status

Open the [Goldcraft player dashboard](https://thegoldiestgoldy.github.io/goldcraft-server-ops/). It shows whether the server PC and Minecraft server are online.

## 2. Choose a client package

Use the dashboard download matching your device:

| Device | Package |
|---|---|
| Android using Amethyst | Amethyst + Podium profile |
| 8 GB laptop with integrated/weak graphics | Basic laptop profile |
| 16 GB laptop or GTX 1060-class PC | Balanced PC profile |
| Strong desktop matching the main client | Full client files |

The dashboard also provides separate current archives for mods, active resource packs and shader packs.

## 3. Required runtime

- Minecraft 1.21.1
- Fabric Loader
- Java 21
- Enough free storage for the selected profile

Extract each archive into the matching Minecraft instance folders. Do not mix the Amethyst/Podium renderer files into a desktop Sodium/Iris instance.

## 4. Verify the installation

Before joining:

1. Launch the instance once.
2. Confirm Fabric reaches the main menu without dependency errors.
3. Compare the installed mod versions with [the client inventory](../inventory/client-mods.md).
4. Keep Distant Horizons bulk synchronization disabled during first join.
5. Start without a shader on mobile or weak laptops; enable the included lightweight shader only after stable gameplay is confirmed.

## 5. Get the connection address

The address is intentionally not stored in Git history. Request the current address from the server operator or the community channel where the server is announced.

## Troubleshooting

- Large or repeating LOD queue: [LOD download-loop record](issues/lod-download-loop.md)
- Rubberbanding when players separate: [rubberbanding record](issues/rubberbanding.md)
- Exact installed assets and profile hashes: [client assets](../inventory/client-assets.md)
- Complete client/server mod comparison: [client mods](../inventory/client-mods.md) and [server mods](../inventory/server-mods.md)

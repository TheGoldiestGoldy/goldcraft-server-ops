# World Tram Pack — Phase 1 compatibility audit

Audit date: 2026-10-24. Read-only inspection; no client, server, mod, world, or original archive was changed.

## Compatibility matrix

| Component | Evidence | Status | Implication |
|---|---|---|---|
| Minecraft/Fabric | Prism instance `1.21.1`; Fabric Loader `0.19.5` | Working | Correct target instance located at `%USERPROFILE%\AppData\Roaming\PrismLauncher\instances\1.21.1\minecraft` |
| MTR | `MTR-fabric-4.1.0-beta.2+1.21.1.jar` | Working | Installed implementation directly loads `assets/mtr/mtr_custom_resources.json` |
| MTR native OBJ | Installed `VehicleModel`/`ObjModelLoader` classes | Working in principle | OBJ and MTL are supported natively; NTE is not required for this path |
| WTP vehicle schema | 63 unique `vehicles`; keys align with MTR 4 schema; 98/98 JSON files parse | Partially working | MTR 4 can read the pack’s modern resource definition; individual broken references remain |
| WTP runtime load | Historical reload included `file/WTP 2.0.0 alpha-5.zip`; no custom-resource parse failure found | Partially verified | The pack reached MTR’s resource reload path, but this is not proof every tram renders or operates correctly |
| OBJ/MTL linkage | 108 OBJ + 108 MTL; 108/108 `mtllib` targets present | Working statically | Geometry/material file linkage is present |
| Model references | 1 invalid target: `mtr:bogies/astra/wozek.objj` | Broken | Affected vehicle is `variolf_met`; it needs permissioned repair |
| Texture references | 39 distinct direct `textureResource` targets missing | Broken/partial | Many are fallback textures; impact must be confirmed per model after authorization |
| MTL texture maps | 6 distinct `map_*` targets missing | Broken/partial | Missing maps can produce invisible/missing material regions |
| Sounds | 50 declared events, 37 OGGs; 16 event targets missing; BVE `lion` config absent | Broken/partial | Pesa motor warnings were observed in the historical log; some vehicle sound bases cannot fully resolve |
| Pack metadata | WTP declares `pack_format: 15`; target is 34 | Outdated/unverified | Do not assume metadata-only editing fixes MTR compatibility |
| Joban/NTE | No Joban or NTE mod/component found in active client | Missing | No NTE-dependent migration path is available or needed |
| Iris/shaders | Iris 1.8.14-beta.1 + Sodium 0.8.13; Bliss configured but shaders disabled | Unverified | Shader-on testing is still pending; current errors cannot be attributed to shaders |
| Rendering integrations | Distant Horizons 3.3.3, Voxy server-side, EntityCulling, ImmediatelyFast, PackForge | Present | Must be tested only in an isolated client after a permitted prototype exists |

## Existing client state

Current enabled resource-pack order from `options.txt`:

`seasons:seasonal_lush_caves`, `vanilla`, `programmer_art`, `high_contrast`, `moonlight:merged_pack`, `fabric`, `DEWON-N700__Kamome-4.0-MTR4.zip`, `DEWON-Shinkansen-Infra-1.9.zip`, `Henoke Suspended Monorail Pack 1.0.zip`, `HarrysLib-1.1.zip`, `Realism_Unified_v1.0_1.21.1.zip`.

WTP is present in the client resource-pack directory but is not currently enabled. The source archive and client copy have matching SHA-256:

`765C543B1F2D4B2A4E48DF34BF1598C045DA2F5358F3D46C3929A04240439CAE`

## Authorization gate

The archive’s `LICENSE.md` and `CREDITS.md` state that cross-version porting/conversion of the author’s models requires explicit written permission, and third-party models require permission from their respective authors. No such authorization is present in the workspace. The pack must therefore remain unchanged and no prototype or migration output containing its assets can be created yet.

## Next action

Provide written authorization covering the specific WTP assets to adapt to Minecraft 1.21.1/MTR 4, including any third-party models, or identify an independently licensed representative tram. Once that gate is satisfied, Phase 2 can build an isolated prototype without touching the existing installation.

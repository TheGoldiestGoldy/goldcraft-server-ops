# Decisions to revisit

| Decision | Current state | Evidence needed |
|---|---|---|
| Support 15 simultaneous players | Goal, not validated | 5/10/15-player MSPT and network tests |
| Keep Distant Horizons server-side | Installed with sync off | One-system-at-a-time LOD trial |
| VSS serving policy | On-disk service enabled; generation off; LOD store enabled; runtime unverified | Decide whether to disable before restart; controlled opt-in transfer test without play disruption |
| Increase view distance above 8 | No | Busy-city and separated-player Spark profiles |
| Resume pregeneration | No | Reviewed bounds, backup, disk forecast and short trial |
| Replace patched Modern Furniture JAR | Not yet | Upstream release proving dedicated-server fix |
| Enable BlueMap high-resolution rendering | No | Disk budget and render-time estimate |
| Public access hardening | Defensive details kept private | Complete authentication and network review before changing exposure |

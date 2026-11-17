# Reviewed city and railway world trim

**Status: applied; aggregate public summary.**

The proposal retained the developed city area, the two long station routes, surrounding terrain buffers and all saved transit records. Isolated distant terrain and unrelated generated areas were selected for removal.

## Review method

- Count saved terrain, entity and point-of-interest region files.
- Compare the retained mask with saved station, platform, depot, siding, lift and rail metadata.
- Preserve whole edge regions rather than cutting individual chunks.
- Verify a recovery copy of every affected file before applying changes.
- Stop the server during the operation.
- Disable the oversized pregeneration task so removed terrain would not immediately regenerate.

## Limits

- Trimming does not repair missing legacy block identifiers inside retained chunks.
- Client and server LOD caches may still contain derived data from removed areas.
- Traveling beyond the reviewed play area can generate new terrain.
- A verified affected-file recovery copy is not the same as a complete world backup.

Exact boundaries, rail identifiers, player locations, maps and per-region decisions remain in the private evidence archive.

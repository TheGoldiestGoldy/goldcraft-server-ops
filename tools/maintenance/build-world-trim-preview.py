#!/usr/bin/env python3
"""Build a read-only, operator-defined Minecraft world-trim preview.

The script never changes world files. All boundaries are supplied explicitly at
runtime so public source code does not disclose a live world's locations.
Generated CSV/JSON reports contain coordinates and must remain private.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
from collections import Counter
from pathlib import Path

import msgpack

REGION_BLOCKS = 512


def msgpack_rows(mtr_root: Path, kind: str):
    directory = mtr_root / kind
    if not directory.is_dir():
        return
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        try:
            row = next(iter(msgpack.Unpacker(io.BytesIO(path.read_bytes()), raw=False)))
        except (StopIteration, ValueError, msgpack.ExtraData):
            continue
        if isinstance(row, dict):
            yield path, row


def rail_points(mtr_root: Path):
    rails = []
    for path, rail in msgpack_rows(mtr_root, "rails"):
        if "position1" in rail and "position2" in rail:
            rails.append((path, rail["position1"], rail["position2"]))
    return rails


def corridor_bands(rails, minimum_region_z: int, maximum_region_z: int, buffer_blocks: int):
    samples: dict[int, list[float]] = {}
    for _, start, end in rails:
        distance = math.hypot(start["x"] - end["x"], start["z"] - end["z"])
        steps = max(1, math.ceil(distance / 128))
        for index in range(steps + 1):
            fraction = index / steps
            x = start["x"] + (end["x"] - start["x"]) * fraction
            z = start["z"] + (end["z"] - start["z"]) * fraction
            region_z = math.floor(z / REGION_BLOCKS)
            if minimum_region_z <= region_z <= maximum_region_z:
                samples.setdefault(region_z, []).append(x)

    if not samples:
        raise RuntimeError("No railway samples fell inside the requested corridor")

    occupied = sorted(samples)
    bounds = {}
    for region_z in range(minimum_region_z, maximum_region_z + 1):
        nearest = min(occupied, key=lambda value: abs(value - region_z))
        xs = samples.get(region_z, samples[nearest])
        bounds[region_z] = (
            math.floor((min(xs) - buffer_blocks) / REGION_BLOCKS),
            math.floor((max(xs) + buffer_blocks) / REGION_BLOCKS),
        )
    return bounds


def decision(
    region_x: int,
    region_z: int,
    city_region_bounds: tuple[int, int, int, int],
    corridor,
):
    city_x_min, city_x_max, city_z_min, city_z_max = city_region_bounds
    if city_x_min <= region_x <= city_x_max and city_z_min <= region_z <= city_z_max:
        return "keep", "city boundary"
    if region_z in corridor:
        left, right = corridor[region_z]
        if left <= region_x <= right:
            return "keep", "rail corridor"
    return "remove", "outside boundary"


def region_rows(world: Path, city_region_bounds, corridor):
    for path in sorted((world / "region").glob("r.*.*.mca")):
        match = re.fullmatch(r"r\.(-?\d+)\.(-?\d+)\.mca", path.name)
        if not match:
            continue
        region_x, region_z = map(int, match.groups())
        with path.open("rb") as handle:
            header = handle.read(4096)
        if not header:
            chunks = 0
        elif len(header) != 4096:
            raise RuntimeError(f"Truncated MCA header: {path}")
        else:
            chunks = sum(
                header[index : index + 4] != b"\0\0\0\0"
                for index in range(0, 4096, 4)
            )
        keep, reason = decision(region_x, region_z, city_region_bounds, corridor)
        sidecar_bytes = {}
        for kind in ("poi", "entities"):
            sidecar = world / kind / path.name
            sidecar_bytes[kind] = sidecar.stat().st_size if sidecar.exists() else 0
        yield {
            "region_x": region_x,
            "region_z": region_z,
            "block_x_min": region_x * REGION_BLOCKS,
            "block_x_max": region_x * REGION_BLOCKS + REGION_BLOCKS - 1,
            "block_z_min": region_z * REGION_BLOCKS,
            "block_z_max": region_z * REGION_BLOCKS + REGION_BLOCKS - 1,
            "chunk_slots": chunks,
            "region_bytes": path.stat().st_size,
            "poi_bytes": sidecar_bytes["poi"],
            "entity_bytes": sidecar_bytes["entities"],
            "decision": keep,
            "reason": reason,
        }


def object_positions(value):
    if isinstance(value, dict):
        if isinstance(value.get("x"), int) and isinstance(value.get("z"), int):
            yield value["x"], value["z"]
        for child in value.values():
            yield from object_positions(child)
    elif isinstance(value, list):
        for child in value:
            yield from object_positions(child)


def object_check(mtr_root: Path, city_region_bounds, corridor):
    results = {}
    for kind in ("stations", "platforms", "sidings", "depots", "lifts"):
        total = outside = 0
        for _, row in msgpack_rows(mtr_root, kind):
            for x, z in object_positions(row):
                total += 1
                result, _ = decision(
                    math.floor(x / REGION_BLOCKS),
                    math.floor(z / REGION_BLOCKS),
                    city_region_bounds,
                    corridor,
                )
                outside += result == "remove"
        results[kind] = {"positions": total, "outside": outside}
    return results


def block_to_region_bounds(args):
    return (
        math.floor(args.city_x_min / REGION_BLOCKS),
        math.floor(args.city_x_max / REGION_BLOCKS),
        math.floor(args.city_z_min / REGION_BLOCKS),
        math.floor(args.city_z_max / REGION_BLOCKS),
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", type=Path, required=True, help="Path to the world directory")
    parser.add_argument("--output", type=Path, required=True, help="Private report directory")
    parser.add_argument("--prefix", default="world-trim-preview")
    parser.add_argument("--city-x-min", type=int, required=True)
    parser.add_argument("--city-x-max", type=int, required=True)
    parser.add_argument("--city-z-min", type=int, required=True)
    parser.add_argument("--city-z-max", type=int, required=True)
    parser.add_argument("--corridor-z-min-region", type=int, required=True)
    parser.add_argument("--corridor-z-max-region", type=int, required=True)
    parser.add_argument("--rail-buffer-blocks", type=int, default=1024)
    return parser.parse_args()


def main():
    args = parse_args()
    world = args.world.expanduser().resolve(strict=True)
    mtr_root = world / "mtr" / "minecraft" / "overworld"
    if not (world / "region").is_dir():
        raise RuntimeError("World region directory not found")
    if args.city_x_min > args.city_x_max or args.city_z_min > args.city_z_max:
        raise RuntimeError("City minimum bounds must not exceed maximum bounds")
    if args.corridor_z_min_region > args.corridor_z_max_region:
        raise RuntimeError("Corridor minimum must not exceed maximum")

    city_region_bounds = block_to_region_bounds(args)
    corridor = corridor_bands(
        rail_points(mtr_root),
        args.corridor_z_min_region,
        args.corridor_z_max_region,
        args.rail_buffer_blocks,
    )
    rows = list(region_rows(world, city_region_bounds, corridor))
    if not rows:
        raise RuntimeError("No region files found")

    object_results = object_check(mtr_root, city_region_bounds, corridor)
    if any(value["outside"] for value in object_results.values()):
        raise RuntimeError("Requested boundary excludes one or more saved MTR objects")

    counts = {"keep": Counter(), "remove": Counter()}
    for row in rows:
        count = counts[row["decision"]]
        count["regions"] += 1
        count["chunks"] += row["chunk_slots"]
        for key in ("region_bytes", "poi_bytes", "entity_bytes"):
            count[key] += row[key]

    args.output.mkdir(parents=True, exist_ok=True)
    csv_path = args.output / f"{args.prefix}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    mask = {
        "warning": "Private coordinate-bearing output; do not publish.",
        "coordinate_unit": "Minecraft block X/Z",
        "region_size_blocks": REGION_BLOCKS,
        "city_block_bounds": {
            "x_min": args.city_x_min,
            "x_max": args.city_x_max,
            "z_min": args.city_z_min,
            "z_max": args.city_z_max,
        },
        "rail_x_buffer_blocks": args.rail_buffer_blocks,
        "corridor_region_x_bounds_by_region_z": {
            str(z): list(bounds) for z, bounds in sorted(corridor.items())
        },
        "kept_existing_regions": [
            [row["region_x"], row["region_z"]]
            for row in rows
            if row["decision"] == "keep"
        ],
        "mtr_object_check": object_results,
    }
    mask_path = args.output / f"{args.prefix}-mask.json"
    mask_path.write_text(json.dumps(mask, indent=2) + "\n", encoding="utf-8")

    print(f"Preview only; no world files changed")
    print(f"Keep: {counts['keep']['regions']:,} regions / {counts['keep']['chunks']:,} chunks")
    print(f"Remove: {counts['remove']['regions']:,} regions / {counts['remove']['chunks']:,} chunks")
    print(f"Private reports: {csv_path} and {mask_path}")


if __name__ == "__main__":
    main()

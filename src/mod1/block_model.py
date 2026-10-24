"""Build a preliminary categorical block model from positioned observations."""

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from src.mod1.desurvey import desurvey
from src.mod1.loader import IntervalData, RawData
from src.mod1.positioning import PositionedRow, position_intervals

GRID_ORIGIN_M = (242225.0, 8196250.0, 2990.0)
BLOCK_SIZE_M = (50.0, 50.0, 10.0)
GRID_SHAPE = (15, 14, 55)
BLOCK_MODEL_COLUMNS = (
    "i",
    "j",
    "k",
    "x_min",
    "y_min",
    "z_min",
    "x_max",
    "y_max",
    "z_max",
    "x_center",
    "y_center",
    "z_center",
    "lith_code",
    "lith_status",
    "lith_support_count",
    "lith_support_codes",
    "assay_composite_support_count",
)


class BlockRecord(TypedDict):
    """One grid cell with observed categorical and assay support."""

    i: int
    j: int
    k: int
    x_min: float
    y_min: float
    z_min: float
    x_max: float
    y_max: float
    z_max: float
    x_center: float
    y_center: float
    z_center: float
    lith_code: str
    lith_status: str
    lith_support_count: int
    lith_support_codes: str
    assay_composite_support_count: int


def _coordinate(row: PositionedRow, field: str, *, table: str, row_number: int) -> float:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(
            f"{table} row {row_number}: {field} must have a numeric value."
        )
    try:
        coordinate = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{table} row {row_number}: {field} must be a parseable number."
        ) from error
    if not math.isfinite(coordinate):
        raise ValueError(f"{table} row {row_number}: {field} must be finite.")
    return coordinate


def _cell_index(
    row: PositionedRow,
    *,
    table: str,
    row_number: int,
    origin_m: tuple[float, float, float],
    block_size_m: tuple[float, float, float],
    shape: tuple[int, int, int],
) -> tuple[int, int, int]:
    x, y, z = (
        _coordinate(row, field, table=table, row_number=row_number)
        for field in ("x_mid", "y_mid", "z_mid")
    )
    indices = (
        math.floor((x - origin_m[0]) / block_size_m[0]),
        math.floor((y - origin_m[1]) / block_size_m[1]),
        math.floor((z - origin_m[2]) / block_size_m[2]),
    )
    if any(
        index < 0 or index >= count
        for index, count in zip(indices, shape)
    ):
        raise ValueError(
            f"{table} row {row_number}: midpoint maps outside grid at index "
            f"{indices}; grid shape is {shape}."
        )
    return indices


def build_block_model(
    positioned_lithology: list[PositionedRow],
    positioned_composites: list[PositionedRow],
    *,
    origin_m: tuple[float, float, float] = GRID_ORIGIN_M,
    block_size_m: tuple[float, float, float] = BLOCK_SIZE_M,
    shape: tuple[int, int, int] = GRID_SHAPE,
) -> list[BlockRecord]:
    """Build a grid and assign only unanimous, non-empty observed lith codes.

    Lithology interval midpoints are the sole categorical support. Composite
    midpoints contribute only to the assay-support count.
    """
    if len(origin_m) != 3 or len(block_size_m) != 3 or len(shape) != 3:
        raise ValueError("Grid origin, block dimensions, and shape must have 3 axes.")
    if any(size <= 0 or not math.isfinite(size) for size in block_size_m):
        raise ValueError("Block dimensions must be positive and finite.")
    if any(type(count) is not int or count <= 0 for count in shape):
        raise ValueError("Grid dimensions must be positive integers.")
    if any(not math.isfinite(value) for value in origin_m):
        raise ValueError("Grid origin coordinates must be finite.")

    lith_support: dict[tuple[int, int, int], list[str | None]] = defaultdict(list)
    for row_number, row in enumerate(positioned_lithology, start=1):
        index = _cell_index(
            row,
            table="lithology",
            row_number=row_number,
            origin_m=origin_m,
            block_size_m=block_size_m,
            shape=shape,
        )
        code = row.get("lith_code")
        lith_support[index].append(
            code.strip() if isinstance(code, str) and code.strip() else None
        )

    assay_support: dict[tuple[int, int, int], int] = defaultdict(int)
    for row_number, row in enumerate(positioned_composites, start=1):
        index = _cell_index(
            row,
            table="composite",
            row_number=row_number,
            origin_m=origin_m,
            block_size_m=block_size_m,
            shape=shape,
        )
        assay_support[index] += 1

    blocks: list[BlockRecord] = []
    nx, ny, nz = shape
    dx, dy, dz = block_size_m
    ox, oy, oz = origin_m
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                index = (i, j, k)
                codes = lith_support.get(index, [])
                unique_codes = sorted({code for code in codes if code is not None})
                assigned = (
                    bool(codes)
                    and all(code is not None for code in codes)
                    and len(unique_codes) == 1
                )
                x_min, y_min, z_min = ox + i * dx, oy + j * dy, oz + k * dz
                blocks.append(
                    {
                        "i": i,
                        "j": j,
                        "k": k,
                        "x_min": x_min,
                        "y_min": y_min,
                        "z_min": z_min,
                        "x_max": x_min + dx,
                        "y_max": y_min + dy,
                        "z_max": z_min + dz,
                        "x_center": x_min + dx / 2,
                        "y_center": y_min + dy / 2,
                        "z_center": z_min + dz / 2,
                        "lith_code": unique_codes[0] if assigned else "",
                        "lith_status": "ASSIGNED" if assigned else "UNKNOWN/UNASSIGNED",
                        "lith_support_count": len(codes),
                        "lith_support_codes": "|".join(unique_codes),
                        "assay_composite_support_count": assay_support.get(index, 0),
                    }
                )
    return blocks


def build_preliminary_block_model(
    raw_data: RawData,
    positioned_composites: list[PositionedRow],
    *,
    origin_m: tuple[float, float, float] = GRID_ORIGIN_M,
    block_size_m: tuple[float, float, float] = BLOCK_SIZE_M,
    shape: tuple[int, int, int] = GRID_SHAPE,
) -> list[BlockRecord]:
    """Desurvey raw inputs, position lithology intervals, and build the grid."""
    trajectory = desurvey(raw_data["collar"], raw_data["survey"])
    interval_data: IntervalData = {
        "assay": raw_data["assay"],
        "lithology": raw_data["lithology"],
        "alteration": raw_data["alteration"],
        "density": raw_data["density"],
    }
    positioned_intervals = position_intervals(
        trajectory,
        interval_data,
    )
    return build_block_model(
        positioned_intervals["lithology"],
        positioned_composites,
        origin_m=origin_m,
        block_size_m=block_size_m,
        shape=shape,
    )


def write_block_model_csv(blocks: list[BlockRecord], output_path: Path) -> None:
    """Write the block model as a CSV with an explicit, stable column order."""
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=BLOCK_MODEL_COLUMNS)
        writer.writeheader()
        for block in blocks:
            writer.writerow(dict(block))

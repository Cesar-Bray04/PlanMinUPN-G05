"""Build a preliminary categorical block model from positioned observations."""

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from src.mod1.desurvey import desurvey
from src.mod1.loader import IntervalData, RawData
from src.mod1.positioning import PositionedRow, PositionedSegment, position_intervals

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
GEOLOGICAL_BLOCK_COLUMNS = (
    *BLOCK_MODEL_COLUMNS,
    "lith_support_length_m",
    "lith_support_interval_count",
    "lith_support_interval_ids",
    "lith_assignment_reason",
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


class GeologicalBlockRecord(BlockRecord):
    """A block with interval-intersection support and assignment provenance."""

    lith_support_length_m: float
    lith_support_interval_count: int
    lith_support_interval_ids: str
    lith_assignment_reason: str


class IntervalCoverage(TypedDict):
    """Downhole-length accounting for one observed lithology interval."""

    interval_id: str
    hole_id: str
    from_m: float
    to_m: float
    observed_length_m: float
    inside_length_m: float
    outside_length_m: float


class _CellSupport(TypedDict):
    codes: list[str | None]
    length: float
    intervals: list[str]


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


def _segment_grid_parts(
    segment: PositionedSegment,
    *,
    origin_m: tuple[float, float, float],
    block_size_m: tuple[float, float, float],
    shape: tuple[int, int, int],
) -> list[tuple[tuple[int, int, int] | None, float]]:
    md_start, md_end, start, end = segment
    if md_end <= md_start:
        raise ValueError("Positioned trajectory segments must have positive MD length.")
    delta = tuple(last - first for first, last in zip(start, end))
    if math.hypot(*delta) <= 1e-12:
        raise ValueError("Positioned trajectory segment has zero XYZ length.")

    parameters = {0.0, 1.0}
    for axis, (first, change, origin, size) in enumerate(
        zip(start, delta, origin_m, block_size_m)
    ):
        if change == 0:
            continue
        low, high = sorted((first, first + change))
        first_boundary = math.floor((low - origin) / size) + 1
        last_boundary = math.ceil((high - origin) / size) - 1
        for boundary_index in range(first_boundary, last_boundary + 1):
            boundary = origin + boundary_index * size
            parameter = (boundary - first) / change
            if 0.0 < parameter < 1.0:
                parameters.add(parameter)

    ordered = sorted(parameters)
    parts: list[tuple[tuple[int, int, int] | None, float]] = []
    grid_max = tuple(
        origin + count * size
        for origin, count, size in zip(origin_m, shape, block_size_m)
    )
    for first_t, last_t in zip(ordered, ordered[1:]):
        if last_t <= first_t:
            continue
        midpoint_t = (first_t + last_t) / 2.0
        midpoint = tuple(
            coordinate + midpoint_t * change
            for coordinate, change in zip(start, delta)
        )
        indices: list[int] = []
        for coordinate, origin, size, count, maximum in zip(
            midpoint, origin_m, block_size_m, shape, grid_max
        ):
            if math.isclose(coordinate, maximum, rel_tol=0.0, abs_tol=1e-10):
                index = count - 1
            else:
                index = math.floor((coordinate - origin) / size)
            indices.append(index)
        index_tuple = tuple(indices)
        cell = (
            index_tuple
            if all(0 <= value < count for value, count in zip(index_tuple, shape))
            else None
        )
        parts.append((cell, (md_end - md_start) * (last_t - first_t)))
    return parts


def _positioned_segment(
    value: object, *, row_number: int, segment_number: int
) -> PositionedSegment:
    if not isinstance(value, (tuple, list)) or len(value) != 4:
        raise ValueError(
            f"lithology row {row_number}: malformed trajectory segment "
            f"{segment_number}."
        )
    md_values: list[float] = []
    for field, raw in zip(("start MD", "end MD"), value[:2]):
        if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
            raise ValueError(
                f"lithology row {row_number}: segment {segment_number} {field} "
                "must be numeric."
            )
        number = float(raw)
        if not math.isfinite(number):
            raise ValueError(
                f"lithology row {row_number}: segment {segment_number} {field} "
                "must be finite."
            )
        md_values.append(number)
    coordinates: list[tuple[float, float, float]] = []
    for label, raw_coordinates in zip(("start XYZ", "end XYZ"), value[2:]):
        if not isinstance(raw_coordinates, (tuple, list)) or len(raw_coordinates) != 3:
            raise ValueError(
                f"lithology row {row_number}: segment {segment_number} {label} "
                "must have three coordinates."
            )
        point: list[float] = []
        for raw in raw_coordinates:
            if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
                raise ValueError(
                    f"lithology row {row_number}: segment {segment_number} "
                    f"{label} values must be numeric."
                )
            coordinate = float(raw)
            if not math.isfinite(coordinate):
                raise ValueError(
                    f"lithology row {row_number}: segment {segment_number} "
                    f"{label} values must be finite."
                )
            point.append(coordinate)
        coordinates.append((point[0], point[1], point[2]))
    return md_values[0], md_values[1], coordinates[0], coordinates[1]


def build_geological_block_model(
    positioned_lithology: list[PositionedRow],
    positioned_composites: list[PositionedRow],
    *,
    origin_m: tuple[float, float, float] = GRID_ORIGIN_M,
    block_size_m: tuple[float, float, float] = BLOCK_SIZE_M,
    shape: tuple[int, int, int] = GRID_SHAPE,
) -> tuple[list[GeologicalBlockRecord], list[IntervalCoverage]]:
    """Assign only codes supported by positive-length observed 3D intersections."""
    if len(origin_m) != 3 or len(block_size_m) != 3 or len(shape) != 3:
        raise ValueError("Grid origin, block dimensions, and shape must have 3 axes.")
    if any(size <= 0 or not math.isfinite(size) for size in block_size_m):
        raise ValueError("Block dimensions must be positive and finite.")
    if any(type(count) is not int or count <= 0 for count in shape):
        raise ValueError("Grid dimensions must be positive integers.")
    if any(not math.isfinite(value) for value in origin_m):
        raise ValueError("Grid origin coordinates must be finite.")

    support: dict[tuple[int, int, int], _CellSupport] = defaultdict(
        lambda: _CellSupport(codes=[], length=0.0, intervals=[])
    )
    coverage: list[IntervalCoverage] = []
    tolerance = 1e-8
    for row_number, row in enumerate(positioned_lithology, start=1):
        hole_id = str(row.get("hole_id", "")).strip()
        from_md = _coordinate(row, "from_m", table="lithology", row_number=row_number)
        to_md = _coordinate(row, "to_m", table="lithology", row_number=row_number)
        if not hole_id or from_md >= to_md:
            raise ValueError(f"lithology row {row_number}: invalid hole_id or interval.")
        interval_id = f"{hole_id}:{from_md:.9f}-{to_md:.9f}"
        segments = row.get("trajectory_segments")
        if not isinstance(segments, (tuple, list)) or not segments:
            raise ValueError(
                f"lithology row {row_number}: positioned trajectory segments are required."
            )
        validated_segments = [
            _positioned_segment(segment, row_number=row_number, segment_number=index)
            for index, segment in enumerate(segments, start=1)
        ]
        code_value = row.get("lith_code")
        code = code_value.strip() if isinstance(code_value, str) else ""
        inside_length = 0.0
        outside_length = 0.0
        for segment in validated_segments:
            parts = _segment_grid_parts(
                segment, origin_m=origin_m, block_size_m=block_size_m, shape=shape
            )
            for cell, part_length in parts:
                if cell is None:
                    outside_length += part_length
                    continue
                inside_length += part_length
                cell_support = support[cell]
                cell_support["codes"].append(code or None)
                cell_support["length"] += part_length
                cell_support["intervals"].append(interval_id)

        observed_length = to_md - from_md
        accounted = inside_length + outside_length
        if not math.isclose(accounted, observed_length, rel_tol=0.0, abs_tol=tolerance):
            raise ValueError(
                f"lithology row {row_number}: interval length accounting differs by "
                f"{accounted - observed_length:.12g} m."
            )
        coverage.append(
            {
                "interval_id": interval_id,
                "hole_id": hole_id,
                "from_m": from_md,
                "to_m": to_md,
                "observed_length_m": observed_length,
                "inside_length_m": inside_length,
                "outside_length_m": outside_length,
            }
        )

    assay_support: dict[tuple[int, int, int], int] = defaultdict(int)
    for row_number, row in enumerate(positioned_composites, start=1):
        coordinates = tuple(
            _coordinate(row, field, table="composite", row_number=row_number)
            for field in ("x_mid", "y_mid", "z_mid")
        )
        index_values = tuple(
            math.floor((value - origin) / size)
            for value, origin, size in zip(coordinates, origin_m, block_size_m)
        )
        indices = (index_values[0], index_values[1], index_values[2])
        if all(0 <= index < count for index, count in zip(indices, shape)):
            assay_support[indices] += 1

    blocks: list[GeologicalBlockRecord] = []
    nx, ny, nz = shape
    dx, dy, dz = block_size_m
    ox, oy, oz = origin_m
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                index = (i, j, k)
                cell_support = support.get(index)
                codes = cell_support["codes"] if cell_support else []
                unique_codes = sorted({code for code in codes if code is not None})
                interval_ids = sorted(set(cell_support["intervals"])) if cell_support else []
                has_empty_code = bool(cell_support) and any(code is None for code in codes)
                assigned = bool(codes) and not has_empty_code and len(unique_codes) == 1
                reason = (
                    "ASSIGNED"
                    if assigned
                    else "NO_LITHOLOGY_SUPPORT"
                    if not codes
                    else "EMPTY_CODE"
                    if has_empty_code
                    else "CODE_CONFLICT"
                )
                x_min, y_min, z_min = ox + i * dx, oy + j * dy, oz + k * dz
                blocks.append(
                    GeologicalBlockRecord(
                        i=i,
                        j=j,
                        k=k,
                        x_min=x_min,
                        y_min=y_min,
                        z_min=z_min,
                        x_max=x_min + dx,
                        y_max=y_min + dy,
                        z_max=z_min + dz,
                        x_center=x_min + dx / 2,
                        y_center=y_min + dy / 2,
                        z_center=z_min + dz / 2,
                        lith_code=unique_codes[0] if assigned else "",
                        lith_status="ASSIGNED" if assigned else "UNKNOWN/UNASSIGNED",
                        lith_support_count=len(interval_ids),
                        lith_support_codes="|".join(unique_codes),
                        assay_composite_support_count=assay_support.get(index, 0),
                        lith_support_length_m=(
                            float(cell_support["length"]) if cell_support else 0.0
                        ),
                        lith_support_interval_count=len(interval_ids),
                        lith_support_interval_ids="|".join(interval_ids),
                        lith_assignment_reason=reason,
                    )
                )
    return blocks, coverage


def build_geological_block_model_from_raw(
    raw_data: RawData,
    positioned_composites: list[PositionedRow],
    *,
    origin_m: tuple[float, float, float] = GRID_ORIGIN_M,
    block_size_m: tuple[float, float, float] = BLOCK_SIZE_M,
    shape: tuple[int, int, int] = GRID_SHAPE,
) -> tuple[list[GeologicalBlockRecord], list[IntervalCoverage], list[PositionedRow]]:
    """Position raw lithology intervals and build the interval-supported model."""
    trajectory = desurvey(raw_data["collar"], raw_data["survey"])
    interval_data: IntervalData = {
        "assay": raw_data["assay"],
        "lithology": raw_data["lithology"],
        "alteration": raw_data["alteration"],
        "density": raw_data["density"],
    }
    positioned_lithology = position_intervals(trajectory, interval_data)["lithology"]
    blocks, coverage = build_geological_block_model(
        positioned_lithology,
        positioned_composites,
        origin_m=origin_m,
        block_size_m=block_size_m,
        shape=shape,
    )
    return blocks, coverage, positioned_lithology


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


def write_geological_block_model_csv(
    blocks: list[GeologicalBlockRecord], output_path: Path
) -> None:
    """Write the interval-supported model as a separate derivative."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=GEOLOGICAL_BLOCK_COLUMNS, extrasaction="raise"
        )
        writer.writeheader()
        for block in blocks:
            writer.writerow(dict(block))

"""Create length-weighted assay composites constrained to continuous lithology."""

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from src.mod1.desurvey import Trajectory, desurvey
from src.mod1.loader import CsvRow, IntervalData, load_raw_data
from src.mod1.positioning import PositionedRow, position_intervals
from src.mod1.validator import validate_data


DEFAULT_COMPOSITE_LENGTH_M = 2.0
INTERVAL_TOLERANCE_M = 1e-8
COMPOSITE_COLUMNS = (
    "hole_id",
    "from_m",
    "to_m",
    "length_m",
    "mid_m",
    "x_mid",
    "y_mid",
    "z_mid",
    "lith_code",
    "cu_pct",
    "residual_flag",
    "source_sample_count",
    "source_sample_ids",
)


class Composite(TypedDict):
    """A composite interval and its source assay sample provenance."""

    hole_id: str
    from_m: float
    to_m: float
    length_m: float
    lith_code: str
    cu_pct: float
    residual_flag: bool
    source_sample_ids: list[str]


class CompositeAccumulator(TypedDict):
    """Mutable weighted totals while filling one target-length composite."""

    hole_id: str
    from_m: float
    to_m: float
    length_m: float
    lith_code: str
    cu_length_sum: float
    source_sample_ids: set[str]


def _number(row: CsvRow, field: str, *, table: str, row_number: int) -> float:
    raw_value = row.get(field, "")
    try:
        value = float(raw_value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{table} row {row_number}, field {field!r} must be numeric; "
            f"got {raw_value!r}."
        ) from error
    if not math.isfinite(value):
        raise ValueError(
            f"{table} row {row_number}, field {field!r} must be finite; "
            f"got {raw_value!r}."
        )
    return value


def _interval(row: CsvRow, *, table: str, row_number: int) -> tuple[float, float]:
    start = _number(row, "from_m", table=table, row_number=row_number)
    end = _number(row, "to_m", table=table, row_number=row_number)
    if start >= end:
        raise ValueError(
            f"{table} row {row_number}: from_m must be less than to_m."
        )
    return start, end


def split_assays_at_lithology_contacts(
    assays: list[CsvRow], lithology: list[CsvRow]
) -> list[CsvRow]:
    """Split assay intervals at lithology boundaries and assign observed codes.

    Each assay must be completely and unambiguously covered by lithology
    intervals. Raw input mappings are copied, never changed.
    """
    lithology_by_hole: dict[str, list[tuple[float, float, str, int]]] = defaultdict(list)
    for row_number, row in enumerate(lithology, start=1):
        hole_id = row.get("hole_id", "").strip()
        lith_code = row.get("lith_code", "").strip()
        if not hole_id or not lith_code:
            raise ValueError(
                f"lithology row {row_number}: hole_id and lith_code are required."
            )
        start, end = _interval(row, table="lithology", row_number=row_number)
        lithology_by_hole[hole_id].append((start, end, lith_code, row_number))

    for rows in lithology_by_hole.values():
        rows.sort(key=lambda interval: (interval[0], interval[1], interval[3]))

    split_rows: list[CsvRow] = []
    for assay_row_number, assay in enumerate(assays, start=1):
        hole_id = assay.get("hole_id", "").strip()
        sample_id = assay.get("sample_id", "").strip()
        if not hole_id or not sample_id:
            raise ValueError(
                f"assay row {assay_row_number}: hole_id and sample_id are required."
            )
        start, end = _interval(assay, table="assay", row_number=assay_row_number)
        cu_pct = _number(
            assay, "cu_pct", table="assay", row_number=assay_row_number
        )
        if cu_pct < 0:
            raise ValueError(
                f"assay row {assay_row_number}: cu_pct must be non-negative."
            )

        hole_lithology = lithology_by_hole.get(hole_id, [])
        overlaps = [
            (lith_start, lith_end, lith_code, lith_row_number)
            for lith_start, lith_end, lith_code, lith_row_number in hole_lithology
            if lith_start < end and lith_end > start
        ]
        cursor = start
        sample_segment = 0
        for lith_start, lith_end, lith_code, lith_row_number in overlaps:
            segment_start = max(start, lith_start)
            segment_end = min(end, lith_end)
            if segment_end <= segment_start:
                continue
            if segment_start > cursor + INTERVAL_TOLERANCE_M:
                raise ValueError(
                    f"assay sample {sample_id!r} has an uncovered lithology gap "
                    f"from {cursor} to {segment_start} m."
                )
            if segment_start < cursor - INTERVAL_TOLERANCE_M:
                raise ValueError(
                    f"assay sample {sample_id!r} overlaps lithology intervals "
                    f"near {segment_start} m (lithology row {lith_row_number})."
                )
            piece_start = cursor
            piece_end = segment_end
            if piece_end > piece_start:
                sample_segment += 1
                piece = dict(assay)
                piece.update(
                    {
                        "from_m": format(piece_start, ".12g"),
                        "to_m": format(piece_end, ".12g"),
                        "length_m": format(piece_end - piece_start, ".12g"),
                        "lith_code": lith_code,
                        "source_sample_id": sample_id,
                        "source_segment_index": str(sample_segment),
                    }
                )
                split_rows.append(piece)
                cursor = piece_end
            if cursor >= end - INTERVAL_TOLERANCE_M:
                break

        if cursor < end - INTERVAL_TOLERANCE_M:
            raise ValueError(
                f"assay sample {sample_id!r} has an uncovered lithology gap "
                f"from {cursor} to {end} m."
            )
        if not sample_segment:
            raise ValueError(
                f"assay sample {sample_id!r} is not covered by lithology."
            )
    return split_rows


def _new_composite(
    hole_id: str, lith_code: str, start: float
) -> CompositeAccumulator:
    return {
        "hole_id": hole_id,
        "from_m": start,
        "to_m": start,
        "length_m": 0.0,
        "lith_code": lith_code,
        "cu_length_sum": 0.0,
        "source_sample_ids": set(),
    }


def composite_assays(
    split_assays: list[CsvRow],
    target_length_m: float = DEFAULT_COMPOSITE_LENGTH_M,
) -> list[Composite]:
    """Build length-weighted composites within each continuous lithology run."""
    if not math.isfinite(target_length_m) or target_length_m <= 0:
        raise ValueError("target_length_m must be finite and greater than zero.")

    assays_by_hole: dict[str, list[CsvRow]] = defaultdict(list)
    for row in split_assays:
        assays_by_hole[row.get("hole_id", "").strip()].append(row)

    composites: list[Composite] = []
    for hole_id in sorted(assays_by_hole):
        rows = sorted(
            assays_by_hole[hole_id],
            key=lambda row: (
                _number(row, "from_m", table="split assay", row_number=0),
                _number(row, "to_m", table="split assay", row_number=0),
            ),
        )
        run_rows: list[CsvRow] = []
        current_lith_code: str | None = None

        def flush_run() -> None:
            if not run_rows:
                return
            current: CompositeAccumulator | None = None
            previous_end: float | None = None
            for row_number, row in enumerate(run_rows, start=1):
                start, end = _interval(row, table="split assay", row_number=row_number)
                cu_pct = _number(
                    row, "cu_pct", table="split assay", row_number=row_number
                )
                if cu_pct < 0:
                    raise ValueError(
                        f"split assay row {row_number}: cu_pct must be non-negative."
                    )
                if previous_end is not None:
                    difference = start - previous_end
                    if difference > INTERVAL_TOLERANCE_M:
                        raise ValueError(
                            f"assay coverage gap in hole {hole_id!r} and "
                            f"lithology {current_lith_code!r}: "
                            f"{previous_end} to {start} m."
                        )
                    if difference < -INTERVAL_TOLERANCE_M:
                        raise ValueError(
                            f"assay intervals overlap in hole {hole_id!r} and "
                            f"lithology {current_lith_code!r} near {start} m."
                        )
                cursor = start
                while cursor < end - INTERVAL_TOLERANCE_M:
                    if current is None:
                        current = _new_composite(
                            hole_id, current_lith_code or "", cursor
                        )
                    remaining = target_length_m - current["length_m"]
                    take = min(end - cursor, remaining)
                    current["to_m"] = cursor + take
                    current["length_m"] += take
                    current["cu_length_sum"] += cu_pct * take
                    current["source_sample_ids"].add(
                        row.get("source_sample_id", row.get("sample_id", ""))
                    )
                    cursor += take
                    previous_end = cursor
                    if current["length_m"] >= target_length_m - INTERVAL_TOLERANCE_M:
                        composites.append(
                            _finalize_composite(current, target_length_m)
                        )
                        current = None
            if current is not None and current["length_m"] > 0:
                composites.append(_finalize_composite(current, target_length_m))

        for row in rows:
            lith_code = row.get("lith_code", "").strip()
            if not lith_code:
                raise ValueError("split assay row is missing lith_code.")
            if current_lith_code is None:
                current_lith_code = lith_code
            elif lith_code != current_lith_code:
                flush_run()
                run_rows = []
                current_lith_code = lith_code
            run_rows.append(row)
        flush_run()
    return composites


def _finalize_composite(
    composite: CompositeAccumulator, target_length_m: float
) -> Composite:
    length = composite["length_m"]
    if length <= 0 or length > target_length_m + INTERVAL_TOLERANCE_M:
        raise ValueError(f"Invalid composite length {length} m.")
    source_ids = composite["source_sample_ids"]
    return {
        "hole_id": composite["hole_id"],
        "from_m": composite["from_m"],
        "to_m": composite["to_m"],
        "length_m": length,
        "lith_code": composite["lith_code"],
        "cu_pct": composite["cu_length_sum"] / length,
        "residual_flag": length < target_length_m - INTERVAL_TOLERANCE_M,
        "source_sample_ids": sorted(source_ids),
    }


def _as_csv_rows(composites: list[Composite]) -> list[CsvRow]:
    return [
        {
            "hole_id": composite["hole_id"],
            "from_m": format(composite["from_m"], ".12g"),
            "to_m": format(composite["to_m"], ".12g"),
            "length_m": format(composite["length_m"], ".12g"),
            "lith_code": composite["lith_code"],
            "cu_pct": format(composite["cu_pct"], ".12g"),
        }
        for composite in composites
    ]


def write_positioned_composites(
    composites: list[Composite],
    trajectory: Trajectory,
    output_path: Path,
) -> list[PositionedRow]:
    """Position composites with M01's existing interval positioning function."""
    raw_composites = _as_csv_rows(composites)
    intervals: IntervalData = {
        "assay": raw_composites,
        "lithology": [],
        "alteration": [],
        "density": [],
    }
    positioned = position_intervals(trajectory, intervals)["assay"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=COMPOSITE_COLUMNS)
        writer.writeheader()
        for composite, positioned_row in zip(composites, positioned, strict=True):
            source_ids = composite["source_sample_ids"]
            writer.writerow(
                {
                    "hole_id": composite["hole_id"],
                    "from_m": format(composite["from_m"], ".12g"),
                    "to_m": format(composite["to_m"], ".12g"),
                    "length_m": format(composite["length_m"], ".12g"),
                    "mid_m": format(float(positioned_row["mid_m"]), ".12g"),
                    "x_mid": format(float(positioned_row["x_mid"]), ".12g"),
                    "y_mid": format(float(positioned_row["y_mid"]), ".12g"),
                    "z_mid": format(float(positioned_row["z_mid"]), ".12g"),
                    "lith_code": composite["lith_code"],
                    "cu_pct": format(composite["cu_pct"], ".12g"),
                    "residual_flag": str(composite["residual_flag"]).lower(),
                    "source_sample_count": len(source_ids),
                    "source_sample_ids": ";".join(source_ids),
                }
            )
    return positioned


def build_m01b_composites(
    raw_directory: Path,
    output_path: Path,
    target_length_m: float = DEFAULT_COMPOSITE_LENGTH_M,
) -> list[Composite]:
    """Load raw observations, constrain composites, position and export them."""
    raw_data = load_raw_data(raw_directory)
    validation = validate_data(raw_data)
    errors = [finding for finding in validation["findings"] if finding["severity"] == "ERROR"]
    if errors:
        first = errors[0]
        raise ValueError(
            f"Cannot composite invalid inputs: {len(errors)} validation errors; "
            f"first is {first['rule_id']} in {first['source_file']} "
            f"row {first['row_number']}."
        )

    trajectory = desurvey(raw_data["collar"], raw_data["survey"])
    split_assays = split_assays_at_lithology_contacts(
        raw_data["assay"], raw_data["lithology"]
    )
    composites = composite_assays(split_assays, target_length_m)
    write_positioned_composites(composites, trajectory, output_path)
    return composites

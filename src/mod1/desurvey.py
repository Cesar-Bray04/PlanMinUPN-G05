"""Calculate drillhole trajectories using the Minimum Curvature method."""

import math
from typing import TypedDict

from src.mod1.loader import CsvRow


class TrajectoryPoint(TypedDict):
    """A spatial trajectory point at a measured depth."""

    hole_id: str
    md_m: float
    x: float
    y: float
    z: float


Trajectory = dict[str, list[TrajectoryPoint]]


def _number(row: CsvRow, field: str, *, source: str) -> float:
    raw_value = row.get(field)
    if raw_value is None or not raw_value.strip():
        raise ValueError(f"{source} field {field!r} is missing or empty.")
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError(
            f"{source} field {field!r} must be numeric; got {raw_value!r}."
        ) from error
    if not math.isfinite(value):
        raise ValueError(
            f"{source} field {field!r} must be finite; got {raw_value!r}."
        )
    return value


def _direction(azimuth_deg: float, dip_deg: float) -> tuple[float, float, float]:
    azimuth = math.radians(azimuth_deg)
    dip = math.radians(dip_deg)
    return (
        math.sin(azimuth) * math.cos(dip),
        math.cos(azimuth) * math.cos(dip),
        math.sin(dip),
    )


def _dogleg_and_ratio_factor(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> tuple[float, float]:
    cross = (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )
    cross_norm = math.hypot(*cross)
    dot = sum(a * b for a, b in zip(first, second))
    beta = math.atan2(cross_norm, dot)
    ratio_factor = 1.0 if beta == 0.0 else 2.0 * math.tan(beta / 2.0) / beta
    return beta, ratio_factor


def _trajectory_for_hole(
    collar_row: CsvRow, survey_rows: list[CsvRow]
) -> list[TrajectoryPoint]:
    hole_id = collar_row["hole_id"]
    x = _number(collar_row, "x", source=f"collar {hole_id!r}")
    y = _number(collar_row, "y", source=f"collar {hole_id!r}")
    z = _number(collar_row, "z", source=f"collar {hole_id!r}")

    stations: list[tuple[float, tuple[float, float, float]]] = []
    previous_md: float | None = None
    for row_number, row in enumerate(survey_rows, start=1):
        source = f"survey row {row_number} for hole {hole_id!r}"
        md = _number(row, "depth_m", source=source)
        azimuth = _number(row, "azimuth_deg", source=source)
        dip = _number(row, "dip_deg", source=source)
        if md < 0:
            raise ValueError(f"{source} depth_m must be non-negative.")
        if previous_md is not None and md < previous_md:
            raise ValueError(
                f"Survey stations for hole {hole_id!r} are not ordered by "
                "increasing depth_m."
            )
        previous_md = md
        stations.append((md, _direction(azimuth, dip)))

    if not any(md == 0.0 for md, _ in stations):
        raise ValueError(f"Survey for hole {hole_id!r} has no station at MD=0.")

    points: list[TrajectoryPoint] = [
        {"hole_id": hole_id, "md_m": 0.0, "x": x, "y": y, "z": z}
    ]
    for (md_1, direction_1), (md_2, direction_2) in zip(stations, stations[1:]):
        interval_length = md_2 - md_1
        if interval_length <= 0:
            raise ValueError(
                f"Survey stations for hole {hole_id!r} are not ordered by "
                "strictly increasing depth_m."
            )
        _, ratio_factor = _dogleg_and_ratio_factor(direction_1, direction_2)
        displacement = tuple(
            interval_length * (a + b) * ratio_factor / 2.0
            for a, b in zip(direction_1, direction_2)
        )
        x += displacement[0]
        y += displacement[1]
        z += displacement[2]
        points.append(
            {"hole_id": hole_id, "md_m": md_2, "x": x, "y": y, "z": z}
        )

    return points


def desurvey(collar: list[CsvRow], survey: list[CsvRow]) -> Trajectory:
    """Return XYZ trajectory points grouped by hole ID.

    Survey rows are consumed in their supplied order. The function does not
    modify its inputs, compare collar orientation with survey at MD=0, or
    extrapolate beyond the last survey station.
    """
    collar_by_hole: dict[str, CsvRow] = {}
    for row in collar:
        hole_id = row.get("hole_id", "")
        if not hole_id.strip():
            raise ValueError("Collar contains a missing or empty hole_id.")
        if hole_id in collar_by_hole:
            raise ValueError(f"Collar contains duplicate hole_id {hole_id!r}.")
        collar_by_hole[hole_id] = row

    survey_by_hole: dict[str, list[CsvRow]] = {hole_id: [] for hole_id in collar_by_hole}
    for row_number, row in enumerate(survey, start=1):
        hole_id = row.get("hole_id", "")
        if hole_id not in collar_by_hole:
            raise ValueError(
                f"Survey row {row_number} references unknown hole_id {hole_id!r}."
            )
        survey_by_hole[hole_id].append(row)

    return {
        hole_id: _trajectory_for_hole(collar_row, survey_by_hole[hole_id])
        for hole_id, collar_row in collar_by_hole.items()
    }

"""Position downhole intervals on an already calculated XYZ trajectory."""

import math
from typing import TypedDict

from src.mod1.desurvey import Trajectory
from src.mod1.loader import CsvRow, IntervalData


PositionedRow = dict[str, object]


class PositionedIntervals(TypedDict):
    """Interval tables enriched with XYZ coordinates at their boundaries/midpoint."""

    assay: list[PositionedRow]
    lithology: list[PositionedRow]
    alteration: list[PositionedRow]
    density: list[PositionedRow]


XYZ = tuple[float, float, float]


def _md_value(value: object, *, table: str, row_number: int, field: str, hole_id: str) -> float:
    context = f"{table} row {row_number}, hole_id {hole_id!r}, field {field!r}"
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"{context}: MD is missing or empty.")
    try:
        md = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{context}: MD must be numeric; got {value!r}.") from error
    if not math.isfinite(md):
        raise ValueError(f"{context}: MD must be finite; got {value!r}.")
    return md


def _validated_trajectory(
    trajectory: Trajectory, hole_id: str, *, table: str, row_number: int
) -> list[tuple[float, XYZ]]:
    if hole_id not in trajectory:
        raise ValueError(
            f"{table} row {row_number}, hole_id {hole_id!r}: "
            "no trajectory is available for this hole_id."
        )
    stations = trajectory[hole_id]
    if not stations:
        raise ValueError(
            f"{table} row {row_number}, hole_id {hole_id!r}: trajectory is empty."
        )
    validated: list[tuple[float, XYZ]] = []
    previous_md: float | None = None
    for station_number, station in enumerate(stations, start=1):
        md = _md_value(
            station.get("md_m"),
            table=f"trajectory station {station_number}",
            row_number=row_number,
            field="md_m",
            hole_id=hole_id,
        )
        if previous_md is not None and md <= previous_md:
            raise ValueError(
                f"Trajectory for hole_id {hole_id!r} must have strictly "
                "increasing md_m values."
            )
        previous_md = md
        coordinates: list[float] = []
        for field in ("x", "y", "z"):
            value = station.get(field)
            try:
                coordinate = float(value)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Trajectory station {station_number}, hole_id {hole_id!r}, "
                    f"field {field!r} must be numeric; got {value!r}."
                ) from error
            if not math.isfinite(coordinate):
                raise ValueError(
                    f"Trajectory station {station_number}, hole_id {hole_id!r}, "
                    f"field {field!r} must be finite; got {value!r}."
                )
            coordinates.append(coordinate)
        validated.append((md, (coordinates[0], coordinates[1], coordinates[2])))
    return validated


def _interpolate_xyz(
    stations: list[tuple[float, XYZ]],
    md: float,
    *,
    table: str,
    row_number: int,
    hole_id: str,
    field: str,
) -> XYZ:
    minimum_md = stations[0][0]
    maximum_md = stations[-1][0]
    if md < minimum_md or md > maximum_md:
        raise ValueError(
            f"{table} row {row_number}, hole_id {hole_id!r}: "
            f"{field} MD {md} is outside trajectory range "
            f"[{minimum_md}, {maximum_md}]."
        )

    for station_md, coordinates in stations:
        if md == station_md:
            return coordinates

    for (md_1, point_1), (md_2, point_2) in zip(stations, stations[1:]):
        if md_1 < md < md_2:
            fraction = (md - md_1) / (md_2 - md_1)
            return tuple(
                first + fraction * (second - first)
                for first, second in zip(point_1, point_2)
            )  # type: ignore[return-value]

    raise ValueError(
        f"{table} row {row_number}, hole_id {hole_id!r}: "
        f"could not locate {field} MD {md} on the trajectory."
    )


def _position_table(
    table: str,
    rows: list[CsvRow],
    trajectory: Trajectory,
) -> list[PositionedRow]:
    positioned: list[PositionedRow] = []
    for row_number, row in enumerate(rows, start=1):
        hole_id = row.get("hole_id", "")
        if not hole_id.strip():
            raise ValueError(
                f"{table} row {row_number}: hole_id is missing or empty."
            )
        stations = _validated_trajectory(
            trajectory, hole_id, table=table, row_number=row_number
        )
        from_md = _md_value(
            row.get("from_m"),
            table=table,
            row_number=row_number,
            field="from_m",
            hole_id=hole_id,
        )
        to_md = _md_value(
            row.get("to_m"),
            table=table,
            row_number=row_number,
            field="to_m",
            hole_id=hole_id,
        )
        mid_md = (from_md + to_md) / 2.0
        from_xyz = _interpolate_xyz(
            stations,
            from_md,
            table=table,
            row_number=row_number,
            hole_id=hole_id,
            field="from_m",
        )
        mid_xyz = _interpolate_xyz(
            stations,
            mid_md,
            table=table,
            row_number=row_number,
            hole_id=hole_id,
            field="mid_m",
        )
        to_xyz = _interpolate_xyz(
            stations,
            to_md,
            table=table,
            row_number=row_number,
            hole_id=hole_id,
            field="to_m",
        )
        positioned.append(
            {
                **row,
                "mid_m": mid_md,
                "x_from": from_xyz[0],
                "y_from": from_xyz[1],
                "z_from": from_xyz[2],
                "x_mid": mid_xyz[0],
                "y_mid": mid_xyz[1],
                "z_mid": mid_xyz[2],
                "x_to": to_xyz[0],
                "y_to": to_xyz[1],
                "z_to": to_xyz[2],
            }
        )
    return positioned


def position_intervals(
    trajectory: Trajectory, intervals: IntervalData
) -> PositionedIntervals:
    """Enrich interval rows with linearly interpolated XYZ positions.

    Interpolation is performed on the discretized XYZ trajectory, representing
    the straight segment between calculated stations; it does not reconstruct
    Minimum Curvature geometry or add observed geometry.
    """
    return {
        table: _position_table(table, intervals[table], trajectory)
        for table in ("assay", "lithology", "alteration", "density")
    }

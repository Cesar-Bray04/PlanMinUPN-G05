"""Interpolate topography and classify preliminary blocks against the surface."""

import csv
import math
from pathlib import Path
from typing import NamedTuple

import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial import Delaunay, QhullError

from src.mod1.block_model import BLOCK_MODEL_COLUMNS, BlockRecord

TOPOGRAPHY_COLUMNS = ("PID", "X", "Y", "Z")
TOPOGRAPHIC_BLOCK_COLUMNS = (*BLOCK_MODEL_COLUMNS, "topo_z_m", "topo_status")
TOPO_STATUS_VALUES = {"ROCK", "AIR", "PARTIAL"}


class TopographicBlockRecord(BlockRecord):
    """A preliminary block with independent topographic elevation and status."""

    topo_z_m: float
    topo_status: str


class TopographySurface(NamedTuple):
    """Scattered topographic observations and their linear TIN interpolator."""

    points: np.ndarray
    simplices: np.ndarray
    interpolator: LinearNDInterpolator

    def interpolate(self, xy: np.ndarray) -> np.ndarray:
        """Interpolate points inside the triangulated coverage; never extrapolate."""
        query = np.asarray(xy, dtype=float)
        if query.ndim != 2 or query.shape[1] != 2:
            raise ValueError("Topography query coordinates must have shape (n, 2).")
        elevations = np.asarray(self.interpolator(query), dtype=float).reshape(-1)
        missing = ~np.isfinite(elevations)
        if missing.any():
            examples = query[missing][:5].tolist()
            raise ValueError(
                f"Topography does not cover {int(missing.sum())} XY query point(s); "
                f"first uncovered coordinates: {examples}."
            )
        return elevations


def read_topography_points(path: Path) -> np.ndarray:
    """Read and validate finite PID/X/Y/Z observations without changing the source."""
    points: list[tuple[float, float, float]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing = set(TOPOGRAPHY_COLUMNS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(
                f"Topography CSV is missing required fields: {sorted(missing)}."
            )
        for row_number, row in enumerate(reader, start=2):
            values: list[float] = []
            for field in ("X", "Y", "Z"):
                try:
                    value = float(row[field])
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"Topography CSV row {row_number}: {field} must be numeric."
                    ) from error
                if not math.isfinite(value):
                    raise ValueError(
                        f"Topography CSV row {row_number}: {field} must be finite."
                    )
                values.append(value)
            points.append((values[0], values[1], values[2]))

    if len(points) < 3:
        raise ValueError("Topography CSV must contain at least three XYZ points.")
    return np.asarray(points, dtype=float)


def triangulate_topography(points: np.ndarray) -> TopographySurface:
    """Build a linear TIN from unique XY observations."""
    observations = np.asarray(points, dtype=float)
    if (
        observations.ndim != 2
        or observations.shape[1] != 3
        or observations.shape[0] < 3
        or not np.isfinite(observations).all()
    ):
        raise ValueError("Topography points must be a finite array with shape (n, 3).")
    if np.unique(observations[:, :2], axis=0).shape[0] != observations.shape[0]:
        raise ValueError("Topography contains duplicate XY coordinates.")
    try:
        triangulation = Delaunay(observations[:, :2])
    except QhullError as error:
        raise ValueError("Topography XY observations cannot form a TIN.") from error
    interpolator = LinearNDInterpolator(
        triangulation, observations[:, 2], fill_value=np.nan
    )
    return TopographySurface(
        observations,
        triangulation.simplices,
        interpolator,
    )


def classify_blocks_against_topography(
    blocks: list[BlockRecord], surface: TopographySurface
) -> list[TopographicBlockRecord]:
    """Add interpolated center elevations and ROCK/AIR/PARTIAL states."""
    if not blocks:
        raise ValueError("Block model contains no blocks.")

    xy_to_position: dict[tuple[float, float], int] = {}
    xy_values: list[tuple[float, float]] = []
    for block in blocks:
        x, y = float(block["x_center"]), float(block["y_center"])
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("Block-center XY coordinates must be finite.")
        xy = (x, y)
        if xy not in xy_to_position:
            xy_to_position[xy] = len(xy_values)
            xy_values.append(xy)

    elevations = surface.interpolate(np.asarray(xy_values, dtype=float))
    classified: list[TopographicBlockRecord] = []
    for block in blocks:
        z_min, z_max = float(block["z_min"]), float(block["z_max"])
        if not math.isfinite(z_min) or not math.isfinite(z_max) or z_min >= z_max:
            raise ValueError("Each block must have finite z_min < z_max.")
        topo_z = float(
            elevations[xy_to_position[(float(block["x_center"]), float(block["y_center"]))]]
        )
        if topo_z <= z_min:
            status = "AIR"
        elif topo_z >= z_max:
            status = "ROCK"
        else:
            status = "PARTIAL"
        classified.append(
            TopographicBlockRecord(
                **block,
                topo_z_m=topo_z,
                topo_status=status,
            )
        )
    return classified


def prepare_topographic_block_model(
    blocks: list[BlockRecord], topography_path: Path
) -> tuple[list[TopographicBlockRecord], TopographySurface]:
    """Interpolate surface elevations for all block XY centers and classify them."""
    surface = triangulate_topography(read_topography_points(topography_path))
    return classify_blocks_against_topography(blocks, surface), surface


def write_topographic_block_model_csv(
    blocks: list[TopographicBlockRecord], output_path: Path
) -> None:
    """Write a new topography-enriched block-model derivative."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=TOPOGRAPHIC_BLOCK_COLUMNS, extrasaction="raise"
        )
        writer.writeheader()
        for block in blocks:
            writer.writerow(dict(block))

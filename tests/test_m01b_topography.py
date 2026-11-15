import csv
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import pytest

from src.mod1.block_model import BlockRecord
from src.mod1.block_model_visualizer import (
    build_topographic_block_model_figure,
    read_block_model_csv,
)
from src.mod1.desurvey import Trajectory
from src.mod1.topography import (
    classify_blocks_against_topography,
    prepare_topographic_block_model,
    read_topography_points,
    triangulate_topography,
    write_topographic_block_model_csv,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "data" / "processed" / "m01b" / "block_model_preliminary.csv"
TOPOGRAPHY_PATH = PROJECT_ROOT / "data" / "raw" / "topography" / "Topopl.csv"
LITHOLOGY_FIELDS = (
    "lith_code",
    "lith_status",
    "lith_support_count",
    "lith_support_codes",
)


def sample_block(
    *,
    x: float = 5,
    y: float = 5,
    z_min: float = 100,
    z_max: float = 120,
    lith_code: str = "POR",
    lith_status: str = "ASSIGNED",
) -> BlockRecord:
    return {
        "i": 0,
        "j": 0,
        "k": 0,
        "x_min": x - 5,
        "y_min": y - 5,
        "z_min": z_min,
        "x_max": x + 5,
        "y_max": y + 5,
        "z_max": z_max,
        "x_center": x,
        "y_center": y,
        "z_center": (z_min + z_max) / 2,
        "lith_code": lith_code,
        "lith_status": lith_status,
        "lith_support_count": 1 if lith_code else 0,
        "lith_support_codes": lith_code,
        "assay_composite_support_count": 1,
    }


def numeric_block(row: dict[str, str]) -> BlockRecord:
    return {
        "i": int(row["i"]),
        "j": int(row["j"]),
        "k": int(row["k"]),
        "x_min": float(row["x_min"]),
        "y_min": float(row["y_min"]),
        "z_min": float(row["z_min"]),
        "x_max": float(row["x_max"]),
        "y_max": float(row["y_max"]),
        "z_max": float(row["z_max"]),
        "x_center": float(row["x_center"]),
        "y_center": float(row["y_center"]),
        "z_center": float(row["z_center"]),
        "lith_code": row["lith_code"],
        "lith_status": row["lith_status"],
        "lith_support_count": int(row["lith_support_count"]),
        "lith_support_codes": row["lith_support_codes"],
        "assay_composite_support_count": int(row["assay_composite_support_count"]),
    }


def planar_surface():
    points = np.array(
        [
            [0, 0, 100],
            [10, 0, 110],
            [0, 10, 110],
            [10, 10, 120],
        ],
        dtype=float,
    )
    return triangulate_topography(points)


def test_linear_tin_interpolates_inside_coverage_and_rejects_extrapolation():
    surface = planar_surface()

    assert surface.interpolate(np.array([[5, 5]]))[0] == pytest.approx(110)
    with pytest.raises(ValueError, match="does not cover 1 XY"):
        surface.interpolate(np.array([[20, 5]]))


def test_classification_handles_exact_intersection_boundaries_and_keeps_lithology():
    blocks = [
        sample_block(z_min=110, z_max=120, lith_code="AIR"),
        sample_block(z_min=100, z_max=120),
        sample_block(z_min=90, z_max=110),
    ]

    classified = classify_blocks_against_topography(blocks, planar_surface())

    assert [block["topo_status"] for block in classified] == [
        "AIR",
        "PARTIAL",
        "ROCK",
    ]
    assert all(block["topo_z_m"] == pytest.approx(110) for block in classified)
    assert classified[0]["lith_code"] == "AIR"
    assert classified[0]["lith_status"] == "ASSIGNED"
    assert classified[1]["lith_code"] == blocks[1]["lith_code"]


def test_topography_csv_schema_and_duplicate_xy_are_rejected(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text(
        "PID,X,Y,Z\n1,0,0,1\n2,0,0,2\n3,1,0,3\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate XY"):
        triangulate_topography(read_topography_points(path))

    path.write_text("PID,X,Y\n1,0,0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required fields"):
        read_topography_points(path)


def test_real_topography_covers_model_and_new_csv_preserves_lithology(tmp_path):
    with MODEL_PATH.open(encoding="utf-8-sig", newline="") as csv_file:
        original_rows = list(csv.DictReader(csv_file))
    original_lithology = [tuple(row[field] for field in LITHOLOGY_FIELDS) for row in original_rows]
    original_blocks = [numeric_block(row) for row in original_rows]

    classified, surface = prepare_topographic_block_model(
        original_blocks, TOPOGRAPHY_PATH
    )
    output = tmp_path / "block_model_topography.csv"
    write_topographic_block_model_csv(classified, output)
    written = read_block_model_csv(output)

    assert len(surface.points) == 218_112
    assert len({(row["x_center"], row["y_center"]) for row in original_blocks}) == 210
    assert len(classified) == len(original_blocks) == 11_550
    assert all(np.isfinite(block["topo_z_m"]) for block in classified)
    assert {block["topo_status"] for block in classified} == {
        "ROCK",
        "AIR",
        "PARTIAL",
    }
    assert [
        tuple(row[field] for field in LITHOLOGY_FIELDS) for row in written
    ] == original_lithology
    assert all(row["topo_status"] in {"ROCK", "AIR", "PARTIAL"} for row in written)


def test_topographic_figure_contains_surface_lithology_and_status_modes():
    blocks = [
        {
            **sample_block(z_min=110, z_max=120),
            "topo_z_m": 110,
            "topo_status": "AIR",
        },
        {
            **sample_block(z_min=100, z_max=120, lith_code="VOL"),
            "topo_z_m": 110,
            "topo_status": "PARTIAL",
        },
        {
            **sample_block(z_min=90, z_max=110, lith_code="BRX"),
            "topo_z_m": 110,
            "topo_status": "ROCK",
        },
        {
            **sample_block(
                z_min=100,
                z_max=120,
                lith_code="",
                lith_status="UNKNOWN/UNASSIGNED",
            ),
            "topo_z_m": 110,
            "topo_status": "PARTIAL",
        },
    ]
    visual_blocks = [
        {field: str(value) for field, value in block.items()} for block in blocks
    ]
    trajectory: Trajectory = {
        "H-01": [
            {"hole_id": "H-01", "md_m": 0.0, "x": 5.0, "y": 5.0, "z": 110.0},
            {"hole_id": "H-01", "md_m": 1.0, "x": 5.0, "y": 5.0, "z": 109.0},
        ]
    }

    figure = build_topographic_block_model_figure(
        visual_blocks, trajectory, planar_surface()
    )

    meshes = [trace for trace in figure.data if isinstance(trace, go.Mesh3d)]
    assert any(trace.name.startswith("Superficie topográfica") for trace in meshes)
    assert any("Litología POR" in trace.name for trace in meshes)
    assert {trace.name.split(" ")[2] for trace in meshes if "Estado topográfico" in trace.name} == {
        "AIR",
        "PARTIAL",
        "ROCK",
    }
    assert len([trace for trace in figure.data if isinstance(trace, go.Scatter3d)]) == 1
    assert len(figure.layout.updatemenus[0].buttons) == 2
    unknown_mesh = next(trace for trace in meshes if "UNKNOWN/UNASSIGNED" in trace.name)
    assert unknown_mesh.visible == "legendonly"
    assert figure.layout.meta["topography_used"] is True
    assert figure.layout.meta["validation_claim"] is False

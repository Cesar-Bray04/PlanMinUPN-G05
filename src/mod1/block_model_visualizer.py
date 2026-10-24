"""Create an auditable, interactive 3D view of the preliminary block model."""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import plotly.graph_objects as go

from src.mod1.desurvey import Trajectory, desurvey
from src.mod1.loader import load_raw_data


UNKNOWN_STATUS = "UNKNOWN/UNASSIGNED"
UNKNOWN_COLOR = "#9a9a9a"
CATEGORY_COLORS = (
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#17becf",
)
BLOCK_FIELDS = (
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
_CUBE_TRIANGLES = (
    (0, 1, 2),
    (0, 2, 3),
    (4, 6, 5),
    (4, 7, 6),
    (0, 4, 5),
    (0, 5, 1),
    (1, 5, 6),
    (1, 6, 2),
    (2, 6, 7),
    (2, 7, 3),
    (3, 7, 4),
    (3, 4, 0),
)


def read_block_model_csv(path: Path) -> list[dict[str, str]]:
    """Read and validate the block-model fields needed by the 3D view."""
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_fields = set(BLOCK_FIELDS) - set(reader.fieldnames or ())
        if missing_fields:
            raise ValueError(
                f"Block model CSV is missing required fields: {sorted(missing_fields)}."
            )
        rows = list(reader)

    if not rows:
        raise ValueError("Block model CSV contains no blocks.")
    for row_number, row in enumerate(rows, start=2):
        status = row["lith_status"]
        code = row["lith_code"].strip()
        if status == "ASSIGNED" and not code:
            raise ValueError(f"Block model CSV row {row_number}: assigned block has no lith_code.")
        if status == UNKNOWN_STATUS and code:
            raise ValueError(
                f"Block model CSV row {row_number}: unassigned block has a lith_code."
            )
        if status not in {"ASSIGNED", UNKNOWN_STATUS}:
            raise ValueError(
                f"Block model CSV row {row_number}: unsupported lith_status {status!r}."
            )
    return rows


def _cube_mesh(
    blocks: list[dict[str, str]],
    *,
    color: str,
    opacity: float,
    name: str,
    legendgroup: str,
    showlegend: bool = True,
    visible: bool | str = True,
) -> go.Mesh3d:
    x_values: list[float] = []
    y_values: list[float] = []
    z_values: list[float] = []
    customdata: list[list[Any]] = []
    i_faces: list[int] = []
    j_faces: list[int] = []
    k_faces: list[int] = []

    for block in blocks:
        x_min, y_min, z_min = (
            float(block[field]) for field in ("x_min", "y_min", "z_min")
        )
        x_max, y_max, z_max = (
            float(block[field]) for field in ("x_max", "y_max", "z_max")
        )
        vertices = (
            (x_min, y_min, z_min),
            (x_max, y_min, z_min),
            (x_max, y_max, z_min),
            (x_min, y_max, z_min),
            (x_min, y_min, z_max),
            (x_max, y_min, z_max),
            (x_max, y_max, z_max),
            (x_min, y_max, z_max),
        )
        base = len(x_values)
        for x, y, z in vertices:
            x_values.append(x)
            y_values.append(y)
            z_values.append(z)
            customdata.append(
                [
                    block["i"],
                    block["j"],
                    block["k"],
                    block["x_center"],
                    block["y_center"],
                    block["z_center"],
                    block["lith_code"] or UNKNOWN_STATUS,
                    block["lith_status"],
                    block["lith_support_count"],
                    block["lith_support_codes"] or "none",
                    block["assay_composite_support_count"],
                ]
            )
        for first, second, third in _CUBE_TRIANGLES:
            i_faces.append(base + first)
            j_faces.append(base + second)
            k_faces.append(base + third)

    return go.Mesh3d(
        x=x_values,
        y=y_values,
        z=z_values,
        i=i_faces,
        j=j_faces,
        k=k_faces,
        customdata=customdata,
        color=color,
        opacity=opacity,
        flatshading=True,
        name=name,
        legendgroup=legendgroup,
        showlegend=showlegend,
        visible=visible,
        hovertemplate=(
            "Bloque (%{customdata[0]}, %{customdata[1]}, %{customdata[2]})"
            "<br>Centro (X,Y,Z): (%{customdata[3]}, %{customdata[4]}, "
            "%{customdata[5]}) m"
            "<br>lith_code: %{customdata[6]}"
            "<br>Estado: %{customdata[7]}"
            "<br>Soporte litológico: %{customdata[8]}"
            "<br>Códigos de soporte: %{customdata[9]}"
            "<br>Composites soporte assay: %{customdata[10]}"
            "<extra></extra>"
        ),
    )


def build_block_model_figure(
    blocks: list[dict[str, str]], trajectory: Trajectory
) -> go.Figure:
    """Build category meshes, an unknown-state mesh, and drillhole traces."""
    assigned_by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    unknown_blocks: list[dict[str, str]] = []
    for block in blocks:
        if block["lith_status"] == "ASSIGNED":
            assigned_by_code[block["lith_code"].strip()].append(block)
        elif block["lith_status"] == UNKNOWN_STATUS:
            unknown_blocks.append(block)
        else:
            raise ValueError(f"Unsupported lith_status {block['lith_status']!r}.")

    figure = go.Figure()
    codes = sorted(assigned_by_code)
    for code_index, code in enumerate(codes):
        figure.add_trace(
            _cube_mesh(
                assigned_by_code[code],
                color=CATEGORY_COLORS[code_index % len(CATEGORY_COLORS)],
                opacity=0.95,
                name=f"lith_code {code} ({len(assigned_by_code[code])})",
                legendgroup=f"lith_code:{code}",
            )
        )
    if unknown_blocks:
        figure.add_trace(
            _cube_mesh(
                unknown_blocks,
                color=UNKNOWN_COLOR,
                opacity=0.12,
                name=f"{UNKNOWN_STATUS} ({len(unknown_blocks)})",
                legendgroup="lith_status:unknown",
                visible="legendonly",
            )
        )

    for hole_index, (hole_id, stations) in enumerate(sorted(trajectory.items())):
        figure.add_trace(
            go.Scatter3d(
                x=[point["x"] for point in stations],
                y=[point["y"] for point in stations],
                z=[point["z"] for point in stations],
                mode="lines",
                line={"color": "#111111", "width": 4},
                name=f"Sondajes ({len(trajectory)})",
                legendgroup="drillholes",
                showlegend=hole_index == 0,
                text=[
                    f"{hole_id} — MD {point['md_m']:.2f} m"
                    for point in stations
                ],
                hovertemplate="%{text}<br>(X,Y,Z): (%{x:.2f}, %{y:.2f}, %{z:.2f}) m<extra></extra>",
            )
        )

    figure.update_layout(
        title=(
            "Modelo de bloques preliminar - vista 3D diagnostica"
            "<br><sup>Sin topografia; no constituye validacion geologica ni topografica</sup>"
        ),
        scene={
            "xaxis_title": "X local (m)",
            "yaxis_title": "Y local (m)",
            "zaxis_title": "Z local (m)",
            "aspectmode": "data",
        },
        legend={
            "title": "Categorías/estados y soporte",
            "groupclick": "togglegroup",
            "itemsizing": "constant",
        },
        margin={"l": 0, "r": 0, "t": 80, "b": 0},
        meta={
            "topography_used": False,
            "validation_claim": False,
            "block_count": len(blocks),
            "assigned_codes": codes,
        },
    )
    return figure


def build_visualization_from_files(
    block_model_path: Path, raw_directory: Path
) -> go.Figure:
    """Load the preliminary model and derive the survey trajectories."""
    blocks = read_block_model_csv(block_model_path)
    raw_data = load_raw_data(raw_directory)
    trajectory = desurvey(raw_data["collar"], raw_data["survey"])
    return build_block_model_figure(blocks, trajectory)


def write_block_model_html(figure: go.Figure, output_path: Path) -> None:
    """Write a self-contained HTML visualization for offline local review."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(
        output_path,
        include_plotlyjs=True,
        full_html=True,
        auto_open=False,
    )

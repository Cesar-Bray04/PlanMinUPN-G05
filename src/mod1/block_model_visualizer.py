"""Create an auditable, interactive 3D view of the preliminary block model."""

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.mod1.desurvey import Trajectory, desurvey
from src.mod1.loader import load_raw_data
from src.mod1.topography import (
    TOPO_STATUS_VALUES,
    TopographySurface,
    read_topography_points,
    triangulate_topography,
)
from src.mod1.positioning import PositionedRow, position_intervals


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
TOPOGRAPHIC_FIELDS = ("topo_z_m", "topo_status")
GEOLOGICAL_FIELDS = (
    "lith_support_length_m",
    "lith_support_interval_count",
    "lith_support_interval_ids",
    "lith_assignment_reason",
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
        present_topographic_fields = set(TOPOGRAPHIC_FIELDS) & set(
            reader.fieldnames or ()
        )
        if present_topographic_fields and present_topographic_fields != set(
            TOPOGRAPHIC_FIELDS
        ):
            raise ValueError(
                "Block model CSV must include both topo_z_m and topo_status."
            )
        present_geological_fields = set(GEOLOGICAL_FIELDS) & set(
            reader.fieldnames or ()
        )
        if present_geological_fields and present_geological_fields != set(
            GEOLOGICAL_FIELDS
        ):
            raise ValueError("Block model CSV must include all geological support fields.")
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
        if present_geological_fields:
            try:
                support_length = float(row["lith_support_length_m"])
                support_count = int(row["lith_support_interval_count"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Block model CSV row {row_number}: invalid geological support values."
                ) from error
            if not math.isfinite(support_length) or support_length < 0 or support_count < 0:
                raise ValueError(
                    f"Block model CSV row {row_number}: geological support must be "
                    "finite and non-negative."
                )
            if status == "ASSIGNED" and (
                support_length <= 0
                or support_count == 0
                or not row["lith_support_interval_ids"]
                or row["lith_assignment_reason"] != "ASSIGNED"
                or code not in row["lith_support_codes"].split("|")
            ):
                raise ValueError(
                    f"Block model CSV row {row_number}: assigned lithology lacks "
                    "positive, traceable interval support."
                )
            if status == UNKNOWN_STATUS and row["lith_assignment_reason"] == "ASSIGNED":
                raise ValueError(
                    f"Block model CSV row {row_number}: unassigned block has "
                    "ASSIGNED reason."
                )
        has_topographic_fields = present_topographic_fields == set(TOPOGRAPHIC_FIELDS)
        if has_topographic_fields:
            try:
                topo_z = float(row["topo_z_m"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Block model CSV row {row_number}: topo_z_m must be numeric."
                ) from error
            if not math.isfinite(topo_z):
                raise ValueError(
                    f"Block model CSV row {row_number}: topo_z_m must be finite."
                )
            if row["topo_status"] not in TOPO_STATUS_VALUES:
                raise ValueError(
                    f"Block model CSV row {row_number}: unsupported topo_status "
                    f"{row['topo_status']!r}."
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
                    block.get("topo_z_m", "N/A"),
                    block.get("topo_status", "N/A"),
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
            "<br>Topografía Z: %{customdata[11]} m"
            "<br>Estado topográfico: %{customdata[12]}"
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

    _add_drillhole_traces(figure, trajectory)

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


def build_topographic_block_model_figure(
    blocks: list[dict[str, str]],
    trajectory: Trajectory,
    surface: TopographySurface,
) -> go.Figure:
    """Build a TIN and switchable block meshes for lithology or topographic state."""
    if any(
        not set(TOPOGRAPHIC_FIELDS).issubset(block)
        or block["topo_status"] not in TOPO_STATUS_VALUES
        for block in blocks
    ):
        raise ValueError("Every block must have valid topographic fields.")

    figure = go.Figure()
    figure.add_trace(
        go.Mesh3d(
            x=surface.points[:, 0],
            y=surface.points[:, 1],
            z=surface.points[:, 2],
            i=surface.simplices[:, 0],
            j=surface.simplices[:, 1],
            k=surface.simplices[:, 2],
            color="#8dbb72",
            opacity=0.45,
            name=f"Superficie topográfica ({len(surface.points):,} puntos)",
            legendgroup="topography",
            hovertemplate="Topografía<br>(X,Y,Z): (%{x:.2f}, %{y:.2f}, %{z:.2f}) m<extra></extra>",
        )
    )

    meshes: list[go.Mesh3d] = []
    lithology_visibility: list[bool | str] = []
    topography_visibility: list[bool | str] = []
    assigned_codes = sorted(
        {block["lith_code"].strip() for block in blocks if block["lith_status"] == "ASSIGNED"}
    )
    for code_index, code in enumerate(assigned_codes):
        category_blocks = [
            block
            for block in blocks
            if block["lith_status"] == "ASSIGNED" and block["lith_code"].strip() == code
        ]
        meshes.append(
            _cube_mesh(
                category_blocks,
                color=CATEGORY_COLORS[code_index % len(CATEGORY_COLORS)],
                opacity=0.95,
                name=f"Litología {code} ({len(category_blocks):,})",
                legendgroup=f"lith_code:{code}",
            )
        )
        lithology_visibility.append(True)
        topography_visibility.append(False)

    unknown_blocks = [block for block in blocks if block["lith_status"] == UNKNOWN_STATUS]
    if unknown_blocks:
        meshes.append(
            _cube_mesh(
                unknown_blocks,
                color=UNKNOWN_COLOR,
                opacity=0.12,
                name=f"Litología {UNKNOWN_STATUS} ({len(unknown_blocks):,})",
                legendgroup="lith_status:unknown",
                visible="legendonly",
            )
        )
        lithology_visibility.append("legendonly")
        topography_visibility.append(False)

    topo_colors = {"ROCK": "#8b5a2b", "AIR": "#d9e5f2", "PARTIAL": "#f0c341"}
    for status in ("ROCK", "AIR", "PARTIAL"):
        status_blocks = [block for block in blocks if block["topo_status"] == status]
        if not status_blocks:
            continue
        meshes.append(
            _cube_mesh(
                status_blocks,
                color=topo_colors[status],
                opacity=0.78,
                name=f"Estado topográfico {status} ({len(status_blocks):,})",
                legendgroup=f"topo_status:{status}",
                visible="legendonly",
            )
        )
        lithology_visibility.append(False)
        topography_visibility.append(True)

    for mesh in meshes:
        figure.add_trace(mesh)

    surface_trace_count = 1
    mesh_indices = list(range(surface_trace_count, surface_trace_count + len(meshes)))
    figure.update_layout(
        title=(
            "Modelo de bloques preliminar con topografía - vista 3D diagnóstica"
            "<br><sup>Clasificación por elevación interpolada en XY del centro; "
            "no constituye validación geológica</sup>"
        ),
        scene={
            "xaxis_title": "X (m)",
            "yaxis_title": "Y (m)",
            "zaxis_title": "Z (m)",
            "aspectmode": "data",
        },
        legend={
            "title": "Capas; cambiar color de bloques",
            "groupclick": "togglegroup",
            "itemsizing": "constant",
        },
        updatemenus=[
            {
                "type": "dropdown",
                "direction": "down",
                "x": 0.01,
                "y": 1.14,
                "buttons": [
                    {
                        "label": "Color por litología",
                        "method": "restyle",
                        "args": [{"visible": lithology_visibility}, mesh_indices],
                    },
                    {
                        "label": "Color por estado topográfico",
                        "method": "restyle",
                        "args": [{"visible": topography_visibility}, mesh_indices],
                    },
                ],
            }
        ],
        margin={"l": 0, "r": 0, "t": 110, "b": 0},
        meta={
            "topography_used": True,
            "validation_claim": False,
            "block_count": len(blocks),
            "assigned_codes": assigned_codes,
            "topography_point_count": len(surface.points),
            "topographic_statuses": sorted({block["topo_status"] for block in blocks}),
        },
    )
    _add_drillhole_traces(figure, trajectory)
    return figure


def _add_drillhole_traces(figure: go.Figure, trajectory: Trajectory) -> None:
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
                text=[f"{hole_id} — MD {point['md_m']:.2f} m" for point in stations],
                hovertemplate="%{text}<br>(X,Y,Z): (%{x:.2f}, %{y:.2f}, %{z:.2f}) m<extra></extra>",
            )
        )


def build_topographic_visualization_from_files(
    block_model_path: Path,
    raw_directory: Path,
    topography_path: Path,
) -> go.Figure:
    """Load the topography-enriched model, TIN, and M01 drillhole trajectories."""
    blocks = read_block_model_csv(block_model_path)
    surface = triangulate_topography(read_topography_points(topography_path))
    raw_data = load_raw_data(raw_directory)
    trajectory = desurvey(raw_data["collar"], raw_data["survey"])
    return build_topographic_block_model_figure(blocks, trajectory, surface)


def _interval_contacts(
    intervals: list[PositionedRow],
) -> list[tuple[float, float, float, float, str, str, str]]:
    by_hole: dict[str, list[PositionedRow]] = defaultdict(list)
    for interval in intervals:
        by_hole[str(interval["hole_id"])].append(interval)
    contacts: list[tuple[float, float, float, str, str, str]] = []
    for hole_id, rows in by_hole.items():
        ordered = sorted(rows, key=lambda row: float(row["from_m"]))
        for previous, current in zip(ordered, ordered[1:]):
            if (
                abs(float(previous["to_m"]) - float(current["from_m"])) <= 1e-8
                and previous["lith_code"] != current["lith_code"]
            ):
                contacts.append(
                    (
                        float(current["x_from"]),
                        float(current["y_from"]),
                        float(current["z_from"]),
                        float(current["from_m"]),
                        str(previous["lith_code"]),
                        str(current["lith_code"]),
                        hole_id,
                    )
                )
    return contacts


def _section_segment(
    segment: tuple[float, float, tuple[float, float, float], tuple[float, float, float]],
    y_min: float,
    y_max: float,
) -> tuple[float, float, float, float] | None:
    _, _, start, end = segment
    delta_y = end[1] - start[1]
    if delta_y == 0:
        if not y_min <= start[1] <= y_max:
            return None
        return start[0], start[2], end[0], end[2]
    first_t = max(0.0, min((y_min - start[1]) / delta_y, (y_max - start[1]) / delta_y))
    last_t = min(1.0, max((y_min - start[1]) / delta_y, (y_max - start[1]) / delta_y))
    if last_t <= first_t:
        return None
    first = tuple(a + first_t * (b - a) for a, b in zip(start, end))
    last = tuple(a + last_t * (b - a) for a, b in zip(start, end))
    return first[0], first[2], last[0], last[2]


def build_geological_topographic_block_model_figure(
    blocks: list[dict[str, str]],
    trajectory: Trajectory,
    surface: TopographySurface,
    lithology_intervals: list[PositionedRow],
    *,
    section_j: int | None = None,
) -> go.Figure:
    """Build integrated 3D and diagnostic vertical-section views."""
    base = build_topographic_block_model_figure(blocks, trajectory, surface)
    assigned_codes = sorted(
        {str(row["lith_code"]).strip() for row in lithology_intervals}
    )
    colors = {
        code: CATEGORY_COLORS[index % len(CATEGORY_COLORS)]
        for index, code in enumerate(assigned_codes)
    }
    interval_traces: list[go.Scatter3d] = []
    for code in assigned_codes:
        x_values: list[float | None] = []
        y_values: list[float | None] = []
        z_values: list[float | None] = []
        hover: list[str | None] = []
        for interval in lithology_intervals:
            if str(interval["lith_code"]).strip() != code:
                continue
            segments = interval.get("trajectory_segments", ())
            for segment in segments:
                _, _, start, end = segment
                x_values.extend((start[0], end[0], None))
                y_values.extend((start[1], end[1], None))
                z_values.extend((start[2], end[2], None))
                label = (
                    f"{interval['hole_id']} MD {interval['from_m']}-{interval['to_m']} m"
                )
                hover.extend((label, label, None))
        interval_traces.append(
            go.Scatter3d(
                x=x_values,
                y=y_values,
                z=z_values,
                mode="lines",
                line={"color": colors[code], "width": 5},
                name=f"Intervalos observados {code}",
                legendgroup=f"observed:{code}",
                text=hover,
                hovertemplate="%{text}<br>(X,Y,Z): (%{x:.2f}, %{y:.2f}, %{z:.2f}) m<extra></extra>",
            )
        )

    contacts = _interval_contacts(lithology_intervals)
    if contacts:
        interval_traces.append(
            go.Scatter3d(
                x=[contact[0] for contact in contacts],
                y=[contact[1] for contact in contacts],
                z=[contact[2] for contact in contacts],
                mode="markers",
                marker={"color": "#111111", "size": 4, "symbol": "diamond"},
                name=f"Contactos observados ({len(contacts)})",
                text=[
                    f"{contact[6]} MD {contact[3]:.3f} m: "
                    f"{contact[4]} → {contact[5]}"
                    for contact in contacts
                ],
                hovertemplate="%{text}<br>(X,Y,Z): (%{x:.2f}, %{y:.2f}, %{z:.2f}) m<extra></extra>",
            )
        )

    ny = max(int(block["j"]) for block in blocks) + 1
    selected_j = ny // 2 if section_j is None else section_j
    section_blocks = [block for block in blocks if int(block["j"]) == selected_j]
    if not section_blocks:
        raise ValueError(f"No blocks are available for Y section j={selected_j}.")
    y_min = min(float(block["y_min"]) for block in section_blocks)
    y_max = max(float(block["y_max"]) for block in section_blocks)

    section_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for block in section_blocks:
        code = (
            str(block["lith_code"]).strip()
            if block["lith_status"] == "ASSIGNED"
            else UNKNOWN_STATUS
        )
        section_groups[code].append(block)

    section_traces: list[go.Scatter] = []
    for code, category_blocks in sorted(section_groups.items()):
        x_values: list[float | None] = []
        z_values: list[float | None] = []
        line_color = colors.get(code, UNKNOWN_COLOR)
        for block in category_blocks:
            x0, x1 = float(block["x_min"]), float(block["x_max"])
            z0, z1 = float(block["z_min"]), float(block["z_max"])
            x_values.extend((x0, x1, x1, x0, x0, None))
            z_values.extend((z0, z0, z1, z1, z0, None))
        section_traces.append(
            go.Scatter(
                x=x_values,
                y=z_values,
                mode="lines",
                line={"color": line_color, "width": 1},
                name=f"Sección bloques {code} ({len(category_blocks)})",
                legendgroup=f"section:{code}",
                showlegend=False,
                hoverinfo="skip",
            )
        )

    interval_x: dict[str, list[float | None]] = defaultdict(list)
    interval_z: dict[str, list[float | None]] = defaultdict(list)
    for interval in lithology_intervals:
        code = str(interval["lith_code"]).strip() or UNKNOWN_STATUS
        for segment in interval.get("trajectory_segments", ()):
            clipped = _section_segment(segment, y_min, y_max)
            if clipped is None:
                continue
            x0, z0, x1, z1 = clipped
            interval_x[code].extend((x0, x1, None))
            interval_z[code].extend((z0, z1, None))
    for code, x_values in sorted(interval_x.items()):
        section_traces.append(
            go.Scatter(
                x=x_values,
                y=interval_z[code],
                mode="lines",
                line={"color": colors.get(code, UNKNOWN_COLOR), "width": 3},
                name=f"Intervalos observados {code}",
                showlegend=False,
                hoverinfo="skip",
            )
        )

    section_contacts = [
        contact for contact in contacts if y_min <= contact[1] <= y_max
    ]
    if section_contacts:
        section_traces.append(
            go.Scatter(
                x=[contact[0] for contact in section_contacts],
                y=[contact[2] for contact in section_contacts],
                mode="markers",
                marker={"color": "#111111", "size": 6, "symbol": "diamond"},
                name=f"Contactos ({len(section_contacts)})",
                showlegend=False,
                text=[
                    f"{contact[6]} MD {contact[3]:.3f} m: "
                    f"{contact[4]} → {contact[5]}"
                    for contact in section_contacts
                ],
                hovertemplate="%{text}<extra></extra>",
            )
        )
    topo_by_x: dict[float, float] = {}
    for block in section_blocks:
        topo_by_x[float(block["x_center"])] = float(block["topo_z_m"])
    section_traces.append(
        go.Scatter(
            x=sorted(topo_by_x),
            y=[topo_by_x[x] for x in sorted(topo_by_x)],
            mode="lines",
            line={"color": "#228833", "width": 2, "dash": "dash"},
            name="Topografía (centros XY)",
            showlegend=False,
            hovertemplate="X=%{x:.1f} m; topo_z=%{y:.2f} m<extra></extra>",
        )
    )

    figure = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "scene"}, {"type": "xy"}]],
        column_widths=[0.67, 0.33],
        subplot_titles=("3D integrado", f"Sección X-Z, j={selected_j}, Y={y_min:.1f}–{y_max:.1f} m"),
        horizontal_spacing=0.04,
    )
    for trace in base.data:
        figure.add_trace(trace, row=1, col=1)
    for trace in interval_traces:
        figure.add_trace(trace, row=1, col=1)
    for trace in section_traces:
        figure.add_trace(trace, row=1, col=2)
    figure.update_layout(base.layout.to_plotly_json())
    figure.update_layout(
        title=(
            "Geología observada + topografía — vistas diagnósticas"
            "<br><sup>Coherencia y trazabilidad de intervalos; no es interpretación "
            "profesional externa ni validación operacional</sup>"
        ),
        scene={"xaxis_title": "X (m)", "yaxis_title": "Y (m)", "zaxis_title": "Z (m)"},
        xaxis2={"title": "X (m)"},
        yaxis2={"title": "Z (m)"},
        meta={
            **dict(base.layout.meta),
            "observed_lithology_intervals": len(lithology_intervals),
            "observed_contacts": len(contacts),
            "section_j": selected_j,
            "section_y_min_m": y_min,
            "section_y_max_m": y_max,
            "geological_validation_scope": "observed interval/contact consistency only",
        },
    )
    return figure


def build_geological_topographic_visualization_from_files(
    block_model_path: Path,
    raw_directory: Path,
    topography_path: Path,
) -> go.Figure:
    """Load integrated blocks, raw observations, trajectories, and the TIN."""
    blocks = read_block_model_csv(block_model_path)
    surface = triangulate_topography(read_topography_points(topography_path))
    raw_data = load_raw_data(raw_directory)
    trajectory = desurvey(raw_data["collar"], raw_data["survey"])
    positioned = position_intervals(
        trajectory,
        {
            "assay": raw_data["assay"],
            "lithology": raw_data["lithology"],
            "alteration": raw_data["alteration"],
            "density": raw_data["density"],
        },
    )["lithology"]
    return build_geological_topographic_block_model_figure(
        blocks, trajectory, surface, positioned
    )


def write_block_model_html(figure: go.Figure, output_path: Path) -> None:
    """Write a self-contained HTML visualization for offline local review."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(
        output_path,
        include_plotlyjs=True,
        full_html=True,
        auto_open=False,
    )

import csv

import plotly.graph_objects as go
import pytest

from src.mod1.block_model_visualizer import (
    UNKNOWN_STATUS,
    build_block_model_figure,
    read_block_model_csv,
    write_block_model_html,
)


FIELDS = [
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
]


def block(i, lith_code, status, support=1, support_codes="POR", assay_support=2):
    return {
        "i": str(i),
        "j": "0",
        "k": "0",
        "x_min": str(i * 10),
        "y_min": "0",
        "z_min": "0",
        "x_max": str(i * 10 + 10),
        "y_max": "10",
        "z_max": "10",
        "x_center": str(i * 10 + 5),
        "y_center": "5",
        "z_center": "5",
        "lith_code": lith_code,
        "lith_status": status,
        "lith_support_count": str(support),
        "lith_support_codes": support_codes,
        "assay_composite_support_count": str(assay_support),
    }


def test_reads_preliminary_block_model_and_requires_a_complete_schema(tmp_path):
    csv_path = tmp_path / "model.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(block(0, "POR", "ASSIGNED"))
        writer.writerow(block(1, "", UNKNOWN_STATUS, support=0, support_codes=""))

    assert len(read_block_model_csv(csv_path)) == 2

    csv_path.write_text("i,j,k\n0,0,0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required fields"):
        read_block_model_csv(csv_path)


@pytest.mark.parametrize(
    ("row", "error"),
    [
        (block(0, "", "ASSIGNED"), "assigned block has no lith_code"),
        (block(0, "POR", UNKNOWN_STATUS), "unassigned block has a lith_code"),
    ],
)
def test_rejects_inconsistent_category_and_status(row, error, tmp_path):
    csv_path = tmp_path / "invalid.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(row)
    with pytest.raises(ValueError, match=error):
        read_block_model_csv(csv_path)


def test_figure_separates_categories_unknowns_and_drillhole_support():
    blocks = [
        block(0, "POR", "ASSIGNED", support_codes="POR"),
        block(1, "", UNKNOWN_STATUS, support=0, support_codes="", assay_support=0),
        block(2, "VOL", "ASSIGNED", support_codes="VOL"),
    ]
    trajectory = {
        "H-01": [
            {"hole_id": "H-01", "md_m": 0.0, "x": 1.0, "y": 2.0, "z": 3.0},
            {"hole_id": "H-01", "md_m": 10.0, "x": 1.0, "y": 2.0, "z": -7.0},
        ]
    }

    figure = build_block_model_figure(blocks, trajectory)

    meshes = [trace for trace in figure.data if isinstance(trace, go.Mesh3d)]
    drillholes = [trace for trace in figure.data if isinstance(trace, go.Scatter3d)]
    assert len(meshes) == 3
    assert {mesh.name for mesh in meshes} == {
        "lith_code POR (1)",
        f"{UNKNOWN_STATUS} (1)",
        "lith_code VOL (1)",
    }
    assert sum(len(mesh.i) // 12 for mesh in meshes) == len(blocks)
    unknown_mesh = next(mesh for mesh in meshes if UNKNOWN_STATUS in mesh.name)
    assert unknown_mesh.opacity == 0.12
    assert unknown_mesh.visible == "legendonly"
    assert all(mesh.legendgroup for mesh in meshes)
    assert len(drillholes) == 1
    assert drillholes[0].visible is None
    assert any("MD 10.00 m" in text for text in drillholes[0].text)
    assert figure.layout.meta["topography_used"] is False
    assert figure.layout.meta["validation_claim"] is False
    assert "no constituye validacion geologica ni topografica" in figure.layout.title.text
    for mesh in meshes:
        assert "lith_support_count" in mesh.hovertemplate or "Soporte litológico" in mesh.hovertemplate
        assert "Composites soporte assay" in mesh.hovertemplate


def test_writes_self_contained_html_with_auditable_controls(tmp_path):
    figure = build_block_model_figure(
        [block(0, "OVB", "ASSIGNED")],
        {
            "H-01": [
                {"hole_id": "H-01", "md_m": 0.0, "x": 0, "y": 0, "z": 0},
                {"hole_id": "H-01", "md_m": 1.0, "x": 0, "y": 0, "z": -1},
            ]
        },
    )
    output = tmp_path / "figure.html"

    write_block_model_html(figure, output)

    html = output.read_text(encoding="utf-8")
    assert "plotly.js" in html
    assert "lith_code OVB (1)" in html
    assert UNKNOWN_STATUS not in html
    assert "legend" in html.lower()
    assert "no constituye validacion geologica ni topografica" in html

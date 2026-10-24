import csv

import pytest

from src.mod1.block_model import (
    GEOLOGICAL_BLOCK_COLUMNS,
    build_geological_block_model,
    write_geological_block_model_csv,
)
from src.mod1.positioning import position_intervals


def interval(
    hole_id,
    start_md,
    end_md,
    start_xyz,
    end_xyz,
    code="POR",
):
    return {
        "hole_id": hole_id,
        "from_m": start_md,
        "to_m": end_md,
        "lith_code": code,
        "trajectory_segments": (
            (start_md, end_md, start_xyz, end_xyz),
        ),
    }


def test_interval_intersection_supports_every_crossed_block_and_traces_source_ids():
    blocks, coverage = build_geological_block_model(
        [interval("H-01", 0, 18, (1, 5, 5), (19, 5, 5))],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(2, 1, 1),
    )

    supported = [block for block in blocks if block["lith_support_count"]]
    assert [block["i"] for block in supported] == [0, 1]
    assert [block["lith_support_length_m"] for block in supported] == pytest.approx(
        [9, 9]
    )
    assert all(block["lith_code"] == "POR" for block in supported)
    assert all("H-01:0.000000000-18.000000000" in block["lith_support_interval_ids"] for block in supported)
    assert coverage[0]["inside_length_m"] == pytest.approx(18)
    assert coverage[0]["outside_length_m"] == pytest.approx(0)


def test_observed_interval_is_fully_accounted_inside_and_outside_the_grid():
    _, coverage = build_geological_block_model(
        [interval("H-02", 0, 20, (-5, 5, 5), (15, 5, 5))],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 1),
    )

    assert coverage[0]["observed_length_m"] == pytest.approx(20)
    assert coverage[0]["inside_length_m"] == pytest.approx(10)
    assert coverage[0]["outside_length_m"] == pytest.approx(10)
    assert coverage[0]["inside_length_m"] + coverage[0]["outside_length_m"] == pytest.approx(
        coverage[0]["observed_length_m"]
    )


def test_conflicts_and_empty_codes_stay_unknown_without_majority_assignment():
    positioned = [
        interval("H-01", 0, 2, (1, 1, 1), (3, 1, 1), "POR"),
        interval("H-02", 0, 2, (4, 1, 1), (6, 1, 1), "POR"),
        interval("H-03", 0, 2, (7, 1, 1), (9, 1, 1), "BRX"),
        interval("H-04", 0, 2, (11, 1, 1), (13, 1, 1), "VOL"),
        interval("H-05", 0, 2, (14, 1, 1), (16, 1, 1), ""),
    ]

    blocks, _ = build_geological_block_model(
        positioned,
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(2, 1, 1),
    )

    assert blocks[0]["lith_status"] == "UNKNOWN/UNASSIGNED"
    assert blocks[0]["lith_assignment_reason"] == "CODE_CONFLICT"
    assert blocks[0]["lith_support_codes"] == "BRX|POR"
    assert blocks[0]["lith_code"] == ""
    assert blocks[1]["lith_status"] == "UNKNOWN/UNASSIGNED"
    assert blocks[1]["lith_assignment_reason"] == "EMPTY_CODE"
    assert blocks[1]["lith_code"] == ""


def test_no_code_is_propagated_to_neighbor_without_observed_intersection():
    blocks, _ = build_geological_block_model(
        [interval("H-01", 0, 2, (1, 1, 1), (3, 1, 1), "AIR")],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(2, 1, 1),
    )

    assert blocks[0]["lith_code"] == "AIR"
    assert blocks[0]["lith_support_length_m"] > 0
    assert blocks[1]["lith_status"] == "UNKNOWN/UNASSIGNED"
    assert blocks[1]["lith_assignment_reason"] == "NO_LITHOLOGY_SUPPORT"


def test_zero_measure_contact_does_not_create_support_or_break_accounting():
    blocks, coverage = build_geological_block_model(
        [interval("H-01", 0, 20, (0, 0, 0), (10, 10, 10))],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(5, 5, 5),
        shape=(2, 2, 2),
    )

    supported = [block for block in blocks if block["lith_support_length_m"] > 0]
    assert len(supported) == 2
    assert sum(block["lith_support_length_m"] for block in supported) == pytest.approx(20)
    assert coverage[0]["inside_length_m"] == pytest.approx(20)


def test_positioning_retains_each_trajectory_piece_for_contact_and_turn_geometry():
    trajectory = {
        "H-01": [
            {"hole_id": "H-01", "md_m": 0.0, "x": 1.0, "y": 1.0, "z": 10.0},
            {"hole_id": "H-01", "md_m": 5.0, "x": 6.0, "y": 1.0, "z": 10.0},
            {"hole_id": "H-01", "md_m": 10.0, "x": 6.0, "y": 6.0, "z": 10.0},
        ]
    }
    intervals = {
        "assay": [],
        "lithology": [
            {"hole_id": "H-01", "from_m": "2", "to_m": "8", "lith_code": "POR"}
        ],
        "alteration": [],
        "density": [],
    }

    positioned = position_intervals(trajectory, intervals)["lithology"][0]

    assert len(positioned["trajectory_segments"]) == 2
    assert positioned["trajectory_segments"][0][0:2] == (2.0, 5.0)
    assert positioned["trajectory_segments"][1][0:2] == (5.0, 8.0)
    assert positioned["trajectory_segments"][0][3] == positioned["trajectory_segments"][1][2]


def test_csv_records_only_traceable_geological_support(tmp_path):
    blocks, _ = build_geological_block_model(
        [interval("H-01", 0, 2, (1, 1, 1), (3, 1, 1), "POR")],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 1),
    )
    output = tmp_path / "geology.csv"

    write_geological_block_model_csv(blocks, output)

    with output.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        assert tuple(reader.fieldnames) == GEOLOGICAL_BLOCK_COLUMNS
        row = next(reader)
    assert float(row["lith_support_length_m"]) > 0
    assert row["lith_support_interval_count"] == "1"
    assert row["lith_support_interval_ids"] == "H-01:0.000000000-2.000000000"
    assert row["lith_assignment_reason"] == "ASSIGNED"

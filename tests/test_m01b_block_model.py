import csv

import pytest

from src.mod1.block_model import (
    build_block_model,
    build_preliminary_block_model,
    write_block_model_csv,
)
from src.mod1.loader import RawData


def positioned(x, y, z, lith_code="POR"):
    return {"x_mid": x, "y_mid": y, "z_mid": z, "lith_code": lith_code}


def test_builds_complete_grid_and_assigns_only_a_single_observed_code():
    blocks = build_block_model(
        [positioned(1, 1, 1, "OVB"), positioned(2, 2, 2, "OVB")],
        [positioned(1, 1, 1)],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(2, 1, 1),
    )

    assert len(blocks) == 2
    assert blocks[0]["lith_code"] == "OVB"
    assert blocks[0]["lith_status"] == "ASSIGNED"
    assert blocks[0]["lith_support_count"] == 2
    assert blocks[0]["lith_support_codes"] == "OVB"
    assert blocks[0]["assay_composite_support_count"] == 1
    assert blocks[0]["x_center"] == 5
    assert blocks[1]["lith_code"] == ""
    assert blocks[1]["lith_status"] == "UNKNOWN/UNASSIGNED"
    assert blocks[1]["assay_composite_support_count"] == 0


def test_conflicting_codes_remain_unassigned_even_when_one_code_is_majority():
    blocks = build_block_model(
        [
            positioned(1, 1, 1, "POR"),
            positioned(2, 2, 2, "POR"),
            positioned(3, 3, 3, "BRX"),
        ],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 1),
    )

    assert blocks[0]["lith_code"] == ""
    assert blocks[0]["lith_status"] == "UNKNOWN/UNASSIGNED"
    assert blocks[0]["lith_support_codes"] == "BRX|POR"


def test_empty_lithology_code_makes_cell_unassigned():
    blocks = build_block_model(
        [positioned(1, 1, 1, "POR"), positioned(2, 2, 2, " ")],
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 1),
    )

    assert blocks[0]["lith_code"] == ""
    assert blocks[0]["lith_status"] == "UNKNOWN/UNASSIGNED"
    assert blocks[0]["lith_support_count"] == 2
    assert blocks[0]["lith_support_codes"] == "POR"


def test_composites_only_change_assay_support_count_not_lithology_assignment():
    lithology = [positioned(1, 1, 1, "VOL")]
    without_composites = build_block_model(
        lithology,
        [],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 1),
    )[0]
    with_composites = build_block_model(
        lithology,
        [positioned(1, 1, 1), positioned(2, 2, 2)],
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 1),
    )[0]

    assert with_composites["lith_code"] == without_composites["lith_code"] == "VOL"
    assert with_composites["lith_support_count"] == without_composites["lith_support_count"] == 1
    assert with_composites["assay_composite_support_count"] == 2


def test_rejects_observation_midpoint_outside_grid():
    with pytest.raises(ValueError, match="outside grid"):
        build_block_model(
            [positioned(10, 1, 1)],
            [],
            origin_m=(0, 0, 0),
            block_size_m=(10, 10, 10),
            shape=(1, 1, 1),
        )


def test_preliminary_workflow_positions_lithology_and_writes_csv(tmp_path):
    raw_data: RawData = {
        "collar": [
            {
                "hole_id": "H-01",
                "x": "5",
                "y": "5",
                "z": "20",
                "final_depth_m": "10",
                "azimuth_deg": "0",
                "dip_deg": "-90",
            }
        ],
        "survey": [
            {
                "hole_id": "H-01",
                "depth_m": "0",
                "azimuth_deg": "0",
                "dip_deg": "-90",
            },
            {
                "hole_id": "H-01",
                "depth_m": "10",
                "azimuth_deg": "0",
                "dip_deg": "-90",
            },
        ],
        "assay": [],
        "lithology": [
            {
                "hole_id": "H-01",
                "from_m": "0",
                "to_m": "2",
                "length_m": "2",
                "lith_code": "AIR",
            },
            {
                "hole_id": "H-01",
                "from_m": "2",
                "to_m": "4",
                "length_m": "2",
                "lith_code": "AIR",
            },
        ],
        "alteration": [],
        "density": [],
        "data_dictionary": [],
        "release_manifest": {},
    }
    composites = [positioned(5, 5, 18, "BRX")]
    blocks = build_preliminary_block_model(
        raw_data,
        composites,
        origin_m=(0, 0, 0),
        block_size_m=(10, 10, 10),
        shape=(1, 1, 2),
    )
    output = tmp_path / "block_model.csv"
    write_block_model_csv(blocks, output)

    assert len(blocks) == 2
    supported = next(block for block in blocks if block["lith_support_count"])
    assert supported["lith_code"] == "AIR"
    assert supported["lith_status"] == "ASSIGNED"
    assert supported["assay_composite_support_count"] == 1
    with output.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == 2
    assert rows[0]["lith_status"] == "UNKNOWN/UNASSIGNED"

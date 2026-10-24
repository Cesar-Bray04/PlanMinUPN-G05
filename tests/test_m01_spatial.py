import math

import pytest

from src.mod1.desurvey import desurvey
from src.mod1.positioning import position_intervals
from src.mod1.validator import validate_data


def empty_raw_data():
    return {
        "collar": [],
        "survey": [],
        "assay": [],
        "lithology": [],
        "alteration": [],
        "density": [],
        "data_dictionary": [],
        "release_manifest": {},
    }


def test_validator_reports_interval_and_assay_errors_without_changing_input():
    raw_data = empty_raw_data()
    raw_data["collar"] = [
        {
            "hole_id": "H-01",
            "x": "0",
            "y": "0",
            "z": "100",
            "final_depth_m": "10",
            "azimuth_deg": "0",
            "dip_deg": "-90",
        }
    ]
    raw_data["survey"] = [
        {
            "hole_id": "H-01",
            "depth_m": "0",
            "azimuth_deg": "0",
            "dip_deg": "-90",
        }
    ]
    raw_data["assay"] = [
        {
            "hole_id": "H-01",
            "from_m": "1",
            "to_m": "3",
            "length_m": "2",
            "cu_pct": "-0.1",
            "mo_pct": "0",
            "au_gt": "0",
        }
    ]

    result = validate_data(raw_data)

    assert result["data"] is raw_data
    assert {finding["rule_id"] for finding in result["findings"]} >= {
        "ASSAY-02",
        "ASSAY-03",
        "DENS-03",
        "REL-04",
    }
    assert all(finding["severity"] != "ERROR" for finding in result["findings"] if finding["rule_id"] != "ASSAY-02")


def test_validator_flags_interval_beyond_collar_depth_and_duplicate_density_id():
    raw_data = empty_raw_data()
    raw_data["collar"] = [
        {
            "hole_id": "H-01",
            "x": "0",
            "y": "0",
            "z": "100",
            "final_depth_m": "10",
            "azimuth_deg": "0",
            "dip_deg": "-90",
        }
    ]
    raw_data["survey"] = [
        {
            "hole_id": "H-01",
            "depth_m": "0",
            "azimuth_deg": "0",
            "dip_deg": "-90",
        }
    ]
    raw_data["lithology"] = [
        {
            "hole_id": "H-01",
            "from_m": "8",
            "to_m": "11",
            "length_m": "3",
        }
    ]
    raw_data["density"] = [
        {
            "hole_id": "H-01",
            "density_sample_id": "D-01",
            "density_t_m3": "2.6",
        },
        {
            "hole_id": "H-01",
            "density_sample_id": "D-01",
            "density_t_m3": "2.7",
        },
    ]

    findings = validate_data(raw_data)["findings"]

    assert {finding["rule_id"] for finding in findings} >= {"INT-04", "DENS-02"}
    assert all(
        finding["severity"] == "ERROR"
        for finding in findings
        if finding["rule_id"] in {"INT-04", "DENS-02"}
    )


def test_desurvey_preserves_collar_and_calculates_straight_northward_trajectory():
    collar = [
        {"hole_id": "H-01", "x": "100", "y": "200", "z": "300"},
    ]
    survey = [
        {"hole_id": "H-01", "depth_m": "0", "azimuth_deg": "0", "dip_deg": "0"},
        {"hole_id": "H-01", "depth_m": "10", "azimuth_deg": "0", "dip_deg": "0"},
    ]

    trajectory = desurvey(collar, survey)["H-01"]

    assert trajectory[0] == {
        "hole_id": "H-01",
        "md_m": 0.0,
        "x": 100.0,
        "y": 200.0,
        "z": 300.0,
    }
    assert trajectory[1]["x"] == pytest.approx(100.0)
    assert trajectory[1]["y"] == pytest.approx(210.0)
    assert trajectory[1]["z"] == pytest.approx(300.0)


def test_desurvey_rejects_duplicate_survey_depth():
    collar = [
        {"hole_id": "H-01", "x": "0", "y": "0", "z": "100"},
    ]
    survey = [
        {"hole_id": "H-01", "depth_m": "0", "azimuth_deg": "0", "dip_deg": "-90"},
        {"hole_id": "H-01", "depth_m": "0", "azimuth_deg": "0", "dip_deg": "-90"},
    ]

    with pytest.raises(ValueError, match="strictly increasing"):
        desurvey(collar, survey)


def test_positioning_linearly_interpolates_interval_boundaries_and_midpoint():
    trajectory = {
        "H-01": [
            {"hole_id": "H-01", "md_m": 0.0, "x": 0.0, "y": 0.0, "z": 100.0},
            {"hole_id": "H-01", "md_m": 10.0, "x": 0.0, "y": 10.0, "z": 90.0},
        ]
    }
    intervals = {
        "assay": [
            {
                "hole_id": "H-01",
                "from_m": "2",
                "to_m": "8",
                "length_m": "6",
                "cu_pct": "0.4",
            }
        ],
        "lithology": [],
        "alteration": [],
        "density": [],
    }

    positioned = position_intervals(trajectory, intervals)
    assay = positioned["assay"][0]

    assert assay["mid_m"] == pytest.approx(5.0)
    assert (assay["x_from"], assay["y_from"], assay["z_from"]) == pytest.approx(
        (0.0, 2.0, 98.0)
    )
    assert (assay["x_mid"], assay["y_mid"], assay["z_mid"]) == pytest.approx(
        (0.0, 5.0, 95.0)
    )
    assert (assay["x_to"], assay["y_to"], assay["z_to"]) == pytest.approx(
        (0.0, 8.0, 92.0)
    )
    assert all(math.isfinite(float(assay[field])) for field in ("x_mid", "y_mid", "z_mid"))
    assert positioned["lithology"] == []
    assert positioned["alteration"] == []
    assert positioned["density"] == []


def test_positioning_rejects_interval_outside_trajectory():
    trajectory = {
        "H-01": [
            {"hole_id": "H-01", "md_m": 0.0, "x": 0.0, "y": 0.0, "z": 100.0},
            {"hole_id": "H-01", "md_m": 10.0, "x": 0.0, "y": 10.0, "z": 90.0},
        ]
    }
    intervals = {
        "assay": [
            {"hole_id": "H-01", "from_m": "2", "to_m": "12", "length_m": "10"}
        ],
        "lithology": [],
        "alteration": [],
        "density": [],
    }

    with pytest.raises(ValueError, match="outside trajectory range"):
        position_intervals(trajectory, intervals)

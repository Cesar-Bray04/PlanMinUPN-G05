import csv
import json

from src.mod1.loader import RAW_TABLE_FILES, load_raw_data


def test_load_raw_data_reads_expected_tables_without_changing_sources(tmp_path):
    for filename in RAW_TABLE_FILES.values():
        with (tmp_path / filename).open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["hole_id", "value"])
            writer.writeheader()
            writer.writerow({"hole_id": "H-01", "value": "1"})

    manifest = {"files": list(RAW_TABLE_FILES.values()), "release_id": "test"}
    (tmp_path / "release_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    loaded_data = load_raw_data(tmp_path)

    assert set(loaded_data) == {*RAW_TABLE_FILES, "release_manifest"}
    assert loaded_data["collar"] == [{"hole_id": "H-01", "value": "1"}]
    assert loaded_data["alteration"] == [{"hole_id": "H-01", "value": "1"}]
    assert loaded_data["release_manifest"] == manifest
    assert (tmp_path / "collar.csv").read_text(encoding="utf-8").splitlines() == [
        "hole_id,value",
        "H-01,1",
    ]


def test_load_raw_data_accepts_empty_alteration_table(tmp_path):
    for filename in RAW_TABLE_FILES.values():
        (tmp_path / filename).write_text("hole_id,value\n", encoding="utf-8")
    (tmp_path / "release_manifest.json").write_text("{}", encoding="utf-8")

    loaded_data = load_raw_data(tmp_path)

    assert loaded_data["alteration"] == []

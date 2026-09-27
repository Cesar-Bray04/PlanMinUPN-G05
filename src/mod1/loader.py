"""Read the immutable raw CSV tables into memory."""

import csv
import json
from pathlib import Path
from typing import TypedDict


RAW_TABLE_FILES = {
    "collar": "collar.csv",
    "survey": "survey.csv",
    "assay": "assay.csv",
    "lithology": "lithology.csv",
    "alteration": "alteration.csv",
    "density": "density.csv",
    "data_dictionary": "data_dictionary.csv",
}

CsvRow = dict[str, str]


class IntervalData(TypedDict):
    """Raw interval observations consumed by interval positioning."""

    assay: list[CsvRow]
    lithology: list[CsvRow]
    alteration: list[CsvRow]
    density: list[CsvRow]


class RawData(TypedDict):
    """Raw observations and release metadata loaded for the desurvey workflow."""

    collar: list[CsvRow]
    survey: list[CsvRow]
    assay: list[CsvRow]
    lithology: list[CsvRow]
    alteration: list[CsvRow]
    density: list[CsvRow]
    data_dictionary: list[CsvRow]
    release_manifest: dict[str, object]


def load_raw_data(raw_directory: Path) -> RawData:
    """Load all raw dataset tables and release metadata without modifying sources."""
    tables: dict[str, object] = {}
    for table_name, filename in RAW_TABLE_FILES.items():
        file_path = raw_directory / filename
        with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            tables[table_name] = list(csv.DictReader(csv_file))

    manifest_path = raw_directory / "release_manifest.json"
    with manifest_path.open("r", encoding="utf-8") as manifest_file:
        tables["release_manifest"] = json.load(manifest_file)

    return RawData(**tables)

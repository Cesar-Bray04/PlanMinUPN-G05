"""Validate raw desurvey inputs using the approved M01 validation contract."""

import math
from typing import Literal, TypedDict

from src.mod1.loader import CsvRow, RawData


Severity = Literal["ERROR", "WARNING", "INFO"]


class Finding(TypedDict):
    """A traceable validation result; row_number is 1-based data-row numbering."""

    rule_id: str
    severity: Severity
    source_file: str
    row_number: int | None
    hole_id: str | None
    field: str | None
    observed_value: object
    message: str


class ValidationResult(TypedDict):
    """The original input plus findings, without modifying the input tables."""

    data: RawData
    findings: list[Finding]


INTERVAL_TABLES = ("lithology", "assay", "density", "alteration")
METADATA_TABLES = ("collar", "survey", "lithology", "alteration", "assay", "density")


def _numeric_value(row: CsvRow, field: str) -> float | None:
    """Return a finite numeric value, or None when the field is invalid."""
    raw_value = row.get(field)
    if raw_value is None or not raw_value.strip():
        return None
    try:
        value = float(raw_value)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _add_finding(
    findings: list[Finding],
    *,
    rule_id: str,
    severity: Severity,
    source_file: str,
    message: str,
    row_number: int | None = None,
    hole_id: str | None = None,
    field: str | None = None,
    observed_value: object = None,
) -> None:
    findings.append(
        {
            "rule_id": rule_id,
            "severity": severity,
            "source_file": source_file,
            "row_number": row_number,
            "hole_id": hole_id,
            "field": field,
            "observed_value": observed_value,
            "message": message,
        }
    )


def _check_numeric_fields(
    findings: list[Finding],
    table_name: str,
    rows: list[CsvRow],
    fields: tuple[str, ...],
    rule_id: str,
    message: str,
) -> None:
    for row_number, row in enumerate(rows, start=1):
        for field in fields:
            if _numeric_value(row, field) is None:
                _add_finding(
                    findings,
                    rule_id=rule_id,
                    severity="ERROR",
                    source_file=f"{table_name}.csv",
                    row_number=row_number,
                    hole_id=row.get("hole_id") or None,
                    field=field,
                    observed_value=row.get(field),
                    message=message,
                )


def validate_data(raw_data: RawData) -> ValidationResult:
    """Return findings for approved rules while preserving the RawData object."""
    findings: list[Finding] = []
    collars = raw_data["collar"]
    collar_by_hole: dict[str, CsvRow] = {}

    # Collar identifiers, coordinates, final depths, and initial orientations.
    for row_number, row in enumerate(collars, start=1):
        hole_id = row.get("hole_id", "")
        if not hole_id.strip():
            _add_finding(
                findings,
                rule_id="COL-02",
                severity="ERROR",
                source_file="collar.csv",
                row_number=row_number,
                field="hole_id",
                observed_value=hole_id,
                message="hole_id no puede estar vacío ni contener solo espacios.",
            )
        elif hole_id in collar_by_hole:
            _add_finding(
                findings,
                rule_id="COL-01",
                severity="ERROR",
                source_file="collar.csv",
                row_number=row_number,
                hole_id=hole_id,
                field="hole_id",
                observed_value=hole_id,
                message="hole_id está duplicado en collar.",
            )
        else:
            collar_by_hole[hole_id] = row

    _check_numeric_fields(
        findings,
        "collar",
        collars,
        ("x", "y", "z"),
        "COL-03",
        "La coordenada debe ser numérica y finita.",
    )
    for row_number, row in enumerate(collars, start=1):
        final_depth = _numeric_value(row, "final_depth_m")
        if final_depth is None or final_depth <= 0:
            _add_finding(
                findings,
                rule_id="COL-04",
                severity="ERROR",
                source_file="collar.csv",
                row_number=row_number,
                hole_id=row.get("hole_id") or None,
                field="final_depth_m",
                observed_value=row.get("final_depth_m"),
                message="final_depth_m debe ser numérico, finito y mayor que cero.",
            )
    _check_numeric_fields(
        findings,
        "collar",
        collars,
        ("azimuth_deg", "dip_deg"),
        "COL-05",
        "La orientación inicial debe ser numérica y finita.",
    )

    # Survey identity, ordering, measured depths, and numeric orientations.
    survey_rows = raw_data["survey"]
    survey_holes: set[str] = set()
    previous_depth_by_hole: dict[str, float] = {}
    seen_survey_stations: set[tuple[str, float]] = set()
    for row_number, row in enumerate(survey_rows, start=1):
        hole_id = row.get("hole_id", "")
        if hole_id not in collar_by_hole:
            _add_finding(
                findings,
                rule_id="SUR-01",
                severity="ERROR",
                source_file="survey.csv",
                row_number=row_number,
                hole_id=hole_id or None,
                field="hole_id",
                observed_value=hole_id,
                message="El hole_id de survey no existe en collar.",
            )
        else:
            survey_holes.add(hole_id)

        depth = _numeric_value(row, "depth_m")
        if depth is None or depth < 0:
            _add_finding(
                findings,
                rule_id="SUR-03",
                severity="ERROR",
                source_file="survey.csv",
                row_number=row_number,
                hole_id=hole_id or None,
                field="depth_m",
                observed_value=row.get("depth_m"),
                message="depth_m debe ser numérica, finita y no negativa.",
            )
        else:
            previous_depth = previous_depth_by_hole.get(hole_id)
            if previous_depth is not None and depth < previous_depth:
                _add_finding(
                    findings,
                    rule_id="SUR-04",
                    severity="ERROR",
                    source_file="survey.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="depth_m",
                    observed_value=row.get("depth_m"),
                    message="Las estaciones de survey no están ordenadas ascendentemente.",
                )
            previous_depth_by_hole[hole_id] = depth

            station_key = (hole_id, depth)
            if station_key in seen_survey_stations:
                _add_finding(
                    findings,
                    rule_id="SUR-06",
                    severity="ERROR",
                    source_file="survey.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="depth_m",
                    observed_value=row.get("depth_m"),
                    message="La combinación hole_id + depth_m está duplicada.",
                )
            else:
                seen_survey_stations.add(station_key)

            collar = collar_by_hole.get(hole_id)
            collar_depth = _numeric_value(collar, "final_depth_m") if collar else None
            if collar_depth is not None and depth > collar_depth:
                _add_finding(
                    findings,
                    rule_id="SUR-05",
                    severity="ERROR",
                    source_file="survey.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="depth_m",
                    observed_value=row.get("depth_m"),
                    message="La estación excede final_depth_m del collar.",
                )

    for row_number, row in enumerate(collars, start=1):
        hole_id = row.get("hole_id", "")
        if hole_id.strip() and hole_id not in survey_holes:
            _add_finding(
                findings,
                rule_id="SUR-02",
                severity="ERROR",
                source_file="collar.csv",
                row_number=row_number,
                hole_id=hole_id,
                field="hole_id",
                observed_value=hole_id,
                message="El collar no tiene ninguna medición de survey.",
            )

    _check_numeric_fields(
        findings,
        "survey",
        survey_rows,
        ("azimuth_deg", "dip_deg"),
        "SUR-08",
        "La orientación de survey debe ser numérica y finita.",
    )

    # Common measured-depth interval controls, including alteration if populated.
    for table_name in INTERVAL_TABLES:
        rows = raw_data[table_name]
        for row_number, row in enumerate(rows, start=1):
            hole_id = row.get("hole_id", "")
            if hole_id not in collar_by_hole:
                _add_finding(
                    findings,
                    rule_id="INT-01",
                    severity="ERROR",
                    source_file=f"{table_name}.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="hole_id",
                    observed_value=hole_id,
                    message="El hole_id del intervalo no existe en collar.",
                )

            numeric_fields = {
                field: _numeric_value(row, field)
                for field in ("from_m", "to_m", "length_m")
            }
            for field, value in numeric_fields.items():
                if value is None:
                    _add_finding(
                        findings,
                        rule_id="INT-02",
                        severity="ERROR",
                        source_file=f"{table_name}.csv",
                        row_number=row_number,
                        hole_id=hole_id or None,
                        field=field,
                        observed_value=row.get(field),
                        message="from_m, to_m y length_m deben ser numéricos y finitos.",
                    )

            start = numeric_fields["from_m"]
            end = numeric_fields["to_m"]
            if start is not None and end is not None and start >= end:
                _add_finding(
                    findings,
                    rule_id="INT-03",
                    severity="ERROR",
                    source_file=f"{table_name}.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="from_m/to_m",
                    observed_value={"from_m": row.get("from_m"), "to_m": row.get("to_m")},
                    message="El intervalo debe cumplir from_m < to_m.",
                )

            collar = collar_by_hole.get(hole_id)
            collar_depth = _numeric_value(collar, "final_depth_m") if collar else None
            outside = (start is not None and start < 0) or (
                end is not None and collar_depth is not None and end > collar_depth
            )
            if outside:
                _add_finding(
                    findings,
                    rule_id="INT-04",
                    severity="ERROR",
                    source_file=f"{table_name}.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="from_m/to_m",
                    observed_value={"from_m": row.get("from_m"), "to_m": row.get("to_m")},
                    message="El intervalo debe quedar dentro de [0, final_depth_m].",
                )

    # Assay values and summarized zero counts.
    assay_rows = raw_data["assay"]
    _check_numeric_fields(
        findings,
        "assay",
        assay_rows,
        ("cu_pct", "mo_pct", "au_gt"),
        "ASSAY-01",
        "La ley debe ser numérica y finita.",
    )
    for row_number, row in enumerate(assay_rows, start=1):
        for field in ("cu_pct", "mo_pct", "au_gt"):
            value = _numeric_value(row, field)
            if value is not None and value < 0:
                _add_finding(
                    findings,
                    rule_id="ASSAY-02",
                    severity="ERROR",
                    source_file="assay.csv",
                    row_number=row_number,
                    hole_id=row.get("hole_id") or None,
                    field=field,
                    observed_value=row.get(field),
                    message="La ley no puede ser negativa.",
                )

    for field in ("mo_pct", "au_gt"):
        zero_count = sum(
            _numeric_value(row, field) == 0 for row in assay_rows
        )
        _add_finding(
            findings,
            rule_id="ASSAY-03",
            severity="INFO",
            source_file="assay.csv",
            field=field,
            observed_value={"zero_count": zero_count, "row_count": len(assay_rows)},
            message="Conteo resumido de ceros; su significado no se interpreta.",
        )

    # Density values and unique sample identifiers.
    density_rows = raw_data["density"]
    seen_density_ids: set[str] = set()
    density_counts: dict[str, int] = {}
    for row_number, row in enumerate(density_rows, start=1):
        hole_id = row.get("hole_id", "")
        sample_id = row.get("density_sample_id", "")
        if sample_id.strip():
            if sample_id in seen_density_ids:
                _add_finding(
                    findings,
                    rule_id="DENS-02",
                    severity="ERROR",
                    source_file="density.csv",
                    row_number=row_number,
                    hole_id=hole_id or None,
                    field="density_sample_id",
                    observed_value=sample_id,
                    message="density_sample_id está duplicado.",
                )
            else:
                seen_density_ids.add(sample_id)
        if hole_id.strip():
            density_counts[hole_id] = density_counts.get(hole_id, 0) + 1

        density_value = _numeric_value(row, "density_t_m3")
        if density_value is None or density_value <= 0:
            _add_finding(
                findings,
                rule_id="DENS-01",
                severity="ERROR",
                source_file="density.csv",
                row_number=row_number,
                hole_id=hole_id or None,
                field="density_t_m3",
                observed_value=row.get("density_t_m3"),
                message="density_t_m3 debe ser numérica, finita y mayor que cero.",
            )

    _add_finding(
        findings,
        rule_id="DENS-03",
        severity="INFO",
        source_file="density.csv",
        observed_value={
            "samples_by_hole": density_counts,
            "sample_count": len(density_rows),
        },
        message="Resumen de cobertura observada de muestras de densidad por sondaje.",
    )

    # Compare table metadata with the release manifest; do not normalize values.
    manifest = raw_data["release_manifest"]
    expected_metadata = {
        "dataset_id": manifest.get("dataset_id"),
        "project_id": manifest.get("project_id"),
    }
    for table_name in METADATA_TABLES:
        for row_number, row in enumerate(raw_data[table_name], start=1):
            hole_id = row.get("hole_id") or None
            for field, expected_value in expected_metadata.items():
                observed_value = row.get(field)
                if expected_value is not None and observed_value != expected_value:
                    _add_finding(
                        findings,
                        rule_id="REL-02",
                        severity="ERROR",
                        source_file=f"{table_name}.csv",
                        row_number=row_number,
                        hole_id=hole_id,
                        field=field,
                        observed_value=observed_value,
                        message=f"{field} no coincide con el manifest del release.",
                    )

    if not raw_data["alteration"]:
        _add_finding(
            findings,
            rule_id="REL-04",
            severity="INFO",
            source_file="alteration.csv",
            observed_value={"row_count": 0},
            message="El archivo de alteration no contiene observaciones.",
        )

    return {"data": raw_data, "findings": findings}

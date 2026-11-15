"""Export agreed derived results without changing raw source data."""

from pathlib import Path

from src.mod1.loader import RawData


def export_results(
    positioned_data: RawData,
    processed_directory: Path,
    outputs_directory: Path,
) -> None:
    """Write derived data and deliverables using the team's agreed formats."""
    raise NotImplementedError(
        "Define the derived-data and deliverable formats before implementing export."
    )

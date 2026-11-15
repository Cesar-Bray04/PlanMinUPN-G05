"""Entry point for the approved desurvey module flow."""

from pathlib import Path

from src.mod1.desurvey import desurvey
from src.mod1.exporter import export_results
from src.mod1.loader import IntervalData, load_raw_data
from src.mod1.positioning import position_intervals
from src.mod1.validator import validate_data
from src.mod1.visualizer import visualize_results


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def main() -> None:
    """Orchestrate loading, validation, desurvey, positioning, and deliverables."""
    raw_data = load_raw_data(RAW_DATA_DIR)
    validated_data = validate_data(raw_data)
    trajectory = desurvey(validated_data["collar"], validated_data["survey"])
    intervals: IntervalData = {
        "assay": validated_data["assay"],
        "lithology": validated_data["lithology"],
        "alteration": validated_data["alteration"],
        "density": validated_data["density"],
    }
    positioned_data = position_intervals(trajectory, intervals)
    visualize_results(trajectory, positioned_data)
    export_results(positioned_data, PROCESSED_DATA_DIR, OUTPUTS_DIR)


if __name__ == "__main__":
    main()

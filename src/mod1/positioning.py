"""Position observed downhole intervals along calculated trajectories."""

from src.mod1.loader import IntervalData, RawData


def position_intervals(trajectory: object, intervals: IntervalData) -> RawData:
    """Associate assay, lithology, alteration, and density with the trajectory."""
    raise NotImplementedError(
        "Define and implement interval positioning against the desurveyed trajectory."
    )

"""Visualization entry point for desurvey and positioned interval results."""

from src.mod1.loader import RawData


def visualize_results(trajectory: object, positioned_data: RawData) -> None:
    """Visualize results using a format selected by the team."""
    raise NotImplementedError(
        "Select the visualization required for review before implementing this module."
    )

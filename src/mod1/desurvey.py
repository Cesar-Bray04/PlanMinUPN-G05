"""Desurvey drillhole orientation observations into spatial trajectories."""

from src.mod1.loader import RawData


def desurvey(collar: list[dict[str, str]], survey: list[dict[str, str]]) -> object:
    """Calculate drillhole trajectories using the method agreed by the team."""
    raise NotImplementedError(
        "Implement the team's agreed desurvey method before calculating trajectories."
    )

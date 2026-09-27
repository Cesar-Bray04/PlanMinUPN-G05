"""Validation entry point for the team's approved input-validation plan."""

from src.mod1.loader import RawData


def validate_data(raw_data: RawData) -> RawData:
    """Apply the agreed validation plan before calculations begin.

    The repository does not yet contain the validation criteria, so this module
    deliberately does not mark inputs as valid or introduce new checks.
    """
    raise NotImplementedError(
        "Implement the team's approved validation plan before running the workflow."
    )

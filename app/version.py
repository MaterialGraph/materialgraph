"""Resolve the MaterialGraph version from installed package metadata."""

from importlib import metadata


DISTRIBUTION_NAME = "materialgraph"
UNKNOWN_VERSION = "0+unknown"


def get_project_version() -> str:
    """Return the canonical installed version without another release constant."""
    try:
        return metadata.version(DISTRIBUTION_NAME)
    except metadata.PackageNotFoundError:
        return UNKNOWN_VERSION


PROJECT_VERSION = get_project_version()
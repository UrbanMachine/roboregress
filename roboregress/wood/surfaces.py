from enum import Enum


class Surface(Enum):
    """The 'wood' axis goes along the X."""

    TOP = "top"
    """The +Z wood surface"""

    RIGHT = "right"
    """The +Y wood surface"""

    LEFT = "left"
    """The -Y wood surface"""

    BOTTOM = "bottom"
    """The -Z wood surface"""


SURFACE_NORMALS: dict[Surface, tuple[float, float, float]] = {
    Surface.TOP: (0.0, 0.0, 1.0),
    Surface.BOTTOM: (0.0, 0.0, -1.0),
    Surface.LEFT: (0.0, 1.0, 0.0),
    Surface.RIGHT: (0.0, -1.0, 0.0),
}
"""Useful for visualizations"""

SURFACE_COLORS: dict[Surface, tuple[float, float, float]] = {
    Surface.TOP: (0.0, 0.0, 1.0),
    Surface.BOTTOM: (0.5, 0.5, 1.0),
    Surface.LEFT: (0.0, 1.0, 0.0),
    Surface.RIGHT: (0.5, 1.0, 0.5),
}

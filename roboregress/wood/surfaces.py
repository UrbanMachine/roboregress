from enum import Enum
from typing import Dict, Tuple


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


SURFACE_NORMALS: Dict[Surface, Tuple[float, float, float]] = {
    Surface.TOP: (0, 0, 1),
    Surface.BOTTOM: (0, 0, -1),
    Surface.LEFT: (0, 1, 0),
    Surface.RIGHT: (0, -1, 0),
}
"""Useful for visualizations"""

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
